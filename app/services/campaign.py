from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, case, select
from fastapi import HTTPException
from app.db.models.campaign import CampaignModel
from app.db.models.indicators import IndicatorModel, CampaignIndicatorsModel

from app.schemas.campaigns import (
    Campaign,
    CampaignSummary,
    CampaignIndicatorsResponse,
    CampaignIndicatorsQuery,
    CampaignTimelineBucket,
    CampaignTimelineIndicatorRef,
)
from app.services.campaign_mappers import campaign_timeline_mapper


def get_campaign_indicators(
    campaign_id: UUID, filters: CampaignIndicatorsQuery, db_session: Session
) -> CampaignIndicatorsResponse | None:
    campaign_id_str = str(campaign_id)

    stmt = select(CampaignModel).where(CampaignModel.id == campaign_id_str)
    campaign = db_session.execute(stmt).scalar_one_or_none()
    if campaign is None:
        return None

    # Group by day or week
    if filters.group_by == "day":
        period_expr = func.strftime("%Y-%m-%d", CampaignIndicatorsModel.observed_at)
    elif filters.group_by == "week":
        period_expr = func.strftime("%Y-W%W", CampaignIndicatorsModel.observed_at)

    conditions = [CampaignIndicatorsModel.campaign_id == campaign_id_str]
    # Filter by date range
    if filters.start_date:
        conditions.append(CampaignIndicatorsModel.observed_at >= filters.start_date)
    if filters.end_date:
        conditions.append(CampaignIndicatorsModel.observed_at <= filters.end_date)

    # Indicators timeline query
    timeline_rows_stmt = (
        select(
            period_expr.label("period"),
            IndicatorModel.id.label("id"),
            IndicatorModel.type.label("type"),
            IndicatorModel.value.label("value"),
        )
        .join(IndicatorModel, CampaignIndicatorsModel.indicator_id == IndicatorModel.id)
        .where(*conditions)
        .order_by(period_expr.asc(), CampaignIndicatorsModel.observed_at.desc())
    )
    timeline_rows = db_session.execute(timeline_rows_stmt).all()

    # Indicators counts query
    counts_stmt = (
        select(
            period_expr.label("period"),
            IndicatorModel.type.label("type"),
            func.count(func.distinct(CampaignIndicatorsModel.indicator_id)).label(
                "count"
            ),
        )
        .join(IndicatorModel, IndicatorModel.id == CampaignIndicatorsModel.indicator_id)
        .where(*conditions)
        .group_by(period_expr, IndicatorModel.type)
    )
    counts_rows = db_session.execute(counts_stmt).all()

    # Summary query. This summarizes in the selected time period. If we need to summarize
    # across all time, we need to use conditions without the start and end date filters.
    summary_stmt = (
        select(
            func.count(CampaignIndicatorsModel.indicator_id).label("total_indicators"),
            func.count(
                func.distinct(
                    case((IndicatorModel.type == "ip", IndicatorModel.id), else_=None)
                )
            ).label("unique_ips"),
            func.count(
                func.distinct(
                    case(
                        (IndicatorModel.type == "domain", IndicatorModel.id), else_=None
                    )
                )
            ).label("unique_domains"),
            func.min(CampaignIndicatorsModel.observed_at).label("first_seen"),
            func.max(CampaignIndicatorsModel.observed_at).label("last_seen"),
        )
        .join(IndicatorModel, IndicatorModel.id == CampaignIndicatorsModel.indicator_id)
        .where(*conditions)
    )
    summary_row = db_session.execute(summary_stmt).one()

    if summary_row.first_seen and summary_row.last_seen:
        duration_days = (
            summary_row.last_seen.date() - summary_row.first_seen.date()
        ).days
    else:
        duration_days = 0

    timeline = campaign_timeline_mapper(timeline_rows, counts_rows)

    return CampaignIndicatorsResponse(
        campaign=Campaign.model_validate(campaign),
        timeline=timeline,
        summary=CampaignSummary(
            total_indicators=summary_row.total_indicators or 0,
            unique_ips=summary_row.unique_ips or 0,
            unique_domains=summary_row.unique_domains or 0,
            duration_days=duration_days,
        ),
    )
