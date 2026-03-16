from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.indicators import IndicatorDetailResponse
from app.services.indicators import get_indicator_details
from app.db.session import get_db

router = APIRouter(tags=["indicators"])


@router.get("/{indicator_id}")
def get_indicator(
    indicator_id: str, db_session: Session = Depends(get_db)
) -> IndicatorDetailResponse:
    try:
        validated_indicator_id = str(UUID(indicator_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid indicator ID")

    indicator_details = get_indicator_details(validated_indicator_id, db_session)

    if indicator_details is None:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return indicator_details
