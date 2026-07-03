"""
FastAPI REST API for Waste Volume Prediction System.

Run with: uvicorn api.main:app --reload
"""
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import configure_logging, load_settings
from api.dependencies import load_predictor_state
from api.rate_limit import InMemoryRateLimiter
from api.routes import iot, model, predictions, root, stats


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = load_settings()
    configure_logging(settings.log_level)
    predictor_state = load_predictor_state()
    rate_limiter = InMemoryRateLimiter(
        per_minute=settings.rate_limit_per_minute,
        exempt_paths=settings.rate_limit_exempt_paths,
    )

    api = FastAPI(
        title="Waste Volume Prediction API",
        description="REST API for predicting waste volume using Machine Learning",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    api.state.settings = settings
    api.state.predictor_state = predictor_state
    api.state.rate_limiter = rate_limiter

    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.middleware("http")
    async def rate_limit_requests(request: Request, call_next):
        """Apply per-client rate limiting before route handling."""
        if not rate_limiter.is_allowed(request):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry later."},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)

    api.include_router(root.create_router(predictor_state))
    api.include_router(stats.router)
    api.include_router(model.router)
    api.include_router(iot.create_router(settings))
    api.include_router(predictions.create_router(predictor_state))
    return api


app = create_app()

# Compatibility aliases for scripts/tests that imported these from api.main.
settings = app.state.settings
predictor_state = app.state.predictor_state
rate_limiter = app.state.rate_limiter
predictor = predictor_state.predictor
PREDICTOR_LOADED = predictor_state.loaded
PREDICTOR_ERROR = predictor_state.error
IOT_API_KEY = settings.iot_api_key
RATE_LIMIT_PER_MINUTE = settings.rate_limit_per_minute
_rate_limit_window = rate_limiter._window


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
