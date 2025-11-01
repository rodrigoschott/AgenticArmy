"""
Custom exceptions for CrewAI Local.

Provides specific exception types for better error handling and debugging.
"""


class CrewAILocalError(Exception):
    """Base exception for all CrewAI Local errors."""
    pass


class MCPError(CrewAILocalError):
    """Base exception for MCP-related errors."""
    pass


class MCPConnectionError(MCPError):
    """Raised when unable to connect to MCP server or Docker Gateway."""

    def __init__(self, message: str, server_name: str = None, original_error: Exception = None):
        self.server_name = server_name
        self.original_error = original_error
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.server_name:
            msg = f"[{self.server_name}] {msg}"
        if self.original_error:
            msg += f" (Original error: {str(self.original_error)})"
        return msg


class MCPToolExecutionError(MCPError):
    """Raised when MCP tool execution fails."""

    def __init__(self, message: str, tool_name: str = None, original_error: Exception = None):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.tool_name:
            msg = f"[{self.tool_name}] {msg}"
        if self.original_error:
            msg += f" (Original error: {str(self.original_error)})"
        return msg


class MCPTimeoutError(MCPError):
    """Raised when MCP operation times out."""

    def __init__(self, message: str, timeout_seconds: int = None):
        self.timeout_seconds = timeout_seconds
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.timeout_seconds:
            msg += f" (timeout: {self.timeout_seconds}s)"
        return msg


class MCPServerNotAvailableError(MCPError):
    """Raised when MCP server is not available or not initialized."""

    def __init__(self, message: str, server_name: str = None):
        self.server_name = server_name
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.server_name:
            msg = f"[{self.server_name}] {msg}"
        return msg


class DockerError(CrewAILocalError):
    """Base exception for Docker-related errors."""
    pass


class DockerNotAvailableError(DockerError):
    """Raised when Docker is not available or not running."""

    def __init__(self, message: str = "Docker is not available"):
        super().__init__(message)


class DockerMCPGatewayError(DockerError):
    """Raised when Docker MCP Gateway has issues."""

    def __init__(self, message: str):
        super().__init__(message)


class OllamaError(CrewAILocalError):
    """Base exception for Ollama-related errors."""
    pass


class OllamaNotAvailableError(OllamaError):
    """Raised when Ollama is not available."""

    def __init__(self, message: str, base_url: str = None):
        self.base_url = base_url
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.base_url:
            msg += f" (Base URL: {self.base_url})"
        return msg


class OllamaModelNotFoundError(OllamaError):
    """Raised when requested Ollama model is not found."""

    def __init__(self, message: str, model_name: str = None):
        self.model_name = model_name
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.model_name:
            msg += f" (Model: {self.model_name})"
        return msg


class ConfigurationError(CrewAILocalError):
    """Raised when there's a configuration error."""

    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.config_key:
            msg += f" (Config key: {self.config_key})"
        return msg


class EnvironmentError(CrewAILocalError):
    """Raised when there's an environment variable error."""

    def __init__(self, message: str, env_var: str = None):
        self.env_var = env_var
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.env_var:
            msg += f" (Environment variable: {self.env_var})"
        return msg


class ValidationError(CrewAILocalError):
    """Raised when validation fails."""
    pass


# Convenience functions for raising common errors

def raise_docker_not_available():
    """Raise DockerNotAvailableError with helpful message."""
    raise DockerNotAvailableError(
        "Docker Desktop is not running or not accessible.\n"
        "Please start Docker Desktop and ensure it's running properly.\n"
        "On Windows: Check system tray for Docker icon.\n"
        "To verify: Run 'docker ps' in terminal."
    )


def raise_mcp_gateway_not_available():
    """Raise DockerMCPGatewayError with helpful message."""
    raise DockerMCPGatewayError(
        "Docker MCP Gateway is not available.\n"
        "Please ensure:\n"
        "1. Docker Desktop is running\n"
        "2. MCP Toolkit is enabled in Docker settings\n"
        "3. Run 'docker mcp tools list' to verify\n"
    )


def raise_ollama_not_available(base_url: str):
    """Raise OllamaNotAvailableError with helpful message."""
    raise OllamaNotAvailableError(
        f"Ollama is not available at {base_url}.\n"
        "Please ensure:\n"
        "1. Ollama is installed\n"
        "2. Ollama server is running\n"
        "3. OLLAMA_BASE_URL environment variable is correct\n"
        "To verify: curl {base_url}/api/tags",
        base_url=base_url
    )


def raise_google_maps_key_not_configured():
    """Raise EnvironmentError for missing Google Maps API key."""
    raise EnvironmentError(
        "Google Maps API key is not configured.\n"
        "To use location-based tools (maps_geocode, maps_search_places), you need to:\n"
        "1. Get an API key from: https://console.cloud.google.com/apis/credentials\n"
        "2. Enable Maps JavaScript API, Places API, and Geocoding API\n"
        "3. Set GOOGLE_MAPS_API_KEY in your .env file\n"
        "Location-based tools will be disabled until configured.",
        env_var="GOOGLE_MAPS_API_KEY"
    )
