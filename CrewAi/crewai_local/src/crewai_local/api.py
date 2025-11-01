"""
FastAPI Application for CrewAI Local n8n Integration.

Provides REST API endpoints for executing CrewAI workflows with both
synchronous and asynchronous execution modes.

Usage:
    uvicorn crewai_local.api:app --host 0.0.0.0 --port 8000 --reload

API Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json
"""

import uuid
import asyncio
import time
import httpx
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api_config import APIConfig
from .models import (
    PropertyEvaluationRequest,
    PositioningStrategyRequest,
    OpeningPreparationRequest,
    Planning30DaysRequest,
    WorkflowResponse,
    AsyncWorkflowResponse,
    JobStatusResponse,
    HealthResponse,
    ModelListResponse,
    ModelInfo,
    JobStatus,
    ErrorResponse,
)
from .background_jobs import JobManager


# Global job manager
job_manager = JobManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    print(f">> Starting {APIConfig.PROJECT_NAME} v{APIConfig.VERSION}")
    print(f">> Ollama: {APIConfig.OLLAMA_BASE_URL}")
    print(f">> Max concurrent jobs: {APIConfig.MAX_CONCURRENT_JOBS}")

    # Ensure directories exist
    APIConfig.ensure_directories()

    yield

    # Shutdown
    print(">> Shutting down API server")
    job_manager.cancel_all_jobs()


