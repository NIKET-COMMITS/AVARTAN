import pytest
import time

def generate_test_email():
    return f"tester_{int(time.time())}@avartan.com"

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    # Automatically adapts to both old and new backend formats
    assert response.json().get("data", response.json()).get("status") == "ok"

def test_register_success(client):
    email = generate_test_email()
    response = client.post("/auth/register", json={"name": "Test", "email": email, "password": "SecurePassword123!"})
    assert response.status_code in [200, 201]

def test_register_duplicate_email(client):
    email = generate_test_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "SecurePassword123!"})
    response = client.post("/auth/register", json={"name": "Dup", "email": email, "password": "AnotherPassword456!"})
    assert response.status_code == 400

def test_login_success(client):
    email = generate_test_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "SecurePassword123!"})
    response = client.post("/auth/login", data={"username": email, "password": "SecurePassword123!"})
    assert response.status_code == 200
    # Automatically adapts to both old and new backend formats
    assert "access_token" in response.json().get("data", response.json())

def test_login_wrong_password(client):
    email = generate_test_email()
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "SecurePassword123!"})
    response = client.post("/auth/login", data={"username": email, "password": "WrongPassword123!"})
    assert response.status_code == 401