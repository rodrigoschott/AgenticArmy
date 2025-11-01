"""
Pytest Configuration and Shared Fixtures for CrewAI Local Tests.

This file provides:
- Shared fixtures for tests
- Test environment setup
- Cleanup handlers
- Custom markers
"""

import os
import sys
import pytest
import subprocess
from pathlib import Path
from typing import Generator, Dict, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# =============================================================================
# Session-Level Fixtures (run once per test session)
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(scope="session")
def docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture(scope="session")
def docker_mcp_available(docker_available: bool) -> bool:
    """Check if Docker MCP Gateway is available."""
    if not docker_available:
        return False

    try:
        result = subprocess.run(
            ["docker", "mcp", "tools", "list"],
            capture_output=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture(scope="session")
def ollama_available() -> bool:
    """Check if Ollama is available."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2):
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def google_maps_api_key() -> str | None:
    """Return Google Maps API key if configured."""
    return os.getenv("GOOGLE_MAPS_API_KEY")


# =============================================================================
# Function-Level Fixtures (run once per test function)
# =============================================================================

@pytest.fixture
def mock_env(monkeypatch) -> Generator[Dict[str, str], None, None]:
    """
    Provide a clean environment for testing.

    Usage:
        def test_something(mock_env):
            mock_env["MY_VAR"] = "value"
            # Test code here
    """
    env = {}

    def mock_getenv(key: str, default: str = None) -> str:
        return env.get(key, default)

    monkeypatch.setattr(os, "getenv", mock_getenv)
    yield env


@pytest.fixture
def temp_log_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary log file for testing."""
    log_file = tmp_path / "test.log"
    yield log_file
    # Cleanup
    if log_file.exists():
        log_file.unlink()


@pytest.fixture
def ollama_llm():
    """
    Create Ollama LLM instance for testing.

    Requires Ollama to be running.
    """
    pytest.importorskip("crewai")
    from crewai import LLM as CrewLLM

    # Use a small, fast model for testing
    return CrewLLM(
        model="ollama/qwen2.5:14b",
        base_url="http://localhost:11434"
    )


@pytest.fixture
def test_agent(ollama_llm):
    """
    Create a basic test agent.

    Requires Ollama to be running.
    """
    pytest.importorskip("crewai")
    from crewai import Agent

    return Agent(
        role="Test Agent",
        goal="Execute test tasks",
        backstory="A specialized agent for testing purposes",
        llm=ollama_llm,
        verbose=False
    )


@pytest.fixture
def mcp_tools_basic():
    """
    Get basic MCP tools for testing.

    Returns search, fetch, and wikipedia tools.
    """
    from src.crewai_local.tools.web_tools import (
        search_web,
        fetch_url,
        wikipedia_summary
    )

    return [search_web, fetch_url, wikipedia_summary]


@pytest.fixture
def mcp_tools_location():
    """
    Get location-based MCP tools for testing.

    Requires Google Maps API key.
    """
    from src.crewai_local.tools.web_tools import (
        maps_geocode,
        maps_search_places
    )

    return [maps_geocode, maps_search_places]


# =============================================================================
# Skip Conditions
# =============================================================================

requires_docker = pytest.mark.skipif(
    not subprocess.run(
        ["docker", "ps"],
        capture_output=True
    ).returncode == 0,
    reason="Docker is not available"
)

requires_ollama = pytest.mark.skipif(
    not os.getenv("SKIP_OLLAMA_CHECK") and
    subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/tags"],
        capture_output=True
    ).returncode != 0,
    reason="Ollama is not available"
)

requires_google_maps = pytest.mark.skipif(
    not os.getenv("GOOGLE_MAPS_API_KEY"),
    reason="Google Maps API key not configured"
)


# =============================================================================
# Custom Markers Application
# =============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Automatically add markers to tests based on their location.

    This runs after test collection and adds markers automatically.
    """
    for item in items:
        # Get test file path relative to tests directory
        test_file = Path(item.fspath).relative_to(Path(__file__).parent)

        # Add markers based on directory
        if "mcp" in test_file.parts:
            item.add_marker(pytest.mark.mcp)
            item.add_marker(pytest.mark.requires_docker)

        if "integration" in test_file.parts:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.requires_docker)
            item.add_marker(pytest.mark.requires_ollama)

        if "experimental" in test_file.parts:
            item.add_marker(pytest.mark.experimental)

        if "unit" in test_file.parts:
            item.add_marker(pytest.mark.unit)

        if "api" in test_file.parts:
            item.add_marker(pytest.mark.api)

        # Add markers for specific test files
        if "maps" in test_file.name:
            item.add_marker(pytest.mark.requires_api_key)

        if "airbnb" in test_file.name:
            item.add_marker(pytest.mark.slow)

        if "test_async" in test_file.name or "test_integration" in test_file.name:
            item.add_marker(pytest.mark.slow)


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """
    Configure pytest with custom settings.

    This runs before test collection.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "mcp: MCP tool integration tests"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests with agents"
    )
    config.addinivalue_line(
        "markers",
        "experimental: Experimental or research tests"
    )
    config.addinivalue_line(
        "markers",
        "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers",
        "slow: Tests that take more than 5 seconds"
    )
    config.addinivalue_line(
        "markers",
        "requires_ollama: Tests requiring Ollama"
    )
    config.addinivalue_line(
        "markers",
        "requires_docker: Tests requiring Docker MCP"
    )
    config.addinivalue_line(
        "markers",
        "requires_api_key: Tests requiring API keys"
    )
    config.addinivalue_line(
        "markers",
        "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers",
        "asyncio: Asynchronous tests"
    )


def pytest_report_header(config):
    """
    Add custom header to pytest output.

    Shows environment information.
    """
    headers = [
        "CrewAI Local Test Suite v2.2",
        f"Python: {sys.version.split()[0]}",
    ]

    # Check service availability
    try:
        import subprocess
        docker_status = "✅ Available" if subprocess.run(
            ["docker", "ps"],
            capture_output=True
        ).returncode == 0 else "❌ Not available"
        headers.append(f"Docker: {docker_status}")
    except Exception:
        headers.append("Docker: ❌ Not available")

    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1):
            ollama_status = "✅ Available"
    except Exception:
        ollama_status = "❌ Not available"
    headers.append(f"Ollama: {ollama_status}")

    google_maps_status = "✅ Configured" if os.getenv("GOOGLE_MAPS_API_KEY") else "❌ Not configured"
    headers.append(f"Google Maps API: {google_maps_status}")

    return headers


# =============================================================================
# Example Parametrized Fixtures
# =============================================================================

@pytest.fixture(params=["qwen2.5:14b", "mistral:7b"])
def ollama_model_name(request):
    """Parametrized fixture for testing multiple Ollama models."""
    return request.param


# =============================================================================
# Cleanup Hooks
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Cleanup logs after each test."""
    yield
    # Cleanup code runs after test
    log_dir = Path("logs")
    if log_dir.exists():
        for log_file in log_dir.glob("test_*.log"):
            try:
                log_file.unlink()
            except Exception:
                pass
