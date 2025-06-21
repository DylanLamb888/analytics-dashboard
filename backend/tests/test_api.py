"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import create_access_token

client = TestClient(app)


def get_auth_headers(role="admin"):
    """Get authorization headers for testing."""
    token = create_access_token(data={"sub": f"{role}@test.com", "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success():
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_failure():
    """Test failed login with wrong credentials."""
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_upload_requires_auth():
    """Test that upload endpoint requires authentication."""
    response = client.post("/api/upload/csv")
    assert response.status_code == 403  # No auth header


def test_orders_requires_auth():
    """Test that orders endpoint requires authentication."""
    response = client.get("/api/orders")
    assert response.status_code == 403


def test_metrics_with_auth():
    """Test metrics endpoint with authentication."""
    headers = get_auth_headers("viewer")
    response = client.get("/api/metrics/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "sales_metrics" in data
    assert "top_products" in data
    assert "time_series" in data
    assert "geographic_distribution" in data