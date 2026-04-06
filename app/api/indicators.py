from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas import (
    IndicatorDetailResponse,
    IndicatorSearchQuery,
    IndicatorSearchResponse,
)
from app.services import get_indicator_details, search_indicators
from app.db.session import get_db
from .utils import generate_etag

router = APIRouter(tags=["indicators"])


@router.get(
    "/search",
    response_model=IndicatorSearchResponse,
    description="Search and filter indicators based on various criteria.",
    responses={
        200: {
            "description": "Indicators matching the search criteria.",
            "model": IndicatorSearchResponse,
        }
    },
)
def search_indicators_endpoint(
    filters: IndicatorSearchQuery = Depends(IndicatorSearchQuery),
    db_session: Session = Depends(get_db),
) -> IndicatorSearchResponse:
    return search_indicators(filters, db_session)


@router.get(
    "/{indicator_id}",
    summary="Get indicator details by ID",
    description="Retrieve detailed information about a specific indicator.",
    response_model=IndicatorDetailResponse,
    responses={
        200: {
            "description": "Detailed information about the indicator.",
            "model": IndicatorDetailResponse,
        },
        304: {
            "description": "The indicator has not changed since the last request.",
        },
        404: {
            "description": "The indicator with the given ID was not present in the database.",
        },
    },
)
def get_indicator(
    indicator_id: UUID,
    response: Response,
    request: Request,
    db_session: Session = Depends(get_db),
) -> IndicatorDetailResponse:
    indicator_details = get_indicator_details(indicator_id, db_session)

    if indicator_details is None:
        raise HTTPException(status_code=404, detail="Indicator not found")

    # HTTP-Level caching
    etag = generate_etag(indicator_details.model_dump_json())
    print(etag)
    if request.headers.get("If-None-Match") == etag:
        print("304")
        return Response(status_code=304)

    response.headers["Cache-Control"] = "public, max-age=30"
    response.headers["ETag"] = etag
    return indicator_details
