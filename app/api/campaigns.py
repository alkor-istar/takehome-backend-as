from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from sqlalchemy.orm import Session


from app.db.session import get_db
from app.schemas import CampaignIndicatorsResponse, CampaignIndicatorsQuery
from app.services import get_campaign_indicators

router = APIRouter(tags=["campaigns"])


@router.get(
    "/{campaign_id}/indicators",
    response_model=CampaignIndicatorsResponse,
    summary="Get campaign indicators",
    description="Get all indicators associated with a campaign, organized for timeline visualization.",
    responses={
        200: {
            "description": "Campaign indicators",
            "model": CampaignIndicatorsResponse,
        },
        404: {
            "description": "The campaign with the given ID was not present in the database.",
        },
    },
)
def get_campaign_indicators_endpoint(
    campaign_id: UUID,
    filters: CampaignIndicatorsQuery = Depends(),
    db_session: Session = Depends(get_db),
):
    indicators = get_campaign_indicators(campaign_id, filters, db_session)
    if indicators is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return indicators
