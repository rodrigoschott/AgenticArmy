"""
Configuration for CrewAI Local API Server.

Manages API settings, environment variables, and constants.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIConfig:
    """API configuration settings."""

    # Server settings
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"

    # CORS settings
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5678,http://localhost:3000"
    ).split(",")

    # Webhook settings
    WEBHOOK_TIMEOUT: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    WEBHOOK_RETRY_COUNT: int = int(os.getenv("WEBHOOK_RETRY_COUNT", "3"))

    # Job settings
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))
    JOB_TIMEOUT: int = int(os.getenv("JOB_TIMEOUT", "10800"))  # 3 hours

    # Ollama settings (inherited from main config)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL: Optional[str] = os.getenv("DEFAULT_MODEL")

    # Docker MCP settings
    DOCKER_MCP_ENABLED: bool = os.getenv("DOCKER_MCP_ENABLED", "true").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Project info
    PROJECT_NAME: str = "CrewAI Local API"
    VERSION: str = "2.2"
    DESCRIPTION: str = """
    API REST para integração CrewAI Local com n8n e outros sistemas.

    ## Workflows Disponíveis

    - **Property Evaluation**: Análise completa de viabilidade de propriedade
    - **Positioning Strategy**: Estratégia de posicionamento de mercado
    - **Opening Preparation**: Planejamento de inauguração
    - **30-Day Planning**: Plano de ação detalhado para 30 dias

    ## Modos de Execução

    - **Sync**: Resposta síncrona (aguarda conclusão)
    - **Async**: Execução em background com webhook callback

    ## Autenticação

    Atualmente sem autenticação (ambiente local).
    Para produção, configure API_KEY no .env
    """

    # API Key (optional, for production)
    API_KEY: Optional[str] = os.getenv("API_KEY")

    # Storage paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    LOGS_DIR: Path = BASE_DIR / "logs"
    RESULTS_DIR: Path = BASE_DIR / "api_results"

    # Workflow duration estimates (in seconds)
    WORKFLOW_DURATIONS = {
        "property_evaluation": {"min": 600, "max": 1200, "label": "10-20 minutes"},
        "positioning_strategy": {"min": 480, "max": 900, "label": "8-15 minutes"},
        "opening_preparation": {"min": 600, "max": 1080, "label": "10-18 minutes"},
        "planning_30days": {"min": 7200, "max": 10800, "label": "2-3 hours"},
    }

    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True

)

    @classmethod
    def get_workflow_duration(cls, workflow: str) -> dict:
        """Get duration estimate for a workflow."""
        return cls.WORKFLOW_DURATIONS.get(workflow, {"min": 600, "max": 1800, "label": "10-30 minutes"})


# Initialize directories on import
APIConfig.ensure_directories()
