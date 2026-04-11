from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Facility, FacilityReview, User
from backend.routers.auth import get_current_user
from backend.services.location_service import haversine_distance, rank_facilities
from pydantic import BaseModel

router = APIRouter(prefix="/facilities", tags=["Facilities"])

# Pydantic schema for creating a review
class ReviewCreate(BaseModel):
    overall_rating: float
    title: Optional[str] = None
    text: Optional[str] = None

@router.get("/nearby")
def get_nearby_facilities(
    latitude: float = Query(..., description="User's current latitude"),
    longitude: float = Query(..., description="User's current longitude"),
    material: Optional[str] = Query(None, description="Filter by material (e.g. Metal)"),
    max_distance_km: float = Query(25.0, description="Max search radius"),
    db: Session = Depends(get_db)
):
    """Finds and ranks recycling facilities near the user using Haversine math."""
    all_facilities = db.query(Facility).filter(Facility.is_open == True).all()
    
    nearby = []
    for fac in all_facilities:
        # 1. Filter by material if requested
        if material and material not in (fac.materials_accepted or []):
            continue
            
        # 2. Calculate distance
        dist = haversine_distance(latitude, longitude, fac.latitude, fac.longitude)
        
        # 3. Keep if within radius
        if dist <= max_distance_km:
            nearby.append({
                "facility": fac,
                "distance_km": dist
            })
            
    # Rank using our smart algorithm
    ranked = rank_facilities(nearby, max_distance_km)
    
    # Format for JSON response
    return {
        "success": True,
        "count": len(ranked),
        "data": [
            {
                "id": item["facility"].id,
                "name": item["facility"].name,
                "address": f"{item['facility'].city}, {item['facility'].pincode}",
                "distance_km": item["distance_km"],
                "score": item["score"],
                "rating": item["facility"].rating,
                "materials": item["facility"].materials_accepted,
                "phone": item["facility"].phone
            }
            for item in ranked
        ]
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