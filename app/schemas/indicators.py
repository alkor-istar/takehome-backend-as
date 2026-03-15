from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.threat_actors import ThreatActor
from app.schemas.campaigns import Campaign


class Indicator(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    value: str
    confidence: int
    first_seen: datetime
    last_seen: datetime
    tags: str
    created_at: datetime


class IndicatorDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    value: str
    confidence: int
    first_seen: datetime
    last_seen: datetime
    threat_actors: list[ThreatActor]
    campaigns: list[Campaign]
    related_indicators: list[Indicator]
