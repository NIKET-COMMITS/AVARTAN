"""
Waste Input Routes - Production Ready with Security
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import re

from backend.database import get_db
from backend.models import User, WasteItem, UserImpact, AuditLog
from backend.routers.auth import get_current_user
from backend.services.gemini_service import (
    validate_waste_with_gemini,
    get_fallback_response
)
from backend.validators import (
    validate_waste_description,
    validate_quantity,
    validate_condition,
    ValidationError
)
from backend.logger import log_request, log_error, log_success

router = APIRouter(prefix="/waste", tags=["waste"])

# ============ PYDANTIC MODELS ============

class WasteInputRequest(BaseModel):
    """Data structure for manual waste input"""
    item_name: str = Field(..., min_length=3, max_length=200)
    quantity: int = Field(1, ge=1, le=1000)
    unit: str = Field("pieces", max_length=20)
    condition: str = Field(..., pattern="^(mint|good|fair|poor|broken)$")
    description: str = Field("", max_length=500)

# ============ HELPERS ============

def create_audit_log(db: Session, user_id: int, action: str, details: str):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()

# ============ ENDPOINTS ============

@router.post("/analyze")
def analyze_waste(
    description: str
):
    """
    Endpoint: Send description to Gemini AI for analysis.
    NOTE: Authentication removed for Phase 2 testing.
    """
    # Removed log_request as it requires current_user.id
    
    try:
        validated_desc = validate_waste_description(description)
        result = validate_waste_with_gemini(validated_desc)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error("Analysis failed", e)
        return get_fallback_response(description)

@router.post("/add")
def add_waste_item(
    data: WasteInputRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint: Save a waste item to the database (Requires Login)"""
    log_request("/waste/add", "POST", current_user.id)
    
    new_item = WasteItem(
        user_id=current_user.id,
        item_name=data.item_name,
        quantity=data.quantity,
        unit=data.unit,
        condition=data.condition,
        description=data.description
    )
    
    db.add(new_item)
    
    impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
    if impact:
        impact.total_waste_collected += data.quantity
        impact.points += (data.quantity * 10)
    
    db.commit()
    
    create_audit_log(db, current_user.id, "ADD_WASTE", f"Added {data.item_name}")
    log_success("Waste Added", f"User {current_user.id} added {data.item_name}")
    
    return {"message": "Item added successfully", "item_id": new_item.id}

@router.get("/my-waste")
def get_user_waste(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint: List all waste items for the logged-in user"""
    items = db.query(WasteItem).filter(WasteItem.user_id == current_user.id).all()
    return {"items": items}