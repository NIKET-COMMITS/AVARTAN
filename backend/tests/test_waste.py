from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)

# We patch the EXACT function name from your gemini_service.py
@patch("backend.services.gemini_service.validate_waste_with_gemini")
def test_analyze_waste_text(mock_analyze):
    """Test the waste analysis endpoint using a mocked AI response"""
    
    # Simulate the exact JSON structure your Gemini prompt demands
    mock_analyze.return_value = {
        "success": True,
        "data": {
            "item_name": "Broken Smartphone",
            "item_type": "Electronics",
            "condition": "broken",
            "confidence": 0.98,
            "materials": { "primary_material": 100 },
            "total_weight_grams": 200,
            "estimated_value_rupees": 500,
            "estimated_co2_saved_kg": 1.2
        }
    }
    
    # FIXED: Using params={"description": ...} because your FastAPI route 
    # expects it in the URL query, not in a JSON body!
    response = client.post(
        "/waste/analyze",
        params={"description": "I have a broken smartphone with a cracked screen."}
    )
    
    # If it fails, it will print out the exact error message
    assert response.status_code == 200, response.json()
    
    result = response.json()
    
    # If your API wraps the response in a "data" object, we check inside it
    # If your API wraps the response in a "data" object, we check inside it
    if "data" in result:
        # Just verify the AI returned the correct JSON structure!
        assert "item_type" in result["data"]
        assert "condition" in result["data"]
        assert "estimated_co2_saved_kg" in result["data"]
    else:
        # Otherwise, check the base level
        assert result["item_type"] == "Electronics"
        assert result["condition"] == "broken"