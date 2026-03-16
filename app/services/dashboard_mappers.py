from app.db.models.indicators import IndicatorModel
from app.db.models.threat_actor import ThreatActorModel
from app.schemas.dashboard import ThreatActorActivity


def indicators_mapper(indicators_rows: list[IndicatorModel]) -> dict[str, int]:
    return {
        **{"ip": 0, "domain": 0, "url": 0, "hash": 0},
        **{r.type: (r.count or 0) for r in indicators_rows},
    }


def threat_actor_activity_mapper(
    top_threat_actors_rows: list[ThreatActorModel],
) -> list[ThreatActorActivity]:
    return [
        ThreatActorActivity(id=r.id, name=r.name, indicator_count=r.indicator_count)
        for r in top_threat_actors_rows
    ]
