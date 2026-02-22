"""
Automated tests for the AssuranceAI API.

These run in CI (GitHub Actions) on every push to make sure
nothing is broken. They test:
  1. Health endpoint responds
  2. Public endpoints work (bundles, form-schema)
  3. Auth works (register, login, me)
  4. Prediction works with a valid token
  5. Cache is working
  6. Admin endpoints are protected
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    from backend.api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def user_token(client):
    """Register a test user and return the JWT token."""
    import time
    email = f"testuser_{int(time.time())}@test.com"
    res = client.post("/api/auth/register", json={
        "email": email,
        "full_name": "Test User",
        "password": "testpass123",
    })
    assert res.status_code == 200
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def admin_token(client):
    """Login as the seeded admin and return the JWT token."""
    res = client.post("/api/auth/login", json={
        "email": "admin@assuranceai.com",
        "password": "admin123",
    })
    assert res.status_code == 200
    return res.json()["access_token"]


# ── 1. Health ──────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AssuranceAI"


# ── 2. Public endpoints ───────────────────────────────────────────────────

def test_bundles(client):
    res = client.get("/api/bundles")
    assert res.status_code == 200
    bundles = res.json()["bundles"]
    assert len(bundles) == 10
    # Each bundle should have an id, name, category
    for b in bundles:
        assert "id" in b
        assert "name" in b
        assert "category" in b


def test_form_schema(client):
    res = client.get("/api/form-schema")
    assert res.status_code == 200
    sections = res.json()["sections"]
    assert "demographics" in sections
    assert "history" in sections
    assert "policy" in sections
    assert "sales" in sections
    assert "timeline" in sections


# ── 3. Auth ────────────────────────────────────────────────────────────────

def test_register_duplicate(client, user_token):
    """Registering the same email twice should fail."""
    # user_token fixture already registered; try re-registering
    # We'll use a new email to avoid depending on fixture internals
    import time
    email = f"dup_{int(time.time())}@test.com"
    res1 = client.post("/api/auth/register", json={
        "email": email, "full_name": "Dup", "password": "pass123",
    })
    assert res1.status_code == 200
    res2 = client.post("/api/auth/register", json={
        "email": email, "full_name": "Dup", "password": "pass123",
    })
    assert res2.status_code == 400


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@assuranceai.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


def test_me_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code in (401, 403)


def test_me_with_token(client, user_token):
    res = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {user_token}",
    })
    assert res.status_code == 200
    data = res.json()
    assert "email" in data
    assert data["role"] == "user"


# ── 4. Prediction ─────────────────────────────────────────────────────────

SAMPLE_INPUT = {
    "Adult_Dependents": 1,
    "Child_Dependents": 2,
    "Infant_Dependents": 0,
    "Estimated_Annual_Income": 65000,
    "Employment_Status": "Employed",
    "Region_Code": 3,
    "Existing_Policyholder": "Yes",
    "Previous_Claims_Filed": 0,
    "Years_Without_Claims": 5,
    "Previous_Policy_Duration_Months": 12,
    "Policy_Cancelled_Post_Purchase": "No",
    "Deductible_Tier": 2,
    "Payment_Schedule": "Monthly",
    "Vehicles_on_Policy": 1,
    "Custom_Riders_Requested": 0,
    "Grace_Period_Extensions": 0,
    "Days_Since_Quote": 5,
    "Underwriting_Processing_Days": 3,
    "Policy_Amendments_Count": 0,
    "Acquisition_Channel": "Online",
    "Broker_Agency_Type": "Large",
    "Broker_ID": 9,
    "Employer_ID": 174,
    "Policy_Start_Year": 2024,
    "Policy_Start_Month": "January",
    "Policy_Start_Week": 1,
    "Policy_Start_Day": 10,
}


def test_predict_without_auth(client):
    res = client.post("/api/predict", json=SAMPLE_INPUT)
    assert res.status_code in (401, 403)


def test_predict_with_auth(client, user_token):
    res = client.post("/api/predict", json=SAMPLE_INPUT, headers={
        "Authorization": f"Bearer {user_token}",
    })
    assert res.status_code == 200
    data = res.json()
    assert "predicted_bundle_id" in data
    assert "predicted_bundle_name" in data
    assert "confidence_scores" in data
    assert data["predicted_bundle_id"] in range(10)


# ── 5. Cache ───────────────────────────────────────────────────────────────

def test_cache_stats(client):
    res = client.get("/api/cache/stats")
    assert res.status_code == 200
    data = res.json()
    assert "hits" in data
    assert "misses" in data
    assert "size" in data


def test_cache_hit(client, user_token):
    """Second identical prediction should come from cache."""
    headers = {"Authorization": f"Bearer {user_token}"}
    # First request (miss)
    client.post("/api/predict", json=SAMPLE_INPUT, headers=headers)
    stats_before = client.get("/api/cache/stats").json()
    # Second request (should be hit)
    client.post("/api/predict", json=SAMPLE_INPUT, headers=headers)
    stats_after = client.get("/api/cache/stats").json()
    assert stats_after["hits"] > stats_before["hits"]


# ── 6. Admin protection ───────────────────────────────────────────────────

def test_admin_stats_without_token(client):
    res = client.get("/api/admin/stats")
    assert res.status_code in (401, 403)


def test_admin_stats_as_user(client, user_token):
    res = client.get("/api/admin/stats", headers={
        "Authorization": f"Bearer {user_token}",
    })
    assert res.status_code == 403


def test_admin_stats_as_admin(client, admin_token):
    res = client.get("/api/admin/stats", headers={
        "Authorization": f"Bearer {admin_token}",
    })
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "total_predictions" in data
