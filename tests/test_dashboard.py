"""Tests for dashboard API."""

from tests.mocks.dashboard_fixtures import (
    DASHBOARD_ACTOR_ID,
    seed_dashboard_fixtures,
)


def test_get_dashboard_summary(client_with_memory_db):
    """GET /api/dashboard/summary returns 200 with time_range, new_indicators, active_campaigns, top_threat_actors, indicator_distribution."""
    client, session = client_with_memory_db
    seed_dashboard_fixtures(session)

    response = client.get("/api/dashboard/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["time_range"] in ("24h", "7d", "30d")
    assert "new_indicators" in data
    assert set(data["new_indicators"].keys()) == {"ip", "domain", "url", "hash"}
    assert data["new_indicators"]["ip"] >= 1
    assert data["new_indicators"]["domain"] >= 1
    assert data["new_indicators"]["url"] >= 1
    assert data["active_campaigns"] >= 1
    assert "top_threat_actors" in data
    assert len(data["top_threat_actors"]) >= 1
    actor = next(
        (a for a in data["top_threat_actors"] if a["id"] == DASHBOARD_ACTOR_ID),
        None,
    )
    assert actor is not None
    assert actor["name"] == "Dashboard Fixture Actor"
    assert actor["indicator_count"] >= 1
    assert set(data["indicator_distribution"].keys()) == {"ip", "domain", "url", "hash"}
    assert data["indicator_distribution"]["ip"] >= 1
    assert data["indicator_distribution"]["domain"] >= 1
    assert data["indicator_distribution"]["url"] >= 1


def test_get_dashboard_summary_time_range_param(client_with_memory_db):
    """GET /api/dashboard/summary?time_range=24h returns 200 and echoes time_range."""
    client, session = client_with_memory_db
    seed_dashboard_fixtures(session)

    response = client.get("/api/dashboard/summary", params={"time_range": "24h"})

    assert response.status_code == 200
    assert response.json()["time_range"] == "24h"


def test_get_dashboard_summary_empty(client_with_memory_db):
    """GET /api/dashboard/summary with no data returns zeros and empty lists."""
    client, _ = client_with_memory_db

    response = client.get("/api/dashboard/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["new_indicators"] == {"ip": 0, "domain": 0, "url": 0, "hash": 0}
    assert data["active_campaigns"] == 0
    assert data["top_threat_actors"] == []
    assert data["indicator_distribution"] == {"ip": 0, "domain": 0, "url": 0, "hash": 0}


def test_get_dashboard_summary_invalid_time_range(client):
    """GET /api/dashboard/summary?time_range=invalid returns 400."""
    response = client.get("/api/dashboard/summary", params={"time_range": "invalid"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data
