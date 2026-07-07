"""Centralized logging configuration for PlacementPrep AI."""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "placementprep") -> logging.Logger:
    """Create and configure a logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # File handler
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "placementprep.log")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
