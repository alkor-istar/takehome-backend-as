from app.db.models.indicators import CampaignIndicatorsModel
from app.schemas.campaigns import CampaignTimelineBucket, CampaignTimelineIndicatorRef


def campaign_timeline_mapper(
    timeline_rows: list[CampaignIndicatorsModel],
    counts_rows: list[CampaignIndicatorsModel],
) -> list[CampaignTimelineBucket]:
    buckets: dict[str, CampaignTimelineBucket] = {}
    for r in timeline_rows:
        if r.period not in buckets:
            buckets[r.period] = CampaignTimelineBucket(
                period=r.period,
                indicators=[],
                counts={},
            )
        buckets[r.period].indicators.append(
            CampaignTimelineIndicatorRef(id=r.id, type=r.type, value=r.value)
        )
    for r in counts_rows:
        if r.period not in buckets:
            buckets[r.period] = CampaignTimelineBucket(
                period=r.period,
                indicators=[],
                counts={},
            )
        buckets[r.period].counts[r.type] = r.count

    return [buckets[k] for k in sorted(buckets.keys())]
