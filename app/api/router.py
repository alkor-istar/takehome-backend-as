from fastapi import APIRouter

from app.api.indicators import router as indicators_router

from app.api.campaigns import router as campaigns_router
from app.api.dashboard import router as dashboard_router


api_router = APIRouter(prefix="/api")

api_router.include_router(indicators_router, prefix="/indicators")
api_router.include_router(campaigns_router, prefix="/campaigns")
api_router.include_router(dashboard_router, prefix="/dashboard")


@api_router.get("/health")
def health() -> dict:
    return {"status": "ok"}
