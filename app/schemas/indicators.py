from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


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


class IndicatorDetailThreatActorRef(BaseModel):
    id: str
    name: str
    confidence: int | None = None


class IndicatorDetailCampaignRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    active: bool


class IndicatorDetailRelatedIndicatorRef(BaseModel):
    id: str
    type: str
    value: str
    relationship: str


class IndicatorDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    value: str
    confidence: int | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    threat_actors: list[IndicatorDetailThreatActorRef]
    campaigns: list[IndicatorDetailCampaignRef]
    related_indicators: list[IndicatorDetailRelatedIndicatorRef]
