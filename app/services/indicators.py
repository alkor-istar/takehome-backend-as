from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.models.indicators import IndicatorModel
from app.db.models.campaign import CampaignModel, ActorCampaignsModel
from app.db.models.indicators import CampaignIndicatorsModel
from app.db.models.indicators import IndicatorRelationshipModel
from app.schemas.indicators import IndicatorDetailResponse
from app.services.indicator_mappers import (
    campaign_actor_detail_mapper,
    related_indicators_mapper,
)


def get_indicator_details(
    validated_indicator_id: str, db_session: Session
) -> IndicatorDetail | None:
    stmt = (
        select(IndicatorModel)
        .where(IndicatorModel.id == validated_indicator_id)
        .options(
            selectinload(IndicatorModel.campaigns)
            .selectinload(CampaignIndicatorsModel.campaign)
            .selectinload(CampaignModel.threat_actors)
            .selectinload(ActorCampaignsModel.threat_actor),
        )
    )

    indicator = db_session.execute(stmt).scalar_one_or_none()

    if indicator is None:
        return None

    campaigns, actors = campaign_actor_detail_mapper(indicator)

    stmt = (
        select(IndicatorRelationshipModel)
        .where(
            (IndicatorRelationshipModel.source_indicator_id == validated_indicator_id)
            | (IndicatorRelationshipModel.target_indicator_id == validated_indicator_id)
        )
        .options(
            selectinload(IndicatorRelationshipModel.source_indicator),
            selectinload(IndicatorRelationshipModel.target_indicator),
        )
        .order_by(IndicatorRelationshipModel.first_observed.desc())
        .limit(5)
    )

    related_indicators_db = db_session.execute(stmt).scalars().all()

    related_indicators = related_indicators_mapper(
        related_indicators_db,
        validated_indicator_id,
    )

    return IndicatorDetailResponse(
        id=indicator.id,
        type=indicator.type,
        value=indicator.value,
        confidence=indicator.confidence,
        first_seen=indicator.first_seen,
        last_seen=indicator.last_seen,
        threat_actors=actors,
        campaigns=campaigns,
        related_indicators=related_indicators,
    )
