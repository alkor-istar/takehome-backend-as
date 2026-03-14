from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class Indicator(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    value: str
    confidence: int
    first_seen: datetime
    last_seen: datetime
    tags: str
    created_at: datetime
