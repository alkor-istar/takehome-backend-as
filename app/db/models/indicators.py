# app/db/models/indicators.py
from sqlalchemy import Column, Integer, String, DateTime, UUID
from app.db.models.base import Base


class IndicatorModel(Base):
    __tablename__ = "indicators"

    id = Column(UUID, primary_key=True, index=True)
    type = Column(String, index=True, nullable=False)
    value = Column(String, index=True, nullable=False)
    confidence = Column(Integer, nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