# Create FastAPI app
app = FastAPI(
    title=APIConfig.PROJECT_NAME,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message=str(exc),
            details={"type": type(exc).__name__}
        ).model_dump(mode="json")
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def send_webhook(url: str, data: dict, retries: int = 3):
    """Send webhook callback with retry logic."""
    async with httpx.AsyncClient(timeout=APIConfig.WEBHOOK_TIMEOUT) as client:
        for attempt in range(retries):
            try:
                response = await client.post(url, json=data)
                if response.status_code < 400:
                    print(f"✅ Webhook sent successfully to {url}")
                    return
                print(f"⚠️  Webhook returned {response.status_code}, retrying...")
            except Exception as e:
                print(f"❌ Webhook error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff


def generate_job_id(workflow: str) -> str:
    """Generate unique job ID."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{workflow}-{timestamp}-{short_uuid}"


# ============================================================================
# WORKFLOW EXECUTION FUNCTIONS
# ============================================================================

async def execute_property_evaluation(data: PropertyEvaluationRequest) -> dict:
    """Execute property evaluation workflow."""
    from .crew_paraty import run_property_evaluation, _initialize_llm

    # Initialize LLM with optional model override
    llm = _initialize_llm(interactive=False, model_name=data.model_name)

    # Prepare property data
    property_data = {
        'name': data.name,
        'location': data.location,
        'price': data.price,
        'rooms': data.rooms,
        'capex_estimated': data.capex_estimated,
        'adr_target': data.adr_target,
        'occupancy_target': data.occupancy_target,
    }

    # Execute workflow
    result = await asyncio.to_thread(run_property_evaluation, llm, property_data)

    return {
        "workflow": "property_evaluation",
        "result": result,
        "model_used": llm.model if hasattr(llm, 'model') else "unknown",
    }


async def execute_positioning_strategy(data: PositioningStrategyRequest) -> dict:
    """Execute positioning strategy workflow."""
    from .crew_paraty import run_positioning_strategy, _initialize_llm

    llm = _initialize_llm(interactive=False, model_name=data.model_name)

    strategy_data = {
        'name': data.name,
        'location': data.location,
        'target_audience': data.target_audience,
        'differentiators': data.differentiators,
        'budget_marketing': data.budget_marketing,
    }

    result = await asyncio.to_thread(run_positioning_strategy, llm, strategy_data)

    return {
        "workflow": "positioning_strategy",
        "result": result,
        "model_used": llm.model if hasattr(llm, 'model') else "unknown",
    }


async def execute_opening_preparation(data: OpeningPreparationRequest) -> dict:
    """Execute opening preparation workflow."""
    from .crew_paraty import run_opening_preparation, _initialize_llm

    llm = _initialize_llm(interactive=False, model_name=data.model_name)

    opening_data = {
        'name': data.name,
        'location': data.location,
        'opening_date': data.opening_date,
        'total_staff_needed': data.total_staff_needed,
        'budget_setup': data.budget_setup,
        'priority_areas': data.priority_areas,
    }

    result = await asyncio.to_thread(run_opening_preparation, llm, opening_data)

    return {
        "workflow": "opening_preparation",
        "result": result,
        "model_used": llm.model if hasattr(llm, 'model') else "unknown",
    }


async def execute_planning_30days(data: Planning30DaysRequest) -> dict:
    """Execute 30-day planning workflow."""
    from .crew_paraty import run_planning_30days, _initialize_llm

    llm = _initialize_llm(interactive=False, model_name=data.model_name)

    planning_data = {
        'name': data.name,
        'location': data.location,
        'start_date': data.start_date,
        'focus_areas': data.focus_areas,
        'current_status': data.current_status,
        'key_goals': data.key_goals,
    }

    result = await asyncio.to_thread(run_planning_30days, llm, planning_data)

    return {
        "workflow": "planning_30days",
        "result": result,
        "model_used": llm.model if hasattr(llm, 'model') else "unknown",
    }


# Mapping workflow names to execution functions
WORKFLOW_EXECUTORS = {
    "property_evaluation": execute_property_evaluation,
    "positioning_strategy": execute_positioning_strategy,
    "opening_preparation": execute_opening_preparation,
    "planning_30days": execute_planning_30days,
}


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": APIConfig.PROJECT_NAME,
        "version": APIConfig.VERSION,
        "docs": "/docs",
        "health": "/health",
        "workflows": list(WORKFLOW_EXECUTORS.keys()),
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Health check endpoint."""
    from .crew_paraty import _ollama_available, _get_available_models

    # Check Ollama
    ollama_connected = _ollama_available(APIConfig.OLLAMA_BASE_URL)
    ollama_status = "connected" if ollama_connected else "disconnected"

    # Get available models
    models = _get_available_models(APIConfig.OLLAMA_BASE_URL) if ollama_connected else []

    # Check Docker MCP
    from .tools.mcp_tools_new import check_docker_mcp_available
    docker_available, _ = check_docker_mcp_available()
    docker_status = "available" if docker_available else "unavailable"

    return HealthResponse(
        status="healthy" if ollama_connected else "degraded",
        version=APIConfig.VERSION,
        ollama_status=ollama_status,
        ollama_url=APIConfig.OLLAMA_BASE_URL,
        docker_mcp_status=docker_status,
        available_models=len(models),
        active_jobs=job_manager.get_active_count(),
    )


@app.get("/models", response_model=ModelListResponse, tags=["Info"])
async def list_models():
    """List available Ollama models."""
    from .crew_paraty import _get_available_models

    try:
        models_data = _get_available_models(APIConfig.OLLAMA_BASE_URL)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to fetch models from Ollama: {str(e)}"
        )

    recommended = ["qwen2.5:14b", "glm-4.6:cloud", "llama3.2:latest", "gpt-oss:latest", "deepseek-coder:33b"]

    models = [
        ModelInfo(
            name=m['name'],
            display_name=m['display_name'],
            size_gb=m['size_gb'],
            recommended=m['name'] in recommended
        )
        for m in models_data
    ]

    return ModelListResponse(
        models=models,
        total=len(models),
        recommended=recommended,
    )


# ============================================================================
# SYNCHRONOUS WORKFLOW ENDPOINTS
# ============================================================================

