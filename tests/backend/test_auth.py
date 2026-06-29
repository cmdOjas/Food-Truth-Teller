"""Tests for authentication routes."""
import json


def _register(client, email="test@example.com", password="password123", name="Test User"):
    return client.post("/api/auth/register", json={"email": email, "password": password, "name": name})


def test_register_success(client):
    res = _register(client)
    assert res.status_code == 201
    data = json.loads(res.data)
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"


def test_register_duplicate_email(client):
    _register(client, email="dup@example.com")
    res = _register(client, email="dup@example.com")
    assert res.status_code == 409


def test_register_invalid_email(client):
    res = _register(client, email="not-an-email")
    assert res.status_code == 422


def test_register_short_password(client):
    res = _register(client, password="123")
    assert res.status_code == 422


def test_login_success(client):
    _register(client, email="login@example.com")
    res = client.post("/api/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "token" in json.loads(res.data)


def test_login_wrong_password(client):
    _register(client, email="wrong@example.com")
    res = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"})
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})
    assert res.status_code == 401


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_token(client):
    reg_res = _register(client, email="me@example.com")
    token = json.loads(reg_res.data)["token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert json.loads(res.data)["email"] == "me@example.com"
