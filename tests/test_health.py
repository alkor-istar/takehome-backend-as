def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


# Test rate limit enforcement
def test_rate_limit_enforced(client):
    # Exhaust the limit (10 requests per minute)
    for _ in range(9):
        res = client.get("/api/health")
        assert res.status_code == 200
    # Next request should be rate limited
    res = client.get("/api/health")
    assert res.status_code == 429
