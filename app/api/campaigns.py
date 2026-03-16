from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from sqlalchemy.orm import Session


from app.db.session import get_db
from app.schemas.campaigns import CampaignIndicatorsResponse, CampaignIndicatorsQuery
from app.services.campaign import get_campaign_indicators

router = APIRouter(tags=["campaigns"])


@router.get("/{campaign_id}/indicators", response_model=CampaignIndicatorsResponse)
def get_campaign_indicators_endpoint(
    campaign_id: UUID,
    filters: CampaignIndicatorsQuery = Depends(),
    db_session: Session = Depends(get_db),
):
    indicators = get_campaign_indicators(campaign_id, filters, db_session)
    return indicators
