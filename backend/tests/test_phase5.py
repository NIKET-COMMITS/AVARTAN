"""
Tests for Phase 5: Dashboard & Analytics
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import User, RouteHistory, Facility
from backend.security import hash_password
from datetime import datetime, timedelta

client = TestClient(app)


@pytest.fixture
def setup_test_user():
    """Create test user"""
    db = SessionLocal()
    
    user = User(
        email="dashboard_test@test.com",
        password_hash=hash_password("test123"),
        name="Dashboard Test User",
        latitude=23.1815,
        longitude=72.6313
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user
    
    db.delete(user)
    db.commit()
    db.close()


def test_dashboard_metrics(setup_test_user):
    """Test dashboard metrics endpoint"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get metrics
    response = client.get("/dashboard/metrics", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    assert "total_routes" in data["data"]


def test_dashboard_leaderboards(setup_test_user):
    """Test leaderboard endpoint"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get leaderboards
    response = client.get("/dashboard/leaderboards", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data


def test_dashboard_achievements(setup_test_user):
    """Test achievements endpoint"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get achievements
    response = client.get("/dashboard/achievements", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data


def test_dashboard_community(setup_test_user):
    """Test community stats endpoint"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get community stats
    response = client.get("/dashboard/community", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data


def test_export_csv(setup_test_user):
    """Test CSV export"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Export CSV
    response = client.get("/reports/export/csv?period=monthly", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data


def test_generate_pdf(setup_test_user):
    """Test PDF generation"""
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": setup_test_user.email,
            "password": "test123"
        }
    )
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generate PDF
    response = client.get("/reports/generate/pdf?period=monthly", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data