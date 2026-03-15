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


class ActorCampaignModel(Base):
    __tablename__ = "actor_campaigns"
    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_actor_campaigns_confidence"),
        Index("idx_actor_campaigns_actor", "threat_actor_id"),
        Index("idx_actor_campaigns_campaign", "campaign_id"),
    )

    threat_actor_id = Column(String, ForeignKey("threat_actors.id"), primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), primary_key=True)
    confidence = Column(Integer, nullable=True)