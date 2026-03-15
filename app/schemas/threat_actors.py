from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ThreatActor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    confidence: int
    description: str
    country_origin: str
    first_seen: datetime
    last_seen: datetime
    sophistication_level: str
    created_at: datetime
