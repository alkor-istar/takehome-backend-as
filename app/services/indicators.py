from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, exists, func
from uuid import UUID

from app.db.models.indicators import IndicatorModel
from app.db.models.campaign import CampaignModel, ActorCampaignsModel
from app.db.models.threat_actor import ThreatActorModel
from app.db.models.indicators import CampaignIndicatorsModel
from app.db.models.indicators import IndicatorRelationshipModel
from app.schemas.indicators import (
    IndicatorDetailResponse,
    IndicatorSearchQuery,
    IndicatorSearchResponse,
    IndicatorSearchItem,
)
from app.services.indicator_mappers import (
    campaign_actor_detail_mapper,
    related_indicators_mapper,
    search_indicators_mapper,
)


def get_indicator_details(
    indicator_id: UUID, db_session: Session
) -> IndicatorDetailResponse | None:
    indicator_id_str = str(indicator_id)

    stmt = (
        select(IndicatorModel)
        .where(IndicatorModel.id == indicator_id_str)
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
            (IndicatorRelationshipModel.source_indicator_id == indicator_id_str)
            | (IndicatorRelationshipModel.target_indicator_id == indicator_id_str)
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
        indicator_id_str,
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

    # Total count for pagination
    total_stmt = select(func.count()).select_from(filtered_ids_sq)
    total = db_session.execute(total_stmt).scalar_one()

    # Campaign count per indicator (count distinct campaign_id)
    campaign_counts_sq = (
        select(
            CampaignIndicatorsModel.indicator_id.label("indicator_id"),
            func.count(func.distinct(CampaignIndicatorsModel.campaign_id)).label(
                "campaign_count"
            ),
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
        )
        .join(filtered_ids_sq, filtered_ids_sq.c.id == IndicatorModel.id)
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

    # Convert rows to items
    items = search_indicators_mapper(rows)

    # Return response
    return IndicatorSearchResponse.from_items(
        items=items,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )
