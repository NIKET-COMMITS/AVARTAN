from fastapi import APIRouter
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/predictions", tags=["ML Predictions (Phase 4)"])

@router.get("/facility")
def predict_facility(distance_km: float, rating: float = 4.0, material_match_pct: float = 80.0, eco_preference: float = 0.5):
    """Uses the RandomForest Classifier to predict which facility you will choose."""
    fac_id, conf = ml_service.predict_facility(distance_km, rating, material_match_pct, eco_preference)
    return {"success": True, "predicted_facility_id": fac_id, "confidence": conf}

@router.get("/value")
def predict_value(material: str, condition: str, weight_grams: float):
    """Uses Linear Regression to estimate the exact Rupee value of the waste."""
    value = ml_service.predict_value(material, condition, weight_grams)
    return {"success": True, "estimated_value_rupees": value}