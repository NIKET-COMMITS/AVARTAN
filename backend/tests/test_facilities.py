from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_nearby_facilities():
    """Test if the facility matching engine works and calculates distance"""
    response = client.get("/facilities/nearby?latitude=23.1815&longitude=72.6369&material=Metal")
    
    assert response.status_code == 200
    json_response = response.json()
    
    # Check our professional dictionary wrapper
    assert json_response.get("success") is True
    facilities = json_response.get("data", [])
    
    # Now check the actual list of facilities
    assert isinstance(facilities, list)
    
    if len(facilities) > 0:
        facility = facilities[0]
        assert "name" in facility
        assert "distance_km" in facility
        # Verify our sorting logic worked (closest should be first)
        if len(facilities) > 1:
            assert facilities[0]["distance_km"] <= facilities[1]["distance_km"]