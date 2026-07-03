"""Configuration helpers for the FastAPI application."""
import logging
import os
from dataclasses import dataclass
from typing import List, Set


DEFAULT_ORIGINS = (
    "http://localhost:8501,http://127.0.0.1:8501,"
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:4173,http://127.0.0.1:4173"
)
DEFAULT_RATE_LIMIT_EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


@dataclass(frozen=True)
class Settings:
    log_level: str
    iot_api_key: str
    rate_limit_per_minute: int
    rate_limit_exempt_paths: Set[str]
    allowed_origins: List[str]
    allow_credentials: bool


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def load_settings() -> Settings:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    raw_origins = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    return Settings(
        log_level=log_level,
        iot_api_key=os.getenv("IOT_API_KEY", "").strip(),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "120")),
        rate_limit_exempt_paths=DEFAULT_RATE_LIMIT_EXEMPT_PATHS,
        allowed_origins=allowed_origins,
        allow_credentials="*" not in allowed_origins,
    )
