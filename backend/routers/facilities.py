from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Facility, FacilityReview, User
from backend.routers.auth import get_current_user
from backend.services.location_service import location_service

router = APIRouter(prefix="/facilities", tags=["Facilities"])

# Pydantic schema for creating a review
class ReviewCreate(BaseModel):
    overall_rating: float
    title: Optional[str] = None
    text: Optional[str] = None

@router.get("/nearby")
async def get_nearby_facilities(
    lat: float = Query(23.2156, description="User Latitude (Default: Gandhinagar Center)"),
    lon: float = Query(72.6369, description="User Longitude (Default: Gandhinagar Center)"),
    material: str = Query("plastic", description="Material to recycle")
):
    """
    Finds the top 3 best facilities within 25km based on simulated real GPS distance and operating hours.
    """
    facilities = location_service.find_best_facilities(
        user_lat=lat, 
        user_lon=lon, 
        material=material, 
        max_radius_km=25.0
    )
    
    return {
        "success": True,
        "data": facilities,
        "message": f"Found {len(facilities)} facilities near you accepting {material}."
    }

@router.post("/{facility_id}/reviews")
def add_facility_review(
    facility_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows authenticated users to leave reviews for facilities."""
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
        
    new_review = FacilityReview(
        facility_id=facility_id,
        user_id=current_user.id,
        overall_rating=review.overall_rating,
        title=review.title,
        text=review.text
    )
    
    # Update facility average rating mathematically
    total_rating = (facility.rating * facility.total_reviews) + review.overall_rating
    facility.total_reviews += 1
    facility.rating = round(total_rating / facility.total_reviews, 1)
    
    db.add(new_review)
    db.commit()
    
    return {"success": True, "message": "Review added successfully"}