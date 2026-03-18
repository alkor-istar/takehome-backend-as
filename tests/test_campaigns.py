"""Tests for campaigns API."""

import uuid

from tests.mocks.campaign_fixtures import (
    CAMPAIGN_ID,
    INDICATOR_DOMAIN_ID,
    INDICATOR_IP_ID,
    OBSERVED_DAY,
    OBSERVED_DAY_2,
    seed_campaign_fixtures,
)


def test_get_campaign_indicators(client_with_memory_db):
    """GET /api/campaigns/{id}/indicators returns 200 with campaign, timeline, and summary."""
    client, session = client_with_memory_db
    seed_campaign_fixtures(session)

    response = client.get(f"/api/campaigns/{CAMPAIGN_ID}/indicators")

    assert response.status_code == 200
    data = response.json()
    assert data["campaign"]["id"] == CAMPAIGN_ID
    assert data["campaign"]["name"] == "Campaign Fixture"
    assert data["campaign"]["status"] == "active"
    assert data["summary"]["total_indicators"] == 2
    assert data["summary"]["unique_ips"] == 1
    assert data["summary"]["unique_domains"] == 1
    assert len(data["timeline"]) >= 1
    period = data["timeline"][0]
    assert "period" in period
    assert "indicators" in period
    assert "counts" in period
    ids = {i["id"] for i in period["indicators"]}
    assert INDICATOR_IP_ID in ids
    assert INDICATOR_DOMAIN_ID in ids
    assert period["counts"].get("ip") == 1
    assert period["counts"].get("domain") == 1


def test_get_campaign_indicators_not_found(client_with_memory_db):
    """GET /api/campaigns/{id}/indicators returns 404 when campaign does not exist."""
    client, _ = client_with_memory_db
    unknown_id = uuid.uuid4()

    response = client.get(f"/api/campaigns/{unknown_id}/indicators")

    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"


def test_get_campaign_indicators_invalid_uuid(client):
    """GET /api/campaigns/{id}/indicators returns 400 when campaign_id is not a valid UUID."""
    response = client.get("/api/campaigns/not-a-uuid/indicators")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_get_campaign_indicators_invalid_group_by(client):
    """GET /api/campaigns/{id}/indicators?group_by=invalid returns 400."""
    response = client.get(
        "/api/campaigns/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/indicators",
        params={"group_by": "month"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_get_campaign_indicators_invalid_date(client):
    """GET /api/campaigns/{id}/indicators?start_date=invalid returns 400."""
    response = client.get(
        "/api/campaigns/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/indicators",
        params={"start_date": "not-a-date"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid request parameters"
    assert "errors" in data


def test_get_campaign_indicators_group_by_week(client_with_memory_db):
    """GET /api/campaigns/{id}/indicators?group_by=week returns timeline with week periods."""
    client, session = client_with_memory_db
    seed_campaign_fixtures(session)

    response = client.get(
        f"/api/campaigns/{CAMPAIGN_ID}/indicators",
        params={"group_by": "week"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["timeline"]) >= 1
    assert "W" in data["timeline"][0]["period"]  # e.g. 2024-W28


def test_get_campaign_indicators_date_filter(client_with_memory_db):
    """GET /api/campaigns/{id}/indicators with start_date/end_date filters by observed_at."""
    client, session = client_with_memory_db
    seed_campaign_fixtures(session)

    # Range that includes both observed_at times
    response = client.get(
        f"/api/campaigns/{CAMPAIGN_ID}/indicators",
        params={
            "start_date": OBSERVED_DAY.isoformat(),
            "end_date": OBSERVED_DAY_2.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_indicators"] == 2
