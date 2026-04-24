from datetime import datetime, timedelta, timezone

import jwt
import pytest

from gss_archetype_service.auth import ALGORITHM, SECRET


def test_health_is_public(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert isinstance(body["rows_loaded"], int)


def test_archetypes_happy_path(client, auth_headers):
    r = client.get("/archetypes", params={"k": 3}, headers=auth_headers)
    assert r.status_code == 200
    archs = r.json()
    assert len(archs) == 3
    required = {"size", "share", "age", "educ", "polviews", "partyid", "attend", "happy",
                "sex", "race", "marital", "relig"}
    assert required.issubset(archs[0].keys())


@pytest.mark.parametrize("k", [0, -1, "abc"])
def test_archetypes_rejects_invalid_k(client, auth_headers, k):
    r = client.get("/archetypes", params={"k": k}, headers=auth_headers)
    assert r.status_code == 422


def test_archetypes_k_exceeds_rows_returns_400(client, auth_headers):
    r = client.get("/archetypes", params={"k": 10_000}, headers=auth_headers)
    assert r.status_code == 400


def test_archetypes_rejects_min_year_below_1972(client, auth_headers):
    r = client.get("/archetypes", params={"k": 3, "min_year": 1800}, headers=auth_headers)
    assert r.status_code == 422


def test_openapi_exposes_archetype_schema(client):
    schema = client.get("/openapi.json").json()
    archetype = schema["components"]["schemas"]["Archetype"]
    assert "polviews" in archetype["properties"]
    assert archetype["properties"]["polviews"]["minimum"] == 1.0
    assert archetype["properties"]["polviews"]["maximum"] == 7.0


def test_archetypes_requires_bearer_token(client):
    r = client.get("/archetypes", params={"k": 3})
    assert r.status_code == 401


def test_archetypes_rejects_malformed_token(client):
    r = client.get(
        "/archetypes",
        params={"k": 3},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert r.status_code == 401


def test_archetypes_rejects_expired_token(client):
    expired = jwt.encode(
        {"sub": "x", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET,
        algorithm=ALGORITHM,
    )
    r = client.get(
        "/archetypes",
        params={"k": 3},
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert r.status_code == 401


def test_archetypes_rejects_wrong_signature(client):
    forged = jwt.encode({"sub": "attacker"}, "a" * 32, algorithm=ALGORITHM)
    r = client.get(
        "/archetypes",
        params={"k": 3},
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert r.status_code == 401


def test_auth_token_issues_valid_jwt(client):
    r = client.post("/auth/token", json={"username": "alice"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    claims = jwt.decode(body["access_token"], SECRET, algorithms=[ALGORITHM])
    assert claims["sub"] == "alice"


def test_issued_token_is_accepted_by_archetypes(client):
    r = client.post("/auth/token", json={"username": "alice"})
    token = r.json()["access_token"]
    r = client.get(
        "/archetypes",
        params={"k": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
