from app.schemas.dashboard import DashboardSummaryQuery
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from sqlalchemy import func, select
from app.db.models.indicators import IndicatorModel, CampaignIndicatorsModel
from app.db.models.campaign import CampaignModel, ActorCampaignsModel
from app.db.models.threat_actor import ThreatActorModel
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_mappers import (
    indicators_mapper,
    threat_actor_activity_mapper,
)


def get_dashboard_summary(
    query: DashboardSummaryQuery, db_session: Session
) -> DashboardSummaryResponse:

    now = datetime.now(timezone.utc)
    if query.time_range == "24h":
        cutoff = now - timedelta(hours=24)
    elif query.time_range == "7d":
        cutoff = now - timedelta(days=7)
    elif query.time_range == "30d":
        cutoff = now - timedelta(days=30)

    # New indicators count per type
    # Assumtion: first_seen can be used to determine if an indicator is new
    indicators_stmt = (
        select(
            IndicatorModel.type,
            func.count(IndicatorModel.id).label("count"),
        )
        .where(IndicatorModel.first_seen >= cutoff)
        .group_by(IndicatorModel.type)
    )
    indicators_rows = db_session.execute(indicators_stmt).all()

    new_indicators = indicators_mapper(indicators_rows)

    # Active campaigns count
    active_campaigns_stmt = select(func.count(CampaignModel.id)).where(
        CampaignModel.status == "active"
    )
    active_campaigns_rows = db_session.execute(active_campaigns_stmt).scalar_one()
    active_campaigns = active_campaigns_rows or 0

    # Top 5 threat actors by indicator count
    # This top is computed filtering by the observed_at date of the indicators so
    # it's only the threat actors that have indicators in the selected time range.
    top_threat_actors_stmt = (
        select(
            ThreatActorModel.id,
            ThreatActorModel.name,
            func.count(func.distinct(CampaignIndicatorsModel.indicator_id)).label(
                "indicator_count"
            ),
        )
        .select_from(ActorCampaignsModel)
        .join(
            ThreatActorModel, ThreatActorModel.id == ActorCampaignsModel.threat_actor_id
        )
        .join(
            CampaignIndicatorsModel,
            CampaignIndicatorsModel.campaign_id == ActorCampaignsModel.campaign_id,
        )
        .where(CampaignIndicatorsModel.observed_at >= cutoff)
        .group_by(ThreatActorModel.id, ThreatActorModel.name)
        .order_by(
            func.count(func.distinct(CampaignIndicatorsModel.indicator_id)).desc()
        )
        .limit(5)
    )
    top_threat_actors_rows = db_session.execute(top_threat_actors_stmt).all()
    top_threat_actors = threat_actor_activity_mapper(top_threat_actors_rows)

    # Indicator distribution by type
    indicator_distribution_stmt = select(
        IndicatorModel.type,
        func.count(IndicatorModel.id).label("count"),
    ).group_by(IndicatorModel.type)
    indicator_distribution_rows = db_session.execute(indicator_distribution_stmt).all()
    indicator_distribution = indicators_mapper(indicator_distribution_rows)

    return DashboardSummaryResponse(
        time_range=query.time_range,
        new_indicators=new_indicators,
        active_campaigns=active_campaigns,
        top_threat_actors=top_threat_actors,
        indicator_distribution=indicator_distribution,
    )
