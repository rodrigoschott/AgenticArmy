"""
Pydantic response models for CrewAI workflows.

These models define the output schema for API responses,
ensuring consistent structure across all endpoints.
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowResponse(BaseModel):
    """Synchronous workflow execution response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow": "property_evaluation",
                "status": "completed",
                "result": {
                    "viability_score": 8.5,
                    "recommended_action": "Adquirir - potencial muito alto",
                    "key_insights": ["Localização privilegiada", "ROI estimado 22% a.a."],
                    "full_report": "..."
                },
                "execution_time": 872.3,
                "model_used": "qwen2.5:14b",
                "timestamp": "2025-01-31T14:30:00"
            }
        }
    )

    workflow: str = Field(..., description="Nome do workflow executado")
    status: str = Field("completed", description="Status da execução")
    result: Any = Field(..., description="Resultado do workflow")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
    model_used: str = Field(..., description="Modelo Ollama utilizado")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da execução")


class AsyncWorkflowResponse(BaseModel):
    """Asynchronous workflow execution response (immediate return)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "prop-eval-20250131-143000-abc123",
                "workflow": "property_evaluation",
                "status": "queued",
                "message": "Workflow iniciado em background",
                "status_url": "/workflows/prop-eval-20250131-143000-abc123/status",
                "webhook_url": "https://n8n.example.com/webhook/property-eval-complete",
                "estimated_duration": "10-20 minutes"
            }
        }
    )

    job_id: str = Field(..., description="ID único do job para rastreamento")
    workflow: str = Field(..., description="Nome do workflow")
    status: JobStatus = Field(JobStatus.QUEUED, description="Status inicial do job")
    message: str = Field(..., description="Mensagem informativa")
    status_url: str = Field(..., description="URL para consultar status do job")
    webhook_url: Optional[str] = Field(None, description="URL de webhook configurada")
    estimated_duration: str = Field(..., description="Duração estimada (ex: '10-20 minutes')")


class JobStatusResponse(BaseModel):
    """Job status check response."""

    job_id: str = Field(..., description="ID do job")
    workflow: str = Field(..., description="Nome do workflow")
    status: JobStatus = Field(..., description="Status atual")
    progress: Optional[int] = Field(None, description="Progresso em % (0-100)", ge=0, le=100)
    started_at: Optional[datetime] = Field(None, description="Timestamp de início")
    completed_at: Optional[datetime] = Field(None, description="Timestamp de conclusão")
    elapsed_time: Optional[float] = Field(None, description="Tempo decorrido em segundos")
    result: Optional[Any] = Field(None, description="Resultado (disponível quando status=completed)")
    error: Optional[str] = Field(None, description="Mensagem de erro (se status=failed)")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "job_id": "prop-eval-20250131-143000-abc123",
                "workflow": "property_evaluation",
                "status": "running",
                "progress": 65,
                "started_at": "2025-01-31T14:30:00",
                "completed_at": None,
                "elapsed_time": 567.2,
                "result": None,
                "error": None
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Status geral da API")
    version: str = Field("2.2", description="Versão do CrewAI Local")
    ollama_status: str = Field(..., description="Status da conexão com Ollama")
    ollama_url: str = Field(..., description="URL do Ollama configurada")
    docker_mcp_status: str = Field(..., description="Status do Docker MCP Gateway")
    available_models: int = Field(..., description="Número de modelos Ollama disponíveis")
    active_jobs: int = Field(0, description="Número de jobs em execução")
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.2",
                "ollama_status": "connected",
                "ollama_url": "http://localhost:11434",
                "docker_mcp_status": "available",
                "available_models": 11,
                "active_jobs": 2,
                "timestamp": "2025-01-31T14:30:00"
            }
        }
    )


class ModelInfo(BaseModel):
    """Ollama model information."""

    name: str = Field(..., description="Nome do modelo")
    display_name: str = Field(..., description="Nome formatado para exibição")
    size_gb: float = Field(..., description="Tamanho em GB")
    recommended: bool = Field(False, description="Se é um modelo recomendado")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "name": "qwen2.5:14b",
                "display_name": "qwen2.5:14b",
                "size_gb": 8.4,
                "recommended": True
            }
        }
    )


class ModelListResponse(BaseModel):
    """List of available Ollama models."""

    models: list[ModelInfo] = Field(..., description="Lista de modelos disponíveis")
    total: int = Field(..., description="Número total de modelos")
    recommended: list[str] = Field(..., description="Nomes dos modelos recomendados")
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "models": [
                    {"name": "qwen2.5:14b", "display_name": "qwen2.5:14b", "size_gb": 8.4, "recommended": True},
                    {"name": "llama3.2:latest", "display_name": "llama3.2:latest", "size_gb": 1.9, "recommended": True}
                ],
                "total": 11,
                "recommended": ["qwen2.5:14b", "glm-4.6:cloud", "llama3.2:latest"],
                "timestamp": "2025-01-31T14:30:00"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Tipo de erro")
    message: str = Field(..., description="Mensagem de erro detalhada")
    details: Optional[Any] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "price", "issue": "must be greater than 0"},
                "timestamp": "2025-01-31T14:30:00"
            }
        }
    )
