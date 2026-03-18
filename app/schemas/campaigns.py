from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Campaign(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    status: str | None = None


class CampaignTimelineIndicatorRef(BaseModel):
    id: str
    type: str
    value: str


class CampaignTimelineBucket(BaseModel):
    period: str
    indicators: list[CampaignTimelineIndicatorRef]
    counts: dict[str, int]


class CampaignSummary(BaseModel):
    total_indicators: int
    unique_ips: int
    unique_domains: int
    duration_days: int


class CampaignIndicatorsResponse(BaseModel):
    campaign: Campaign
    timeline: list[CampaignTimelineBucket]
    summary: CampaignSummary


class CampaignIndicatorsQuery(BaseModel):
    group_by: Literal["day", "week"] = Field(default="day")
    start_date: datetime | None = None
    end_date: datetime | None = None
