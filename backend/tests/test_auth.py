"""
TESTS FOR AUTHENTICATION

Tests all auth endpoints to verify they work.
"""

import pytest
import random
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test /health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_success():
    """Test successful registration with a dynamic email"""
    # 1. Generate a random number to ensure the email is always unique
    random_id = random.randint(1, 999999)
    test_email = f"newuser_{random_id}@example.com"
    
    # 2. Send the request
    response = client.post(
        "/auth/register",
        json={
            "email": test_email,
            "password": "TestPassword123!",
            "name": "Test User"
        }
    )
    
    # 3. Verify it worked
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["email"] == test_email  # Compares against our generated email


def test_register_duplicate_email():
    """Test registration with duplicate email"""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Pass123!",
            "name": "User 1"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Pass456!",
            "name": "User 2"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """Test successful login"""
    # Register first
    client.post(
        "/auth/register",
        json={
            "email": "logintest@example.com",
            "password": "LoginPass123!",
            "name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "LoginPass123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "WrongPassword"
        }
    )
    
    assert response.status_code == 401
    assert "credentials" in response.json()["detail"]


def test_logout():
    """Test logout with token"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "email": "logout@example.com",
            "password": "LogoutPass123!",
            "name": "Logout User"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "logout@example.com",
            "password": "LogoutPass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    
    assert response.status_code == 200
    assert "success" in response.json()["status"]


def test_forgot_password():
    """Test password reset request"""
    # Register user
    client.post(
        "/auth/register",
        json={
            "email": "forgot@example.com",
            "password": "ForgotPass123!",
            "name": "Forgot User"
        }
    )
    
    # Request password reset
    response = client.post(
        "/auth/forgot-password?email=forgot@example.com"
    )
    
    assert response.status_code == 200
    assert "message" in response.json()