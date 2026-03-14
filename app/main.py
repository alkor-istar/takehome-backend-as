from fastapi import FastAPI
from app.core.config import settings
from app.db.session import get_db
from app.db.models.indicators import IndicatorModel
from app.schemas.indicators import Indicator
from sqlalchemy.orm import Session
from fastapi import Depends


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/indicators", response_model=list[Indicator])
    def get_indicators(db: Session = Depends(get_db)) -> dict:
        response = db.query(IndicatorModel).all()
        return response

    return app


app = create_app()
