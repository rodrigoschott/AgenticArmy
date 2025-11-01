"""
API Models for CrewAI Local n8n Integration.
"""

from .requests import (
    PropertyEvaluationRequest,
    PositioningStrategyRequest,
    OpeningPreparationRequest,
    Planning30DaysRequest,
    WorkflowRequest,
)

from .responses import (
    WorkflowResponse,
    AsyncWorkflowResponse,
    JobStatusResponse,
    HealthResponse,
    ModelListResponse,
    ModelInfo,
    JobStatus,
    ErrorResponse,
)

__all__ = [
    # Requests
    "PropertyEvaluationRequest",
    "PositioningStrategyRequest",
    "OpeningPreparationRequest",
    "Planning30DaysRequest",
    "WorkflowRequest",
    # Responses
    "WorkflowResponse",
    "AsyncWorkflowResponse",
    "JobStatusResponse",
    "HealthResponse",
    "ModelListResponse",
    "ModelInfo",
    "JobStatus",
    "ErrorResponse",
]
