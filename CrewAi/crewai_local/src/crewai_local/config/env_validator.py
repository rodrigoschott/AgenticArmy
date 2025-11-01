"""
Environment Variable Validation for CrewAI Local.

Validates required environment variables and provides helpful error messages.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EnvVarConfig:
    """Configuration for an environment variable."""
    name: str
    required: bool
    description: str
    default: Optional[str] = None
    validator: Optional[callable] = None


class EnvironmentValidator:
    """Validates environment variables for CrewAI Local."""

    # Environment variable configurations
    ENV_CONFIGS = [
        EnvVarConfig(
            name="OLLAMA_BASE_URL",
            required=False,
            description="Ollama API base URL",
            default="http://localhost:11434"
        ),
        EnvVarConfig(
            name="GOOGLE_MAPS_API_KEY",
            required=False,
            description="Google Maps API key for location tools (maps_geocode, maps_search_places)"
        ),
        EnvVarConfig(
            name="DEFAULT_MODEL",
            required=False,
            description="Default Ollama model to use",
            default=None
        ),
        EnvVarConfig(
            name="LOG_LEVEL",
            required=False,
            description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            default="INFO"
        ),
    ]

    def __init__(self):
        self.validation_results: Dict[str, Tuple[bool, Optional[str]]] = {}
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def validate_all(self, show_warnings: bool = True) -> bool:
        """
        Validate all environment variables.

        Args:
            show_warnings: Whether to print warnings for missing optional variables

        Returns:
            True if all required variables are valid, False otherwise
        """
        all_valid = True

        for config in self.ENV_CONFIGS:
            value = os.getenv(config.name)

            # Check if required variable is missing
            if config.required and not value:
                self.errors.append(
                    f"❌ Required environment variable '{config.name}' is not set.\n"
                    f"   Description: {config.description}"
                )
                self.validation_results[config.name] = (False, "Missing required variable")
                all_valid = False
                continue

            # Use default if not set
            if not value and config.default:
                value = config.default
                os.environ[config.name] = value

            # Warn about optional variables if not set
            if not value and not config.required:
                if show_warnings:
                    self.warnings.append(
                        f"⚠️  Optional variable '{config.name}' is not set.\n"
                        f"   Description: {config.description}"
                    )
                self.validation_results[config.name] = (True, "Optional variable not set")
                continue

            # Run custom validator if provided
            if config.validator and value:
                try:
                    is_valid, error_msg = config.validator(value)
                    if not is_valid:
                        if config.required:
                            self.errors.append(
                                f"❌ Invalid value for '{config.name}': {error_msg}"
                            )
                            all_valid = False
                        else:
                            self.warnings.append(
                                f"⚠️  Invalid value for '{config.name}': {error_msg}"
                            )
                        self.validation_results[config.name] = (is_valid, error_msg)
                        continue
                except Exception as e:
                    error_msg = f"Validator error: {str(e)}"
                    self.errors.append(f"❌ Error validating '{config.name}': {error_msg}")
                    self.validation_results[config.name] = (False, error_msg)
                    all_valid = False
                    continue

            # Variable is valid
            self.validation_results[config.name] = (True, None)

        return all_valid

    def print_report(self):
        """Print validation report with errors and warnings."""
        print("\n" + "=" * 70)
        print("🔍 ENVIRONMENT VALIDATION REPORT")
        print("=" * 70)

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All environment variables are properly configured!")

        print("\n📋 CONFIGURED VARIABLES:")
        for config in self.ENV_CONFIGS:
            value = os.getenv(config.name)
            if value:
                # Mask sensitive values
                if "KEY" in config.name or "SECRET" in config.name or "PASSWORD" in config.name:
                    display_value = value[:8] + "..." if len(value) > 8 else "***"
                else:
                    display_value = value
                print(f"   ✓ {config.name}: {display_value}")
            else:
                status = "REQUIRED" if config.required else "optional"
                print(f"   ○ {config.name}: not set ({status})")

        print("=" * 70 + "\n")

    def check_google_maps_available(self) -> bool:
        """
        Check if Google Maps API key is configured.

        Returns:
            True if Google Maps API key is set, False otherwise
        """
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        return bool(api_key and len(api_key) > 10)

    def get_validation_summary(self) -> Dict[str, any]:
        """
        Get validation summary as a dictionary.

        Returns:
            Dictionary with validation summary
        """
        return {
            "all_valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "results": self.validation_results
        }


def validate_environment(show_report: bool = True, show_warnings: bool = True) -> bool:
    """
    Convenience function to validate environment variables.

    Args:
        show_report: Whether to print validation report
        show_warnings: Whether to show warnings for optional variables

    Returns:
        True if validation passed, False otherwise
    """
    validator = EnvironmentValidator()
    is_valid = validator.validate_all(show_warnings=show_warnings)

    if show_report:
        validator.print_report()

    return is_valid


def check_docker_mcp_available() -> Tuple[bool, str]:
    """
    Check if Docker MCP Gateway is available.

    Returns:
        Tuple of (is_available, message)
    """
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "mcp", "tools", "list"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            # Count available tools
            lines = result.stdout.strip().split('\n')
            tool_count = len([line for line in lines if line.strip() and not line.startswith('Available')])
            return (True, f"Docker MCP Gateway is active with {tool_count} tools available")
        else:
            error = result.stderr[:200] if result.stderr else "Unknown error"
            return (False, f"Docker MCP Gateway returned error: {error}")

    except FileNotFoundError:
        return (False, "Docker command not found. Is Docker Desktop installed?")
    except subprocess.TimeoutExpired:
        return (False, "Docker MCP Gateway did not respond within 5 seconds")
    except Exception as e:
        return (False, f"Error checking Docker MCP: {str(e)}")


# Example usage
if __name__ == "__main__":
    print("Testing environment validation...\n")
    validate_environment(show_report=True, show_warnings=True)

    print("\nTesting Docker MCP availability...")
    is_available, message = check_docker_mcp_available()
    status = "✅" if is_available else "❌"
    print(f"{status} {message}")
