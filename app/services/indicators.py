from sqlalchemy.orm import Session, selectinload
from sqlalchemy import case, select, exists, func, or_
from uuid import UUID

from app.db.models.campaign import CampaignModel, ActorCampaignsModel
from app.db.models.threat_actor import ThreatActorModel
from app.db.models.indicators import (
    IndicatorModel,
    CampaignIndicatorsModel,
    IndicatorRelationshipModel,
)
from app.schemas.indicators import (
    IndicatorDetailResponse,
    IndicatorSearchQuery,
    IndicatorSearchResponse,
    IndicatorSearchItem,
)
from app.services.indicator_mappers import (
    campaign_actor_detail_mapper,
    related_indicators_from_joined_rows,
    search_indicators_mapper,
)


def get_indicator_details(
    indicator_id: UUID, db_session: Session
) -> IndicatorDetailResponse | None:
    indicator_id_str = str(indicator_id)

    indicator_stmt = (
        select(IndicatorModel)
        .where(IndicatorModel.id == indicator_id_str)
        .options(
            selectinload(IndicatorModel.campaigns)
            .selectinload(CampaignIndicatorsModel.campaign)
            .selectinload(CampaignModel.threat_actors)
            .selectinload(ActorCampaignsModel.threat_actor),
        )
    )

    indicator = db_session.execute(indicator_stmt).scalar_one_or_none()

    if indicator is None:
        return None

    campaigns, actors = campaign_actor_detail_mapper(indicator)

    # Single query: JOIN indicator_relationships with indicators (source + target)
    # and use CASE to select the "other" indicator's id/type/value per row.
    ir = IndicatorRelationshipModel.__table__
    si = IndicatorModel.__table__.alias("si")
    ti = IndicatorModel.__table__.alias("ti")
    related_stmt = (
        select(
            ir.c.relationship_type,
            case(
                (ir.c.source_indicator_id == indicator_id_str, ti.c.id),
                else_=si.c.id,
            ).label("other_id"),
            case(
                (ir.c.source_indicator_id == indicator_id_str, ti.c.type),
                else_=si.c.type,
            ).label("other_type"),
            case(
                (ir.c.source_indicator_id == indicator_id_str, ti.c.value),
                else_=si.c.value,
            ).label("other_value"),
        )
        .select_from(ir)
        .join(si, si.c.id == ir.c.source_indicator_id)
        .join(ti, ti.c.id == ir.c.target_indicator_id)
        .where(
            or_(
                ir.c.source_indicator_id == indicator_id_str,
                ir.c.target_indicator_id == indicator_id_str,
            )
        )
        .order_by(ir.c.first_observed.desc())
        .limit(5)
    )
    related_rows = db_session.execute(related_stmt).all()
    related_indicators = related_indicators_from_joined_rows(related_rows)

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


def search_indicators(
    filters: IndicatorSearchQuery, db_session: Session
) -> IndicatorSearchResponse:
    # Base indicator IDs
    filtered_ids = select(IndicatorModel.id).distinct()

    # Add filters
    if filters.type:
        filtered_ids = filtered_ids.where(IndicatorModel.type == filters.type.value)
    if filters.value:
        filtered_ids = filtered_ids.where(
            IndicatorModel.value.ilike(f"%{filters.value}%")
        )
    if filters.first_seen_after:
        filtered_ids = filtered_ids.where(
            IndicatorModel.first_seen >= filters.first_seen_after
        )
    if filters.last_seen_before:
        filtered_ids = filtered_ids.where(
            IndicatorModel.last_seen <= filters.last_seen_before
        )
    if filters.campaign:
        campaign_id = str(filters.campaign)
        filtered_ids = filtered_ids.where(
            IndicatorModel.campaigns.any(
                CampaignIndicatorsModel.campaign_id == campaign_id
            )
        )
    if filters.threat_actor:
        threat_actor_id = str(filters.threat_actor)
        filtered_ids = filtered_ids.where(
            exists(
                select(1)
                .select_from(CampaignIndicatorsModel)
                .join(
                    ActorCampaignsModel,
                    ActorCampaignsModel.campaign_id
                    == CampaignIndicatorsModel.campaign_id,
                )
                .where(
                    CampaignIndicatorsModel.indicator_id == IndicatorModel.id,
                    ActorCampaignsModel.threat_actor_id == threat_actor_id,
                )
            )
        )

    filtered_ids_sq = filtered_ids.subquery("filtered_ids")

    # Campaign count per indicator (count distinct campaign_id)
    campaign_counts_sq = (
        select(
            CampaignIndicatorsModel.indicator_id.label("indicator_id"),
            func.count(func.distinct(CampaignIndicatorsModel.campaign_id)).label(
                "campaign_count"
            ),
        )
        .join(
            filtered_ids_sq,
            filtered_ids_sq.c.id == CampaignIndicatorsModel.indicator_id,
        )
        .group_by(CampaignIndicatorsModel.indicator_id)
        .subquery("campaign_counts")
    )

    # Threat actor count per indicator (count distinct threat_actor_id)
    threat_actor_counts_sq = (
        select(
            CampaignIndicatorsModel.indicator_id.label("indicator_id"),
            func.count(func.distinct(ActorCampaignsModel.threat_actor_id)).label(
                "threat_actor_count"
            ),
        )
        .join(
            ActorCampaignsModel,
            ActorCampaignsModel.campaign_id == CampaignIndicatorsModel.campaign_id,
        )
        .join(
            filtered_ids_sq,
            filtered_ids_sq.c.id == CampaignIndicatorsModel.indicator_id,
        )
        .group_by(CampaignIndicatorsModel.indicator_id)
        .subquery("threat_actor_counts")
    )
    # Final data statement with aggregated counts
    data_stmt = (
        select(
            IndicatorModel.id,
            IndicatorModel.type,
            IndicatorModel.value,
            IndicatorModel.confidence,
            IndicatorModel.first_seen,
            func.coalesce(campaign_counts_sq.c.campaign_count, 0).label(
                "campaign_count"
            ),
            func.coalesce(threat_actor_counts_sq.c.threat_actor_count, 0).label(
                "threat_actor_count"
            ),
            func.count().over().label("total_count"),
        )
        .select_from(filtered_ids_sq)
        .join(IndicatorModel, filtered_ids_sq.c.id == IndicatorModel.id)
        .outerjoin(
            campaign_counts_sq, campaign_counts_sq.c.indicator_id == IndicatorModel.id
        )
        .outerjoin(
            threat_actor_counts_sq,
            threat_actor_counts_sq.c.indicator_id == IndicatorModel.id,
        )
        .order_by(IndicatorModel.first_seen.desc(), IndicatorModel.id.asc())
        .offset((filters.page - 1) * filters.limit)
        .limit(filters.limit)
    )
    rows = db_session.execute(data_stmt).all()

    # Total rows for pagination
    # From window count when we have rows; else one extra count query
    if rows:
        total = rows[0].total_count
    else:
        total = db_session.execute(
            select(func.count()).select_from(filtered_ids_sq)
        ).scalar_one()

    # Convert rows to items
    items = search_indicators_mapper(rows)

    # Return response
    return IndicatorSearchResponse.from_items(
        items=items,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )
