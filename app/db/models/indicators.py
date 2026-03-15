from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from app.db.models.base import Base


class IndicatorModel(Base):
    __tablename__ = "indicators"
    __table_args__ = (
        CheckConstraint("type IN ('ip', 'domain', 'url', 'hash')", name="ck_indicators_type"),
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_indicators_confidence"),
        UniqueConstraint("type", "value", name="uq_indicators_type_value"),
        Index("idx_indicators_type", "type"),
        Index("idx_indicators_value", "value"),
        Index("idx_indicators_first_seen", "first_seen"),
        Index("idx_indicators_last_seen", "last_seen"),
    )

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    confidence = Column(Integer, nullable=True)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class CampaignIndicatorModel(Base):
    __tablename__ = "campaign_indicators"
    __table_args__ = (
        Index("idx_campaign_indicators_campaign", "campaign_id"),
        Index("idx_campaign_indicators_indicator", "indicator_id"),
    )

    campaign_id = Column(String, ForeignKey("campaigns.id"), primary_key=True)
    indicator_id = Column(String, ForeignKey("indicators.id"), primary_key=True)
    observed_at = Column(DateTime, nullable=True)


class IndicatorRelationshipModel(Base):
    __tablename__ = "indicator_relationships"
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('same_campaign', 'same_infrastructure', 'co_occurring')",
            name="ck_indicator_relationships_type",
        ),
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_indicator_relationships_confidence"),
    )

    source_indicator_id = Column(String, ForeignKey("indicators.id"), primary_key=True)
    target_indicator_id = Column(String, ForeignKey("indicators.id"), primary_key=True)
    relationship_type = Column(String, primary_key=True)
    confidence = Column(Integer, nullable=True)
    first_observed = Column(DateTime, nullable=True)


class ObservationModel(Base):
    __tablename__ = "observations"
    __table_args__ = (
        Index("idx_observations_indicator", "indicator_id"),
        Index("idx_observations_timestamp", "observed_at"),
    )

    id = Column(String, primary_key=True)
    indicator_id = Column(String, ForeignKey("indicators.id"))
    observed_at = Column(DateTime, nullable=True)
    source = Column(String, nullable=True)
    notes = Column(String, nullable=True)
