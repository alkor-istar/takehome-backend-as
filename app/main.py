from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models.indicators import IndicatorModel
from app.schemas.indicators import Indicator
from app.api.router import api_router
import app.db.models


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(api_router)

    return app


app = create_app()
