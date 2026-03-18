import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db.session import get_db
from app.db import (
    Base,
    CampaignModel,
    ActorCampaignsModel,
    IndicatorModel,
    CampaignIndicatorsModel,
    IndicatorRelationshipModel,
    ObservationModel,
    ThreatActorModel,
)


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture()
def client_with_memory_db():
    # TestClient with in-memory SQLite; get_db overridden.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    def get_db_override():
        yield session

    app = create_app()
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    try:
        yield client, session
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
