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


@router.get(
    "/search",
    response_model=IndicatorSearchResponse,
    description="Search and filter indicators based on various criteria.",
    responses={
        200: {
            "description": "Indicators matching the search criteria.",
            "model": IndicatorSearchResponse,
        },
        404: {
            "description": "No indicators found.",
        },
    },
)
def search_indicators_endpoint(
    filters: IndicatorSearchQuery = Depends(IndicatorSearchQuery),
    db_session: Session = Depends(get_db),
) -> IndicatorSearchResponse:
    found_indicators = search_indicators(filters, db_session)
    if found_indicators is None:
        raise HTTPException(status_code=404, detail="No indicators found")
    return found_indicators


@router.get(
    "/{indicator_id:uuid}",
    summary="Get indicator details by ID",
    description="Retrieve detailed information about a specific indicator.",
    response_model=IndicatorDetailResponse,
    responses={
        200: {
            "description": "Detailed information about the indicator.",
            "model": IndicatorDetailResponse,
        },
        404: {
            "description": "The indicator with the given ID was not present in the database.",
        },
    },
)
def get_indicator(
    indicator_id: UUID, db_session: Session = Depends(get_db)
) -> IndicatorDetailResponse:
    indicator_details = get_indicator_details(indicator_id, db_session)

    if indicator_details is None:
        raise HTTPException(status_code=404, detail="Indicator not found")

    return indicator_details
