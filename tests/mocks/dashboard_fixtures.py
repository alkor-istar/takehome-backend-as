"""Fixture data for dashboard tests. Seed with seed_dashboard_fixtures(session)."""

from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.db import (
    CampaignModel,
    ActorCampaignsModel,
    IndicatorModel,
    CampaignIndicatorsModel,
    ThreatActorModel,
)


# Use recent timestamps so they fall inside 24h, 7d, 30d cutoffs
NOW = datetime.now(timezone.utc)
ONE_HOUR_AGO = NOW - timedelta(hours=1)

DASHBOARD_CAMPAIGN_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
DASHBOARD_ACTOR_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
DASHBOARD_IP_ID = "10101010-1010-1010-1010-101010101010"
DASHBOARD_DOMAIN_ID = "20202020-2020-2020-2020-202020202020"
DASHBOARD_URL_ID = "30303030-3030-3030-3030-303030303030"


def seed_dashboard_fixtures(db: Session) -> None:
    """Insert data so GET /api/dashboard/summary returns non-empty new_indicators, active_campaigns, top_threat_actors, indicator_distribution."""
    db.add(
        ThreatActorModel(
            id=DASHBOARD_ACTOR_ID,
            name="Dashboard Fixture Actor",
            description=None,
            country_origin=None,
            first_seen=ONE_HOUR_AGO,
            last_seen=ONE_HOUR_AGO,
            sophistication_level="high",
        )
    )
    db.add(
        CampaignModel(
            id=DASHBOARD_CAMPAIGN_ID,
            name="Dashboard Fixture Campaign",
            description=None,
            first_seen=ONE_HOUR_AGO,
            last_seen=ONE_HOUR_AGO,
            status="active",
            target_sectors=None,
            target_regions=None,
        )
    )
    db.add(
        ActorCampaignsModel(
            threat_actor_id=DASHBOARD_ACTOR_ID,
            campaign_id=DASHBOARD_CAMPAIGN_ID,
            confidence=90,
        )
    )
    # Indicators with recent first_seen (for new_indicators) and linked to campaign with observed_at (for top_threat_actors)
    db.add(
        IndicatorModel(
            id=DASHBOARD_IP_ID,
            type="ip",
            value="203.0.113.1",
            confidence=88,
            first_seen=ONE_HOUR_AGO,
            last_seen=ONE_HOUR_AGO,
            tags=None,
        )
    )
    db.add(
        IndicatorModel(
            id=DASHBOARD_DOMAIN_ID,
            type="domain",
            value="dashboard-fixture.example.com",
            confidence=75,
            first_seen=ONE_HOUR_AGO,
            last_seen=ONE_HOUR_AGO,
            tags=None,
        )
    )
    db.add(
        IndicatorModel(
            id=DASHBOARD_URL_ID,
            type="url",
            value="https://dashboard-fixture.example.com/path",
            confidence=70,
            first_seen=ONE_HOUR_AGO,
            last_seen=ONE_HOUR_AGO,
            tags=None,
        )
    )
    db.add(
        CampaignIndicatorsModel(
            campaign_id=DASHBOARD_CAMPAIGN_ID,
            indicator_id=DASHBOARD_IP_ID,
            observed_at=ONE_HOUR_AGO,
        )
    )
    db.add(
        CampaignIndicatorsModel(
            campaign_id=DASHBOARD_CAMPAIGN_ID,
            indicator_id=DASHBOARD_DOMAIN_ID,
            observed_at=ONE_HOUR_AGO,
        )
    )
    db.add(
        CampaignIndicatorsModel(
            campaign_id=DASHBOARD_CAMPAIGN_ID,
            indicator_id=DASHBOARD_URL_ID,
            observed_at=ONE_HOUR_AGO,
        )
    )
    db.commit()
