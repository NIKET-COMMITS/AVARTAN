"""
Facilities & Map Router
Zero-Budget routing using OpenStreetMap-compatible coordinate math and AI scoring.
Includes Zero-Dependency In-Memory TTL Caching for high performance.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import time

from backend.database import get_db
from backend.models import Facility, FacilityReview, User
from backend.routers.auth import get_current_user
from backend.ai_engine import ai_engine

router = APIRouter(prefix="/facilities", tags=["Facilities"])

# --- IN-MEMORY CACHE SETUP ---
# Saves SQLite from being hammered by repetitive map queries
FACILITY_CACHE = {
    "data": None,
    "last_updated": 0
}
CACHE_TTL_SECONDS = 300  # Cache lives for 5 minutes

# Pydantic schema for creating a review
class ReviewCreate(BaseModel):
    overall_rating: float
    title: Optional[str] = None
    text: Optional[str] = None

@router.get("/nearby")
async def get_nearby_facilities(
    lat: float = Query(23.2156, description="User Latitude (Default: Gandhinagar Center)"),
    lon: float = Query(72.6369, description="User Longitude (Default: Gandhinagar Center)"),
    material: str = Query("plastic", description="Material to recycle"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Finds the best facilities based on zero-budget AI scoring (Distance, Rating, Material).
    Uses In-Memory Caching to prevent database lockups.
    """
    try:
        current_time = time.time()
        
        # 1. Check if we have valid cached data
        if FACILITY_CACHE["data"] is not None and (current_time - FACILITY_CACHE["last_updated"]) < CACHE_TTL_SECONDS:
            facilities = FACILITY_CACHE["data"]
        else:
            # 2. Cache miss or expired: Fetch from DB and update cache
            facilities = db.query(Facility).filter(Facility.is_open == True).all()
            FACILITY_CACHE["data"] = facilities
            FACILITY_CACHE["last_updated"] = current_time
        
        if not facilities:
            ranked_facilities = []
        else:
            # Let the AI Engine score and rank them! (Zero paid APIs)
            ranked_facilities = ai_engine.score_and_rank_facilities(
                user_lat=lat, 
                user_lon=lon, 
                material=material.lower(), 
                facilities=facilities
            )
            
        total = len(ranked_facilities)
        start = (page - 1) * limit
        end = start + limit
        paginated = ranked_facilities[start:end]

        return {
            "success": True,
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if total else 0,
            },
        }
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to fetch nearby facilities.",
                "error": str(exc),
            },
        )

@router.post("/{facility_id}/reviews")
def add_facility_review(
    facility_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows authenticated users to leave reviews for facilities."""
    try:
        facility = db.query(Facility).filter(Facility.id == facility_id).first()
        if not facility:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": "Facility not found.",
                    "error": "Not Found",
                },
            )

        new_review = FacilityReview(
            facility_id=facility_id,
            user_id=current_user.id,
            title=review.title or "",
            rating=review.overall_rating,
            comment=review.text or "",
        )

        total_rating = ((facility.rating or 0) * (facility.total_reviews or 0)) + review.overall_rating
        facility.total_reviews = (facility.total_reviews or 0) + 1
        facility.rating = round(total_rating / facility.total_reviews, 1)

        db.add(new_review)
        db.commit()
        
        # IN-MEMORY CACHE INVALIDATION
        # Force the map cache to refresh on the next request so the new rating shows up!
        FACILITY_CACHE["last_updated"] = 0

        return {
            "success": True,
            "data": {"message": "Review added successfully"},
        }
    except HTTPException as exc:
        db.rollback()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error": "Request failed",
            },
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Could not add review.",
                "error": str(exc),
            },
        )

@router.get("/{facility_id}")
def get_facility_details(facility_id: int, db: Session = Depends(get_db)):
    """Fetch details for a specific facility when a user clicks a map marker."""
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    return {
        "success": True,
        "data": {
            "id": facility.id,
            "name": facility.name,
            "address": facility.address,
            "city": facility.city,
            "phone": facility.phone,
            "latitude": facility.latitude,
            "longitude": facility.longitude,
            "rating": facility.rating,
            "materials_accepted": facility.materials_accepted
        }
    }