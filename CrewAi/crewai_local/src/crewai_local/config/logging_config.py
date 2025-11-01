"""
Logging configuration for CrewAI Local.

Provides rotating file handlers and console logging with proper formatting.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_MAX_SIZE_MB = 10
DEFAULT_LOG_BACKUP_COUNT = 5
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',   # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'     # Reset
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_size_mb: Optional[int] = None,
    backup_count: Optional[int] = None,
    console: bool = True,
    colored_console: bool = True
) -> logging.Logger:
    """
    Setup logging configuration with rotating file handler.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/crewai.log)
        max_size_mb: Maximum log file size in MB before rotation
        backup_count: Number of backup files to keep
        console: Whether to also log to console
        colored_console: Whether to use colored output for console

    Returns:
        Configured logger instance
    """
    # Get configuration from environment or use defaults
    log_level = log_level or os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
    max_size_mb = max_size_mb or int(os.getenv("LOG_MAX_SIZE_MB", str(DEFAULT_LOG_MAX_SIZE_MB)))
    backup_count = backup_count or int(os.getenv("LOG_BACKUP_COUNT", str(DEFAULT_LOG_BACKUP_COUNT)))

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
    else:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "crewai.log"

    # Ensure parent directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler with rotation
    max_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        if colored_console and sys.stdout.isatty():
            console_formatter = ColoredFormatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)
        else:
            console_formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # Log startup message
    root_logger.info("=" * 70)
    root_logger.info("CrewAI Local - Logging initialized")
    root_logger.info(f"Log level: {log_level}")
    root_logger.info(f"Log file: {log_path}")
    root_logger.info(f"Max file size: {max_size_mb}MB")
    root_logger.info(f"Backup count: {backup_count}")
    root_logger.info("=" * 70)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """
    Log exception with full traceback.

    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context about where/why the exception occurred
    """
    if context:
        logger.error(f"{context}: {type(exc).__name__}: {str(exc)}", exc_info=True)
    else:
        logger.error(f"{type(exc).__name__}: {str(exc)}", exc_info=True)


def log_mcp_tool_call(logger: logging.Logger, tool_name: str, **kwargs):
    """
    Log MCP tool call with parameters.

    Args:
        logger: Logger instance
        tool_name: Name of the MCP tool
        **kwargs: Tool parameters
    """
    params_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"MCP Tool Call: {tool_name}({params_str})")


def log_mcp_tool_result(logger: logging.Logger, tool_name: str, success: bool, result_preview: str = ""):
    """
    Log MCP tool result.

    Args:
        logger: Logger instance
        tool_name: Name of the MCP tool
        success: Whether the tool call succeeded
        result_preview: Preview of the result (first 100 chars)
    """
    status = "✓" if success else "✗"
    if result_preview:
        preview = result_preview[:100] + "..." if len(result_preview) > 100 else result_preview
        logger.debug(f"MCP Tool Result [{status}]: {tool_name} -> {preview}")
    else:
        logger.debug(f"MCP Tool Result [{status}]: {tool_name}")


# Example usage
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging(log_level="DEBUG")

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(logger, e, "Testing exception logging")

    # Test MCP tool logging
    log_mcp_tool_call(logger, "search", query="Paraty hotels")
    log_mcp_tool_result(logger, "search", True, "Found 10 results about hotels in Paraty")
