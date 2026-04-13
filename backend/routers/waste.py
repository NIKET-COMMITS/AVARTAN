"""
Waste Input Routes - Phase 2 Final (Demo Optimized)
Enhanced with Impact Calculation and Data Integrity
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional

from backend.database import get_db
from backend.models import WasteItem, UserImpact
from backend.services.gemini_service import (
    validate_waste_with_gemini,
    get_fallback_response
)
from backend.logger import log_error, log_success

router = APIRouter(prefix="/waste", tags=["waste"])

# ============ PYDANTIC MODELS ============

class WasteInputRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=200)
    quantity: float = Field(1.0, ge=0.1)
    unit: str = Field("kg", max_length=20)
    condition: str = Field("fair")
    description: Optional[str] = ""

# ============ ENDPOINTS ============

@router.post("/analyze")
async def analyze_waste(
    description: Optional[str] = None, 
    payload: dict = Body(None)
):
    """Handles both URL params and JSON body for AI analysis."""
    input_text = description or (payload.get("description") if payload else None)
    
    if not input_text:
        raise HTTPException(status_code=400, detail="Description required")

    try:
        result = validate_waste_with_gemini(input_text)
        return result
    except Exception as e:
        log_error("AI Analysis failed", e)
        return get_fallback_response(input_text)

@router.post("/add")
def add_waste_item(
    data: WasteInputRequest,
    db: Session = Depends(get_db)
):
    """Saves item and updates the demo user's global impact stats."""
    DEMO_USER_ID = 1 
    
    try:
        # 1. Create the new item
        new_item = WasteItem(
            user_id=DEMO_USER_ID,
            item_name=data.item_name,
            quantity=data.quantity,
            unit=data.unit,
            condition=data.condition,
            description=data.description
        )
        db.add(new_item)
        
        # 2. Update or Create User Impact
        impact = db.query(UserImpact).filter(UserImpact.user_id == DEMO_USER_ID).first()
        if not impact:
            impact = UserImpact(user_id=DEMO_USER_ID, total_waste_collected=0, points=0)
            db.add(impact)
        
        # Logic: Update the stats that drive the Dashboard
        impact.total_waste_collected += data.quantity
        # Demo Logic: 100 points per item + 10 points per kg
        impact.points += int(100 + (data.quantity * 10)) 
        
        db.commit()
        db.refresh(new_item)
        
        log_success("Data Saved", f"User {DEMO_USER_ID} added {data.item_name}")
        return {
            "success": True, 
            "message": "Impact recorded!", 
            "item_id": new_item.id,
            "new_total_points": impact.points
        }
    
    except Exception as e:
        db.rollback()
        log_error("Database Error", e)
        raise HTTPException(status_code=500, detail="Failed to save data")

@router.get("/my-waste")
def get_user_waste(db: Session = Depends(get_db)):
    """
    Returns the user's waste history PLUS summarized metrics 
    for the top-level Dashboard cards.
    """
    DEMO_USER_ID = 1
    
    # 1. Fetch Items
    items = db.query(WasteItem).filter(WasteItem.user_id == DEMO_USER_ID).order_by(WasteItem.id.desc()).all()
    
    # 2. Calculate Aggregates for the UI Stats
    total_items = len(items)
    # Assuming standard CO2 saved per item is tracked in a real app, 
    # here we simulate it for the demo cards based on quantity.
    estimated_total_co2 = sum([item.quantity * 2.5 for item in items]) 
    
    return {
        "success": True,
        "data": {
            "items": items,
            "summary": {
                "total_count": total_items,
                "total_co2_saved": round(estimated_total_co2, 2),
                "demo_user_id": DEMO_USER_ID
            }
        }
    }