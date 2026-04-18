import pytest
from backend.models import Facility

def get_auth_headers(client):
    test_email = "fac_tester@avartan.com"
    test_pass = "SecurePass123!"
    client.post("/auth/register", json={"name": "Rev", "email": test_email, "password": test_pass})
    response = client.post("/auth/login", data={"username": test_email, "password": test_pass})
    data = response.json().get("data", response.json())
    token = data.get("access_token", "")
    return {"Authorization": f"Bearer {token}"}

def test_get_nearby_facilities(client):
    response = client.get("/facilities/nearby?lat=23.2156&lon=72.6369&material=plastic")
    assert response.status_code == 200

def test_add_facility_review_success(client, db_session):
    facility = Facility(name="Eco Plant", address="Road", latitude=23.0, longitude=72.0, rating=0.0, total_reviews=0)
    db_session.add(facility)
    db_session.commit()
    headers = get_auth_headers(client)
    response = client.post(f"/facilities/{facility.id}/reviews", json={"overall_rating": 5.0, "title": "Great", "text": "Clean!"}, headers=headers)
    assert response.status_code == 200

def test_add_facility_review_unauthorized(client, db_session):
    facility = Facility(name="Strict Plant", address="Road", latitude=23.0, longitude=72.0)
    db_session.add(facility)
    db_session.commit()
    response = client.post(f"/facilities/{facility.id}/reviews", json={"overall_rating": 5.0, "text": "Hacker"})
    assert response.status_code == 401

def test_add_review_facility_not_found(client):
    headers = get_auth_headers(client)
    response = client.post("/facilities/99999/reviews", json={"overall_rating": 1.0, "text": "Ghost"}, headers=headers)
    assert response.status_code == 404
