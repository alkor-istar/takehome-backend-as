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
from sqlalchemy.orm import relationship
from app.db.models.base import Base


class CampaignModel(Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'dormant', 'completed')",
            name="ck_campaigns_status",
        ),
    )

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
    target_sectors = Column(String, nullable=True)
    target_regions = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    # Not use 'secondary' as these relationship tables have attributes
    indicators = relationship(
        "CampaignIndicatorsModel",
        back_populates="campaign",
    )

    threat_actors = relationship("ActorCampaignsModel", back_populates="campaign")


class ActorCampaignsModel(Base):
    __tablename__ = "actor_campaigns"
    __table_args__ = (
        CheckConstraint(
            "confidence BETWEEN 0 AND 100", name="ck_actor_campaigns_confidence"
        ),
        Index("idx_actor_campaigns_actor", "threat_actor_id"),
        Index("idx_actor_campaigns_campaign", "campaign_id"),
    )

    threat_actor_id = Column(String, ForeignKey("threat_actors.id"), primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), primary_key=True)
    confidence = Column(Integer, nullable=True)

    threat_actor = relationship("ThreatActorModel", back_populates="campaigns")
    campaign = relationship("CampaignModel", back_populates="threat_actors")
