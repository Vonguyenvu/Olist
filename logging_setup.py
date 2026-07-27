import logging
from logging.config import dictConfig
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def setup_logging(log_file: str | None = None) -> logging.Logger:
    """Configure console and rotating file logging for ETL runs."""
    log_file = log_file or str(PROJECT_ROOT / "logs" / "etl.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(module)s | %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": log_file,
                "encoding": "utf-8",
                "maxBytes": 10_485_760,
                "backupCount": 5,
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    })

    return logging.getLogger(__name__)