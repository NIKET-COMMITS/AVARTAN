"""
Profile Router - Enterprise Grade
Features: JWT Data Extraction, Profile Updates
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from backend.database import get_db
from backend.models import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileUpdateRequest(BaseModel):
    name: str

@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "joined_at": current_user.created_at if hasattr(current_user, 'created_at') else None
        }
    }

@router.put("/update")
def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows user to update their display name securely."""
    try:
        current_user.name = data.name
        db.commit()
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update profile")