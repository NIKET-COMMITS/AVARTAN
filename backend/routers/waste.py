"""
Waste Management Router - AI Vision & Location Integrated
Features: Image Analysis, Facility Matching, and Atomic Impact Calculation
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.database import get_db
from backend.models import WasteItem, UserImpact, User, Facility
from backend.routers.auth import get_current_user
from backend.services.gemini_service import gemini_service
from backend.logger import log_error, log_success

router = APIRouter(prefix="/waste", tags=["waste-management"])

# ============ PYDANTIC MODELS ============

class WasteInputRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=100)
    quantity_grams: float = Field(..., ge=1)
    item_type: str = Field(...)
    condition: str = Field(...)
    verification_payload: Optional[str] = "{}"

# ============ ENDPOINTS ============

@router.post("/analyze")
async def analyze_waste_advanced(
    file: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handles image upload (multipart/form-data) or text input for AI analysis.
    """
    if not file and not description:
        raise HTTPException(status_code=400, detail="Please provide an image or a description.")

    try:
        image_bytes = await file.read() if file else None
        ai_response = await gemini_service.analyze_waste(
            text_input=description, 
            image_bytes=image_bytes
        )

        ai_data = ai_response["data"] if ai_response.get("success") else gemini_service.get_fallback(
            description or "Scanned Waste Item"
        )

        detected_material = str(ai_data.get("material", "")).strip().lower()
        all_open_facilities = db.query(Facility).filter(Facility.is_open == True).all()

        filtered_facilities = []
        for facility in all_open_facilities:
            materials = facility.materials_accepted or []
            if isinstance(materials, str):
                materials = [materials]
            normalized = {str(material).strip().lower() for material in materials}
            if detected_material in normalized or "mixed" in normalized or "other" in normalized:
                filtered_facilities.append(facility)

        top_facilities = filtered_facilities[:5]
        return {
            "analysis": ai_data,
            "facilities": [
                {
                    "id": facility.id,
                    "name": facility.name,
                    "address": facility.address,
                    "city": facility.city,
                    "rating": facility.rating,
                    "materials_accepted": facility.materials_accepted or [],
                }
                for facility in top_facilities
            ],
        }

    except Exception as e:
        log_error(f"Analysis Failure: {str(e)}")
        return {
            "analysis": gemini_service.get_fallback(description or "Unknown Item"),
            "facilities": [],
        }

@router.post("/add", status_code=status.HTTP_201_CREATED)
def submit_verified_waste(
    data: WasteInputRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves verified waste and updates user impact.
    """
    try:
        # Convert grams to KG for database consistency
        qty_kg = data.quantity_grams / 1000

        new_item = WasteItem(
            user_id=current_user.id,
            item_name=data.item_name,
            quantity=qty_kg,
            unit="kg",
            condition=data.condition,
            description=f"AI Verified. Material: {data.item_type}"
        )
        db.add(new_item)

        # Impact Math
        co2_multipliers = {"Metal": 8.5, "Plastic": 1.2, "Electronics": 15.0, "Paper": 0.8}
        multiplier = co2_multipliers.get(data.item_type, 0.5)
        co2_val = qty_kg * multiplier
        points = int(100 * qty_kg * multiplier)

        impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
        if not impact:
            impact = UserImpact(user_id=current_user.id, points=0, total_waste_collected=0, total_co2_saved=0)
            db.add(impact)

        impact.points += points
        impact.total_waste_collected += qty_kg
        impact.total_co2_saved += co2_val

        db.commit()
        return {"success": True, "points_earned": points}

    except Exception as e:
        db.rollback()
        log_error("Add Waste Error", e)
        raise HTTPException(status_code=500, detail="Database Error")