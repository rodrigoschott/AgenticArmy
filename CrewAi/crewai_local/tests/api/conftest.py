"""Pytest fixtures for API tests."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

from crewai_local.api import app, job_manager
from crewai_local.models import (
    PropertyEvaluationRequest,
    PositioningStrategyRequest,
    OpeningPreparationRequest,
    Planning30DaysRequest,
)


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_ollama_available():
    """Mock Ollama availability check to return True."""
    with patch("crewai_local.crew_paraty._ollama_available", return_value=True):
        yield


@pytest.fixture
def mock_ollama_unavailable():
    """Mock Ollama availability check to return False."""
    with patch("crewai_local.crew_paraty._ollama_available", return_value=False):
        yield


@pytest.fixture
def mock_ollama_models():
    """Mock Ollama models list."""
    return {
        "models": [
            {
                "name": "qwen2.5:14b",
                "modified_at": "2025-01-15T10:00:00Z",
                "size": 8300000000,
            },
            {
                "name": "llama3.3:70b",
                "modified_at": "2025-01-10T12:00:00Z",
                "size": 39000000000,
            },
            {
                "name": "mistral:7b",
                "modified_at": "2025-01-05T08:00:00Z",
                "size": 4100000000,
            },
        ]
    }


@pytest.fixture
def mock_workflow_execution():
    """Mock successful workflow execution."""
    async def mock_run(*args, **kwargs):
        return {
            "result": "Workflow completed successfully",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
        }

    with patch("crewai_local.crew_paraty.run_property_evaluation", return_value=mock_run()):
        with patch("crewai_local.crew_paraty.run_positioning_strategy", return_value=mock_run()):
            with patch("crewai_local.crew_paraty.run_opening_preparation", return_value=mock_run()):
                with patch("crewai_local.crew_paraty.run_planning_30days", return_value=mock_run()):
                    yield


@pytest.fixture
def sample_property_evaluation_request():
    """Sample PropertyEvaluationRequest for testing."""
    return {
        "name": "Hotel Teste",
        "location": "Paraty, RJ",
        "price": 1500000.0,
        "rooms": 10,
        "capex_estimated": 300000.0,
        "adr_target": 450.0,
        "occupancy_target": 75.0,
    }


@pytest.fixture
def sample_positioning_strategy_request():
    """Sample PositioningStrategyRequest for testing."""
    return {
        "name": "Pousada Boutique",
        "location": "Paraty Centro Histórico",
        "target_audience": "Casais românticos 35-55 anos, alta renda",
        "differentiators": ["Arquitetura colonial preservada", "Experiências locais autênticas"],
        "budget_marketing": 50000.0,
    }


@pytest.fixture
def sample_opening_preparation_request():
    """Sample OpeningPreparationRequest for testing."""
    return {
        "name": "Casa Colonial",
        "location": "Paraty, RJ",
        "opening_date": "2025-12-01",
        "total_staff_needed": 15,
        "budget_setup": 200000.0,
        "priority_areas": ["Recepção", "Restaurante", "Housekeeping"],
    }


@pytest.fixture
def sample_planning_30days_request():
    """Sample Planning30DaysRequest for testing."""
    return {
        "name": "Paraty Dream",
        "location": "Paraty, RJ",
        "start_date": "2025-02-01",
        "focus_areas": ["Marketing digital", "Otimização operacional", "Treinamento equipe"],
        "current_status": "Operando há 6 meses, 60% ocupação",
        "key_goals": ["Aumentar ocupação para 80%", "Melhorar avaliações", "Reduzir custos"],
    }


@pytest.fixture
def clear_jobs():
    """Clear all jobs before and after tests."""
    job_manager.cancel_all_jobs()
    yield
    job_manager.cancel_all_jobs()


@pytest.fixture
def mock_webhook_success():
    """Mock successful webhook delivery."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock:
        yield mock


@pytest.fixture
def mock_webhook_failure():
    """Mock failed webhook delivery."""
    with patch("httpx.AsyncClient.post", side_effect=Exception("Webhook delivery failed")):
        yield


@pytest.fixture
def mock_docker_mcp_available():
    """Mock Docker MCP tools availability check."""
    with patch("crewai_local.api.check_docker_mcp_available", return_value=True):
        yield


@pytest.fixture
def mock_docker_mcp_unavailable():
    """Mock Docker MCP tools unavailability check."""
    with patch("crewai_local.api.check_docker_mcp_available", return_value=False):
        yield
