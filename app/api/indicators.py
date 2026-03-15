from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.session import get_db
from uuid import UUID

from app.schemas.indicators import IndicatorDetail, IndicatorRef
from app.schemas.campaigns import CampaignRef
from app.schemas.threat_actors import ThreatActorRef
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.models.indicators import (
    IndicatorModel,
    CampaignIndicatorsModel,
    IndicatorRelationshipModel,
)
from app.db.models.threat_actor import ThreatActorModel
from app.db.models.campaign import CampaignModel, ActorCampaignsModel


router = APIRouter(tags=["indicators"])


@router.get("/{indicator_id}")
def get_indicator(
    indicator_id: str, db_session: Session = Depends(get_db)
) -> IndicatorDetail:
    try:
        validated_indicator_id = str(UUID(indicator_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid indicator ID")

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
        raise HTTPException(status_code=404, detail="Indicator not found")

    campaigns = []
    actors = []

    for ci in indicator.campaigns:
        c = ci.campaign

        campaigns.append(CampaignRef(id=c.id, name=c.name, active=c.status == "active"))

        for ac in c.threat_actors:
            a = ac.threat_actor
            actors.append(
                ThreatActorRef(id=a.id, name=a.name, confidence=ac.confidence)
            )

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

    related_indicators: list[IndicatorRef] = []
    for related_indicator_db in related_indicators_db:
        # Need to check if the related indicator is the source or target
        other_indicator = (
            related_indicator_db.source_indicator
            if related_indicator_db.target_indicator_id == validated_indicator_id
            else related_indicator_db.target_indicator
        )

        related_indicators.append(
            IndicatorRef(
                id=other_indicator.id,
                type=other_indicator.type,
                value=other_indicator.value,
                relationship=related_indicator_db.relationship_type,
            )
        )

    return IndicatorDetail(
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
