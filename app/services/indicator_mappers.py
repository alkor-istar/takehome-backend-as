from app.db.models.indicators import IndicatorModel
from app.db.models.campaign import CampaignModel
from app.db.models.threat_actor import ThreatActorModel
from app.db.models.indicators import IndicatorRelationshipModel
from app.schemas.indicators import (
    IndicatorDetailThreatActorRef,
    IndicatorDetailCampaignRef,
    IndicatorDetailRelatedIndicatorRef,
    IndicatorSearchItem,
)


def related_indicators_from_joined_rows(
    rows: list,
) -> list[IndicatorDetailRelatedIndicatorRef]:
    """Build related-indicator refs from the single-query JOIN result (other_id, other_type, other_value, relationship_type)."""
    return [
        IndicatorDetailRelatedIndicatorRef(
            id=row.other_id,
            type=row.other_type,
            value=row.other_value,
            relationship=row.relationship_type,
        )
        for row in rows
    ]


def confidence_value(c: int | None) -> int:
    # Treat None as lowest so we keep the actor with higher confidence.
    return -1 if c is None else c


def campaign_actor_detail_mapper(
    indicator: IndicatorModel,
) -> tuple[list[IndicatorDetailCampaignRef], list[IndicatorDetailThreatActorRef]]:
    campaigns = []
    actors_by_id: dict[str, IndicatorDetailThreatActorRef] = {}
    for ci in indicator.campaigns:
        c = ci.campaign
        campaigns.append(
            IndicatorDetailCampaignRef(
                id=c.id, name=c.name, active=c.status == "active"
            )
        )
        # Deduplicate actors by id and keep the one with higher confidence.
        for ac in c.threat_actors:
            a = ac.threat_actor
            ref = IndicatorDetailThreatActorRef(
                id=a.id, name=a.name, confidence=ac.confidence
            )
            existing = actors_by_id.get(a.id)
            if existing is None or confidence_value(ac.confidence) > confidence_value(
                existing.confidence
            ):
                actors_by_id[a.id] = ref
    return campaigns, list(actors_by_id.values())


def search_indicators_mapper(
    rows: list[IndicatorModel],
) -> list[IndicatorSearchItem]:
    return [
        IndicatorSearchItem(
            id=r.id,
            type=r.type,
            value=r.value,
            confidence=r.confidence,
            first_seen=r.first_seen,
            campaign_count=r.campaign_count,
            threat_actor_count=r.threat_actor_count,
        )
        for r in rows
    ]
