"""Logging configuration for Agency Toolkit."""

import logging
import logging.handlers
from pathlib import Path

logger = logging.getLogger("agency_toolkit")


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
) -> None:
    """Configure logging with console and optional file handlers.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    log_level = getattr(logging, level.upper())

    # Set root logger level to propagate all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Set agency_toolkit logger level
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=3,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
