"""Tests for profile routes."""
import json


def _auth_header(client, email="prof@example.com"):
    client.post("/api/auth/register", json={"email": email, "password": "password123", "name": "Prof User"})
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = json.loads(res.data)["token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_not_found(client):
    headers = _auth_header(client, "noprof@example.com")
    res = client.get("/api/profile", headers=headers)
    assert res.status_code == 404


def test_create_profile(client):
    headers = _auth_header(client, "createprof@example.com")
    res = client.post("/api/profile", headers=headers, json={
        "age": 30,
        "gender": "female",
        "weight_kg": 65.0,
        "height_cm": 165.0,
        "health_conditions": ["Diabetes"],
        "allergies": ["gluten"],
        "diet_preference": "vegetarian",
        "goals": ["Manage Diabetes"],
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["profile"]["age"] == 30
    assert data["profile"]["bmi"] is not None
    assert "Diabetes" in data["profile"]["health_conditions"]


def test_get_profile_after_create(client):
    headers = _auth_header(client, "getprof@example.com")
    client.post("/api/profile", headers=headers, json={"age": 25, "gender": "male"})
    res = client.get("/api/profile", headers=headers)
    assert res.status_code == 200
    assert json.loads(res.data)["age"] == 25


def test_profile_invalid_age(client):
    headers = _auth_header(client, "invage@example.com")
    res = client.post("/api/profile", headers=headers, json={"age": -5})
    assert res.status_code == 422


def test_profile_invalid_diet(client):
    headers = _auth_header(client, "invdiet@example.com")
    res = client.post("/api/profile", headers=headers, json={"diet_preference": "carnivore-extreme"})
    assert res.status_code == 422
