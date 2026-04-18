import pytest
import time

def generate_test_email():
    return f"tester_{int(time.time())}@avartan.com"

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_register_success(client):
    test_email = generate_test_email()
    response = client.post("/auth/register", json={"name": "Test User", "email": test_email, "password": "SecurePassword123!"})
    assert response.status_code in [200, 201]

def test_register_duplicate_email(client):
    test_email = generate_test_email()
    client.post("/auth/register", json={"name": "First", "email": test_email, "password": "SecurePassword123!"})
    response = client.post("/auth/register", json={"name": "Dup", "email": test_email, "password": "AnotherPassword456!"})
    assert response.status_code == 400

def test_login_success(client):
    test_email = generate_test_email()
    client.post("/auth/register", json={"name": "Log", "email": test_email, "password": "SecurePassword123!"})
    response = client.post("/auth/login", data={"username": test_email, "password": "SecurePassword123!"})
    assert response.status_code == 200
    data = response.json().get("data", response.json())
    assert "access_token" in data

def test_login_wrong_password(client):
    test_email = generate_test_email()
    client.post("/auth/register", json={"name": "Log", "email": test_email, "password": "SecurePassword123!"})
    response = client.post("/auth/login", data={"username": test_email, "password": "WrongPassword123!"})
    assert response.status_code == 401
