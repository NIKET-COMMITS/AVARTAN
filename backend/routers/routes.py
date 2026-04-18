"""
Route Optimization Engine - Production Grade
Features: Haversine Distance Calculation, Real-time Sorting, and Geo-Validation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from math import radians, cos, sin, asin, sqrt
from typing import List, Optional

from backend.database import get_db
from backend.models import Facility, User
from backend.routers.auth import get_current_user
from backend.logger import log_error

router = APIRouter(prefix="/routes", tags=["routing"])

# ============ UTILS: THE ENGINE ============

def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points 
    on the Earth's surface in kilometers.
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return round(c * r, 2)

# ============ ENDPOINTS ============

@router.get("/optimize")
async def get_optimized_routes(
    user_lat: float = Query(..., ge=-90, le=90),
    user_lon: float = Query(..., ge=-180, le=180),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches facilities and calculates real-time distance from the user's GPS.
    Sorts results to show the most carbon-efficient options first.
    """
    try:
        # 1. Fetch all active facilities
        facilities = db.query(Facility).all()
        
        if not facilities:
            return {
                "success": True,
                "data": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0},
            }

        # 2. Map distances and enrich data
        enriched_facilities = []
        for f in facilities:
            dist = calculate_haversine(user_lat, user_lon, f.latitude, f.longitude)
            
            enriched_facilities.append({
                "id": f.id,
                "name": f.name or "",
                "address": f.address or "",
                "distance_km": dist,
                "accepted_materials": f.accepted_materials.split(",") if f.accepted_materials else [],
                "phone": f.phone or "",
                "is_open": True,
                "coordinates": {"lat": f.latitude or 0, "lng": f.longitude or 0}
            })

        optimized_list = sorted(enriched_facilities, key=lambda x: x["distance_km"])
        total = len(optimized_list)
        start = (page - 1) * limit
        end = start + limit
        paginated = optimized_list[start:end]

        return {
            "success": True,
            "data": paginated,
            "user_context": {"lat": user_lat, "lon": user_lon},
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit if total else 0,
            },
        }

    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error": "Request failed",
            },
        )
    except Exception as e:
        log_error(f"Routing Error for User {current_user.id}", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Could not calculate optimal routes at this time.",
                "error": str(e),
            },
        )