from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

from app.schemas.threat_actors import ThreatActorRef
from app.schemas.campaigns import CampaignRef


class Indicator(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    value: str
    confidence: int | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    tags: str | None = None
    created_at: datetime | None = None


class IndicatorRef(BaseModel):
    id: str
    type: str
    value: str
    relationship: str


class IndicatorDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    value: str
    confidence: int | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    threat_actors: list[ThreatActorRef]
    campaigns: list[CampaignRef]
    related_indicators: list[IndicatorRef]
