from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, ConfigDict
from pydantic import ConfigDict


class Campaign(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    status: str | None = None
