from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from backend.database import get_db
from backend.models import User, UserImpact
from backend.routers.auth import get_current_user

logger = logging.getLogger("avartan")
router = APIRouter(prefix="/profile", tags=["Profile"])

class ProfileUpdate(BaseModel):
    name: str = ""

def _build_profile_payload(current_user: User, db: Session):
    impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
    
    # Safely construct the badges array
    badges = []
    if impact:
        if getattr(impact, 'green_warrior', 0) > 0:
            badges.append("Green Warrior")
        if getattr(impact, 'serial_recycler', 0) > 0:
            badges.append("Serial Recycler")
        if getattr(impact, 'explorer', 0) > 0:
            badges.append("Explorer")

    return {
        "id": current_user.id,
        "name": current_user.name or "Eco Warrior",
        "email": current_user.email,
        "member_since": current_user.created_at.strftime("%B %Y") if current_user.created_at else "Recently",
        "impact": {
            "points": impact.points if impact else 0,
            "co2_saved": round(getattr(impact, 'total_co2_saved', 0.0), 2),
            "items_recycled": round(getattr(impact, 'total_waste_collected', 0.0), 2),
            "tier": getattr(impact, 'current_tier', "Bronze"),
            "badges": badges
        }
    }

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches the user profile securely."""
    try:
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

        user_data = _build_profile_payload(current_user, db)
        return {"success": True, "data": user_data}
    except Exception as e:
        logger.error(f"Profile / Fetch Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to fetch profile", "error": str(e)}
        )

@router.get("/me")
def get_profile_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches currently logged-in user profile via JWT."""
    try:
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

        user_data = _build_profile_payload(current_user, db)
        return {"success": True, "data": user_data}
    except Exception as e:
        logger.error(f"Profile /me Fetch Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Failed to fetch profile", "error": str(e)}
        )

@router.put("/")
def update_profile(
    profile_data: ProfileUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Updates user profile safely."""
    try:
        if profile_data.name:
            current_user.name = profile_data.name
            db.commit()
            db.refresh(current_user)
            
        return {
            "success": True, 
            "data": {"message": "Profile updated successfully", "name": current_user.name}
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Update failed", "error": str(e)}
        )