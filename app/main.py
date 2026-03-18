from fastapi import FastAPI, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.custom_openapi import get_custom_openapi

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Documentation to use the Threat Intelligence API",
        version="1.0.0",
        openapi_url="/api/openapi.json",
    )

    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Register custom exception handlers (400, 500)
    register_exception_handlers(app)

    # Include routers (api endpoints)
    app.include_router(api_router)

    return app


app = create_app()

# Customize the OpenAPI schema to document validation errors as 400
app.openapi = get_custom_openapi(app)
