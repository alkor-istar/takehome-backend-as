from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.indicators import (
    IndicatorDetailResponse,
    IndicatorSearchQuery,
    IndicatorSearchResponse,
)
from app.services.indicators import get_indicator_details, search_indicators
from app.db.session import get_db

router = APIRouter(tags=["indicators"])


@router.get("/{indicator_id:uuid}")
def get_indicator(
    indicator_id: UUID, db_session: Session = Depends(get_db)
) -> IndicatorDetailResponse:
    indicator_details = get_indicator_details(indicator_id, db_session)

    if indicator_details is None:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return indicator_details


@router.get("/search", response_model=IndicatorSearchResponse)
def search_indicators_endpoint(
    filters: IndicatorSearchQuery = Depends(IndicatorSearchQuery),
    db_session: Session = Depends(get_db),
) -> IndicatorSearchResponse:
    return search_indicators(filters, db_session)
