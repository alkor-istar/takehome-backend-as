"""Fixture data for campaign indicators tests. Seed with seed_campaign_fixtures(session)."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.campaign import CampaignModel, ActorCampaignsModel
from app.db.models.indicators import IndicatorModel, CampaignIndicatorsModel
from app.db.models.threat_actor import ThreatActorModel


CAMPAIGN_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
INDICATOR_IP_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
INDICATOR_DOMAIN_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
THREAT_ACTOR_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"

# Same day so timeline has one bucket when group_by=day
OBSERVED_DAY = datetime(2024, 7, 10, 14, 30, 0)
OBSERVED_DAY_2 = datetime(2024, 7, 10, 16, 0, 0)


def seed_campaign_fixtures(db: Session) -> None:
    """Insert campaign with two indicators so GET /api/campaigns/{id}/indicators returns timeline and summary."""
    db.add(
        ThreatActorModel(
            id=THREAT_ACTOR_ID,
            name="Campaign Fixture Actor",
            description=None,
            country_origin=None,
            first_seen=OBSERVED_DAY,
            last_seen=OBSERVED_DAY,
            sophistication_level="medium",
        )
    )
    db.add(
        CampaignModel(
            id=CAMPAIGN_ID,
            name="Campaign Fixture",
            description="Fixture for campaign indicators tests",
            first_seen=OBSERVED_DAY,
            last_seen=OBSERVED_DAY_2,
            status="active",
            target_sectors=None,
            target_regions=None,
        )
    )
    db.add(
        ActorCampaignsModel(
            threat_actor_id=THREAT_ACTOR_ID,
            campaign_id=CAMPAIGN_ID,
            confidence=70,
        )
    )
    db.add(
        IndicatorModel(
            id=INDICATOR_IP_ID,
            type="ip",
            value="10.0.0.1",
            confidence=85,
            first_seen=OBSERVED_DAY,
            last_seen=OBSERVED_DAY,
            tags=None,
        )
    )
    db.add(
        IndicatorModel(
            id=INDICATOR_DOMAIN_ID,
            type="domain",
            value="campaign-fixture.example.com",
            confidence=80,
            first_seen=OBSERVED_DAY,
            last_seen=OBSERVED_DAY,
            tags=None,
        )
    )
    db.add(
        CampaignIndicatorsModel(
            campaign_id=CAMPAIGN_ID,
            indicator_id=INDICATOR_IP_ID,
            observed_at=OBSERVED_DAY,
        )
    )
    db.add(
        CampaignIndicatorsModel(
            campaign_id=CAMPAIGN_ID,
            indicator_id=INDICATOR_DOMAIN_ID,
            observed_at=OBSERVED_DAY_2,
        )
    )
    db.commit()
