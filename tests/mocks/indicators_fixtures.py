"""Fixture data for indicator details tests. Seed with seed_indicator_details_fixtures(session)."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db import (
    CampaignModel,
    ActorCampaignsModel,
    IndicatorModel,
    CampaignIndicatorsModel,
    IndicatorRelationshipModel,
    ThreatActorModel,
)


# IDs used by the fixture (one main indicator + one related, one campaign, one threat actor)
INDICATOR_ID = "11111111-1111-1111-1111-111111111111"
RELATED_INDICATOR_ID = "22222222-2222-2222-2222-222222222222"
CAMPAIGN_ID = "33333333-3333-3333-3333-333333333333"
THREAT_ACTOR_ID = "44444444-4444-4444-4444-444444444444"

SOME_WHEN = datetime(2024, 6, 15, 12, 0, 0)


def seed_indicator_details_fixtures(db: Session) -> None:
    """Insert minimal data so GET /api/indicators/{INDICATOR_ID} returns full details."""
    # Threat actor
    db.add(
        ThreatActorModel(
            id=THREAT_ACTOR_ID,
            name="Fixture Actor",
            description=None,
            country_origin=None,
            first_seen=SOME_WHEN,
            last_seen=SOME_WHEN,
            sophistication_level="medium",
        )
    )
    # Campaign (active so response has active=True)
    db.add(
        CampaignModel(
            id=CAMPAIGN_ID,
            name="Fixture Campaign",
            description=None,
            first_seen=SOME_WHEN,
            last_seen=SOME_WHEN,
            status="active",
            target_sectors=None,
            target_regions=None,
        )
    )
    # Actor <-> Campaign
    db.add(
        ActorCampaignsModel(
            threat_actor_id=THREAT_ACTOR_ID,
            campaign_id=CAMPAIGN_ID,
            confidence=80,
        )
    )
    # Main indicator
    db.add(
        IndicatorModel(
            id=INDICATOR_ID,
            type="ip",
            value="192.168.1.1",
            confidence=90,
            first_seen=SOME_WHEN,
            last_seen=SOME_WHEN,
            tags=None,
        )
    )
    # Related indicator (for related_indicators in response)
    db.add(
        IndicatorModel(
            id=RELATED_INDICATOR_ID,
            type="domain",
            value="evil.example.com",
            confidence=70,
            first_seen=SOME_WHEN,
            last_seen=SOME_WHEN,
            tags=None,
        )
    )
    # Campaign <-> Indicator (link main indicator to campaign)
    db.add(
        CampaignIndicatorsModel(
            campaign_id=CAMPAIGN_ID,
            indicator_id=INDICATOR_ID,
            observed_at=SOME_WHEN,
        )
    )
    # Indicator relationship (main -> related)
    db.add(
        IndicatorRelationshipModel(
            source_indicator_id=INDICATOR_ID,
            target_indicator_id=RELATED_INDICATOR_ID,
            relationship_type="same_infrastructure",
            confidence=85,
            first_observed=SOME_WHEN,
        )
    )
    db.commit()
