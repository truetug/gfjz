import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

from app.middleware import request_id_context

# To retrieve the request ID elsewhere in the application
def get_request_id() -> str:
    return request_id_context.get()

# Custom log filter to inject request ID into logs
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True

# Pydantic settings
class AppConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    log_format: Literal["json", "plain"] = "json"

settings = AppConfig()

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s"
        },
        "json": {
            "format": "{ \"time\": \"%(asctime)s\", \"logger\": \"%(name)s\", \"level\": \"%(levelname)s\", \"request_id\": \"%(request_id)s\", \"message\": \"%(message)s\" }",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": settings.log_format,
            "filters": ["request_id_filter"],
        },
    },
    "filters": {
        "request_id_filter": {
            "()": RequestIdFilter,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
