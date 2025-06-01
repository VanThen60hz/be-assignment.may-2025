# Test user-related functionality

from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "created_at" in data


def test_list_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user():
    # First create a user
    create_response = client.post(
        "/api/v1/users/",
        json={"email": "get@example.com", "name": "Get User"}
    )
    user_id = create_response.json()["id"]

    # Then get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "get@example.com"
    assert data["name"] == "Get User"
