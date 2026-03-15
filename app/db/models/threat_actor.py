from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from app.db.models.base import Base
from sqlalchemy.orm import relationship


class ThreatActorModel(Base):
    __tablename__ = "threat_actors"
    __table_args__ = (
        CheckConstraint(
            "sophistication_level IN ('low', 'medium', 'high', 'advanced')",
            name="ck_threat_actors_sophistication_level",
        ),
    )

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    country_origin = Column(String, nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    sophistication_level = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    campaigns = relationship(
        "ActorCampaignsModel", back_populates="threat_actor", lazy="selectin"
    )
