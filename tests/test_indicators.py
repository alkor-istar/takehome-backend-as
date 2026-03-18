"""Tests for indicators API (details and search)."""

import uuid

from tests.mocks.indicators_fixtures import (
    CAMPAIGN_ID,
    INDICATOR_ID,
    THREAT_ACTOR_ID,
    seed_indicator_details_fixtures,
)


def test_get_indicator_details(client_with_memory_db):
    """GET /api/indicators/{id} returns 200 and full structure for a seeded indicator."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get(f"/api/indicators/{INDICATOR_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == INDICATOR_ID
    assert data["type"] == "ip"
    assert data["value"] == "192.168.1.1"
    assert data["confidence"] == 90
    assert "first_seen" in data
    assert "last_seen" in data
    assert data["threat_actors"] == [
        {"id": "44444444-4444-4444-4444-444444444444", "name": "Fixture Actor", "confidence": 80}
    ]
    assert data["campaigns"] == [
        {"id": "33333333-3333-3333-3333-333333333333", "name": "Fixture Campaign", "active": True}
    ]
    assert len(data["related_indicators"]) == 1
    assert data["related_indicators"][0]["id"] == "22222222-2222-2222-2222-222222222222"
    assert data["related_indicators"][0]["type"] == "domain"
    assert data["related_indicators"][0]["value"] == "evil.example.com"
    assert data["related_indicators"][0]["relationship"] == "same_infrastructure"


def test_get_indicator_details_not_found(client_with_memory_db):
    """GET /api/indicators/{id} returns 404 when the indicator does not exist."""
    client, _ = client_with_memory_db
    unknown_id = uuid.uuid4()

    response = client.get(f"/api/indicators/{unknown_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Indicator not found"


def test_get_indicator_details_invalid_uuid(client):
    """GET /api/indicators/{id} returns 400 when indicator_id is not a valid UUID."""
    response = client.get("/api/indicators/not-a-uuid")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data
    assert len(data["errors"]) >= 1
    # Path param validation error should mention the invalid value
    error_locs = [e.get("loc") or e.get("location") for e in data["errors"]]
    assert any("indicator_id" in str(loc) or "path" in str(loc) for loc in error_locs)


def test_search_indicators_invalid_type(client):
    """GET /api/indicators/search?type=invalid returns 400."""
    response = client.get("/api/indicators/search", params={"type": "invalid"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_search_indicators_invalid_page(client):
    """GET /api/indicators/search?page=0 returns 400."""
    response = client.get("/api/indicators/search", params={"page": 0})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_search_indicators_invalid_limit(client):
    """GET /api/indicators/search?limit=0 and limit=101 return 400."""
    r1 = client.get("/api/indicators/search", params={"limit": 0})
    r2 = client.get("/api/indicators/search", params={"limit": 101})

    assert r1.status_code == 400
    assert r2.status_code == 400
    assert r1.json()["detail"] == "Invalid request parameters"
    assert r2.json()["detail"] == "Invalid request parameters"


def test_search_indicators_invalid_campaign_uuid(client):
    """GET /api/indicators/search?campaign=not-a-uuid returns 400."""
    response = client.get("/api/indicators/search", params={"campaign": "not-a-uuid"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_search_indicators_empty(client_with_memory_db):
    """GET /api/indicators/search returns 200 with empty data when no indicators exist."""
    client, _ = client_with_memory_db

    response = client.get("/api/indicators/search")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total_pages"] == 0


def test_search_indicators_returns_seeded(client_with_memory_db):
    """GET /api/indicators/search returns 200 with seeded indicators and pagination."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get("/api/indicators/search")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # main + related indicator
    assert len(data["data"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total_pages"] == 1
    ids = {item["id"] for item in data["data"]}
    assert INDICATOR_ID in ids
    assert "22222222-2222-2222-2222-222222222222" in ids
    # Item linked to campaign has counts
    main = next(i for i in data["data"] if i["id"] == INDICATOR_ID)
    assert main["type"] == "ip"
    assert main["value"] == "192.168.1.1"
    assert main["campaign_count"] == 1
    assert main["threat_actor_count"] == 1


def test_search_indicators_filter_by_type(client_with_memory_db):
    """GET /api/indicators/search?type=ip returns only ip indicators."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get("/api/indicators/search", params={"type": "ip"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["data"]) == 1
    assert data["data"][0]["type"] == "ip"
    assert data["data"][0]["id"] == INDICATOR_ID


def test_search_indicators_filter_by_value(client_with_memory_db):
    """GET /api/indicators/search?value=... returns indicators with matching value (substring)."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get("/api/indicators/search", params={"value": "192.168"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["value"] == "192.168.1.1"


def test_search_indicators_filter_by_campaign(client_with_memory_db):
    """GET /api/indicators/search?campaign=... returns indicators linked to that campaign."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get("/api/indicators/search", params={"campaign": CAMPAIGN_ID})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1  # only main indicator is in the campaign
    assert data["data"][0]["id"] == INDICATOR_ID


def test_search_indicators_filter_by_threat_actor(client_with_memory_db):
    """GET /api/indicators/search?threat_actor=... returns indicators in campaigns with that actor."""
    client, session = client_with_memory_db
    seed_indicator_details_fixtures(session)

    response = client.get("/api/indicators/search", params={"threat_actor": THREAT_ACTOR_ID})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["id"] == INDICATOR_ID
