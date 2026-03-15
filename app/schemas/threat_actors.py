from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ThreatActor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    country_origin: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    sophistication_level: str | None = None
    created_at: datetime | None = None


class ThreatActorRef(BaseModel):
    id: str
    name: str
    confidence: int | None = None
