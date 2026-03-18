from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

from uuid import UUID
from app.schemas.common import PaginatedResponse, Page, Limit


class Indicator(BaseModel):
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
    id: str
    name: str
    active: bool


class IndicatorDetailRelatedIndicatorRef(BaseModel):
    id: str
    type: str
    value: str
    relationship: str


class IndicatorDetailResponse(BaseModel):
    id: str
    type: str
    value: str
    confidence: int | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    threat_actors: list[IndicatorDetailThreatActorRef]
    campaigns: list[IndicatorDetailCampaignRef]
    related_indicators: list[IndicatorDetailRelatedIndicatorRef]


class IndicatorSearchQueryType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"


class IndicatorSearchQuery(BaseModel):
    type: IndicatorSearchQueryType | None = None
    value: str | None = None
    threat_actor: UUID | None = None
    campaign: UUID | None = None
    first_seen_after: datetime | None = None
    last_seen_before: datetime | None = None
    page: Page = 1
    limit: Limit = 20


class IndicatorSearchItem(BaseModel):
    id: str
    type: str
    value: str
    confidence: int | None = None
    first_seen: datetime | None = None
    campaign_count: int
    threat_actor_count: int


IndicatorSearchResponse = PaginatedResponse[IndicatorSearchItem]