@app.post("/workflows/property-evaluation", response_model=WorkflowResponse, tags=["Workflows - Sync"])
async def property_evaluation_sync(request: PropertyEvaluationRequest):
    """
    Execute property evaluation workflow (synchronous).

    **Duration:** 10-20 minutes

    **Agents:** 5 (Viability, Positioning, Financial, Risk, ROI)
    """
    try:
        start_time = time.time()

        executor = WORKFLOW_EXECUTORS["property_evaluation"]
        workflow_result = await executor(request)

        execution_time = time.time() - start_time

        return WorkflowResponse(
            workflow=workflow_result["workflow"],
            result=workflow_result["result"],
            execution_time=execution_time,
            model_used=workflow_result["model_used"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.post("/workflows/positioning-strategy", response_model=WorkflowResponse, tags=["Workflows - Sync"])
async def positioning_strategy_sync(request: PositioningStrategyRequest):
    """
    Execute positioning strategy workflow (synchronous).

    **Duration:** 8-15 minutes

    **Agents:** 4 (Market Research, Target Definition, Pricing, Positioning)
    """
    try:
        start_time = time.time()

        executor = WORKFLOW_EXECUTORS["positioning_strategy"]
        workflow_result = await executor(request)

        execution_time = time.time() - start_time

        return WorkflowResponse(
            workflow=workflow_result["workflow"],
            result=workflow_result["result"],
            execution_time=execution_time,
            model_used=workflow_result["model_used"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.post("/workflows/opening-preparation", response_model=WorkflowResponse, tags=["Workflows - Sync"])
async def opening_preparation_sync(request: OpeningPreparationRequest):
    """
    Execute opening preparation workflow (synchronous).

    **Duration:** 10-18 minutes

    **Agents:** 4 (Operations, HR, Suppliers, Launch)
    """
    try:
        start_time = time.time()

        executor = WORKFLOW_EXECUTORS["opening_preparation"]
        workflow_result = await executor(request)

        execution_time = time.time() - start_time

        return WorkflowResponse(
            workflow=workflow_result["workflow"],
            result=workflow_result["result"],
            execution_time=execution_time,
            model_used=workflow_result["model_used"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@app.post("/workflows/planning-30days", response_model=WorkflowResponse, tags=["Workflows - Sync"])
async def planning_30days_sync(request: Planning30DaysRequest):
    """
    Execute 30-day planning workflow (synchronous).

    **Duration:** 2-3 hours ⚠️

    **Agents:** 4 (Operations, Marketing, Quality, Finance)

    **Note:** Due to long duration, consider using async endpoint instead.
    """
    try:
        start_time = time.time()

        executor = WORKFLOW_EXECUTORS["planning_30days"]
        workflow_result = await executor(request)

        execution_time = time.time() - start_time

        return WorkflowResponse(
            workflow=workflow_result["workflow"],
            result=workflow_result["result"],
            execution_time=execution_time,
            model_used=workflow_result["model_used"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


# ============================================================================
# ASYNCHRONOUS WORKFLOW ENDPOINTS
# ============================================================================

@app.post("/workflows/property-evaluation/async", response_model=AsyncWorkflowResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Workflows - Async"])
async def property_evaluation_async(request: PropertyEvaluationRequest, background_tasks: BackgroundTasks):
    """
    Execute property evaluation workflow (asynchronous).

    Returns immediately with job_id for status tracking.
    Optional webhook callback when complete.
    """
    job_id = generate_job_id("property_evaluation")
    workflow_name = "property_evaluation"

    # Create job
    job_manager.create_job(job_id, workflow_name, request.model_dump(mode="json"))

    # Add background task
    background_tasks.add_task(
        job_manager.execute_job,
        job_id,
        WORKFLOW_EXECUTORS[workflow_name],
        request,
        request.webhook_url
    )

    duration = APIConfig.get_workflow_duration(workflow_name)

    return AsyncWorkflowResponse(
        job_id=job_id,
        workflow=workflow_name,
        message="Workflow started in background",
        status_url=f"/workflows/{job_id}/status",
        webhook_url=request.webhook_url,
        estimated_duration=duration["label"],
    )


@app.post("/workflows/positioning-strategy/async", response_model=AsyncWorkflowResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Workflows - Async"])
async def positioning_strategy_async(request: PositioningStrategyRequest, background_tasks: BackgroundTasks):
    """Execute positioning strategy workflow (asynchronous)."""
    job_id = generate_job_id("positioning_strategy")
    workflow_name = "positioning_strategy"

    job_manager.create_job(job_id, workflow_name, request.model_dump(mode="json"))

    background_tasks.add_task(
        job_manager.execute_job,
        job_id,
        WORKFLOW_EXECUTORS[workflow_name],
        request,
        request.webhook_url
    )

    duration = APIConfig.get_workflow_duration(workflow_name)

    return AsyncWorkflowResponse(
        job_id=job_id,
        workflow=workflow_name,
        message="Workflow started in background",
        status_url=f"/workflows/{job_id}/status",
        webhook_url=request.webhook_url,
        estimated_duration=duration["label"],
    )


@app.post("/workflows/opening-preparation/async", response_model=AsyncWorkflowResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Workflows - Async"])
async def opening_preparation_async(request: OpeningPreparationRequest, background_tasks: BackgroundTasks):
    """Execute opening preparation workflow (asynchronous)."""
    job_id = generate_job_id("opening_preparation")
    workflow_name = "opening_preparation"

    job_manager.create_job(job_id, workflow_name, request.model_dump(mode="json"))

    background_tasks.add_task(
        job_manager.execute_job,
        job_id,
        WORKFLOW_EXECUTORS[workflow_name],
        request,
        request.webhook_url
    )

    duration = APIConfig.get_workflow_duration(workflow_name)

    return AsyncWorkflowResponse(
        job_id=job_id,
        workflow=workflow_name,
        message="Workflow started in background",
        status_url=f"/workflows/{job_id}/status",
        webhook_url=request.webhook_url,
        estimated_duration=duration["label"],
    )


@app.post("/workflows/planning-30days/async", response_model=AsyncWorkflowResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Workflows - Async"])
async def planning_30days_async(request: Planning30DaysRequest, background_tasks: BackgroundTasks):
    """Execute 30-day planning workflow (asynchronous) - Recommended for this long workflow."""
    job_id = generate_job_id("planning_30days")
    workflow_name = "planning_30days"

    job_manager.create_job(job_id, workflow_name, request.model_dump(mode="json"))

    background_tasks.add_task(
        job_manager.execute_job,
        job_id,
        WORKFLOW_EXECUTORS[workflow_name],
        request,
        request.webhook_url
    )

    duration = APIConfig.get_workflow_duration(workflow_name)

    return AsyncWorkflowResponse(
        job_id=job_id,
        workflow=workflow_name,
        message="Workflow started in background",
        status_url=f"/workflows/{job_id}/status",
        webhook_url=request.webhook_url,
        estimated_duration=duration["label"],
    )


# ============================================================================
# JOB STATUS ENDPOINTS
# ============================================================================

@app.get("/workflows/{job_id}/status", response_model=JobStatusResponse, tags=["Job Management"])
async def get_job_status(job_id: str):
    """Get status of an async job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return job_manager.get_job_status(job_id)


@app.delete("/workflows/{job_id}", tags=["Job Management"])
async def cancel_job(job_id: str):
    """Cancel a running job."""
    success = job_manager.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found or already completed"
        )

    return {"message": f"Job {job_id} cancelled", "job_id": job_id}


@app.get("/workflows/jobs/active", tags=["Job Management"])
async def list_active_jobs():
    """List all active (running or queued) jobs."""
    return {
        "active_jobs": job_manager.get_active_jobs(),
        "count": job_manager.get_active_count(),
    }


# ============================================================================
# ENTRY POINT
# ============================================================================


def run_dev():
    """Start the API server in development mode with auto-reload."""
    import uvicorn

    print(f">> Starting {APIConfig.PROJECT_NAME} v{APIConfig.VERSION} [DEV MODE]")
    print(f">> Server: http://{APIConfig.HOST}:{APIConfig.PORT}")
    print(f">> Docs: http://{APIConfig.HOST}:{APIConfig.PORT}/docs")
    print(f">> Auto-reload: ENABLED")

    uvicorn.run(
        "crewai_local.api:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=True,
    )


def run_prod():
    """Start the API server in production mode with multiple workers."""
    import uvicorn

    print(f">> Starting {APIConfig.PROJECT_NAME} v{APIConfig.VERSION} [PRODUCTION]")
    print(f">> Server: http://{APIConfig.HOST}:{APIConfig.PORT}")
    print(f">> Docs: http://{APIConfig.HOST}:{APIConfig.PORT}/docs")
    print(f">> Workers: 4")

    uvicorn.run(
        "crewai_local.api:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        workers=4,
    )


if __name__ == "__main__":
    import uvicorn

    print(f">> Starting {APIConfig.PROJECT_NAME} v{APIConfig.VERSION}")
    print(f">> Server: http://{APIConfig.HOST}:{APIConfig.PORT}")
    print(f">> Docs: http://{APIConfig.HOST}:{APIConfig.PORT}/docs")

    uvicorn.run(
        "crewai_local.api:app",
        host=APIConfig.HOST,
        port=APIConfig.PORT,
        reload=APIConfig.RELOAD,
    )
