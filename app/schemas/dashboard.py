from typing import Literal
from pydantic import BaseModel


class DashboardSummaryQuery(BaseModel):
    time_range: Literal["24h", "7d", "30d"] = "7d"


class ThreatActorActivity(BaseModel):
    id: str
    name: str
    indicator_count: int


class DashboardSummaryResponse(BaseModel):
    time_range: Literal["24h", "7d", "30d"]
    new_indicators: dict[str, int]
    active_campaigns: int
    top_threat_actors: list[ThreatActorActivity]
    indicator_distribution: dict[str, int]
