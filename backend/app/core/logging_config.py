import logging.config
import sys
from typing import Any, Dict

# Centralized logging configuration dictionary
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "production",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "app": {  # Application specific logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging() -> None:
    """
    Initialize the centralized logging configuration.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
