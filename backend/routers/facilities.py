from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict
from pydantic import BaseModel
import time

from backend.database import get_db
from backend.models import Facility, FacilityReview, User
from backend.routers.auth import get_current_user
from backend.ai_engine import ai_engine

router = APIRouter(prefix="/facilities", tags=["Facilities"])

FACILITY_CACHE = {"data": None, "last_updated": 0}
CACHE_TTL_SECONDS = 300

class ReviewCreate(BaseModel):
    overall_rating: float
    title: Optional[str] = None
    text: Optional[str] = None

class AppraisalAnswers(BaseModel):
    material: str
    weight: float
    answers: Dict[str, str]

@router.get("/appraisal-questions")
def get_questions(material: str):
    """Returns dynamic AI questions based on item category."""
    questions = ai_engine.get_appraisal_questions(material)
    return {"success": True, "data": questions}

@router.post("/smart-rank-advanced")
def get_advanced_ranked_facilities(
    lat: float, 
    lon: float, 
    payload: AppraisalAnswers, 
    db: Session = Depends(get_db)
):
    """Calculates AI advice and exact value, then ranks facilities."""
    try:
        facilities = db.query(Facility).all()
        if not facilities:
            return {"success": True, "data": []}

        # AI calculates exact market value & advice
        appraisal_data = ai_engine.calculate_exact_value_and_advice(
            material=payload.material, 
            weight=payload.weight, 
            answers=payload.answers
        )

        filtered_facilities = []
        search_material = payload.material.lower().replace("-", "") 
        
        for f in facilities:
            if f.materials_accepted:
                accepted_str = str(f.materials_accepted).lower().replace("-", "")
                if search_material in accepted_str:
                    filtered_facilities.append(f)

        if not filtered_facilities:
            return {"success": True, "data": []}

        # Rank and inject appraisal
        ranked_data = ai_engine.score_and_rank_facilities(
            user_lat=lat, 
            user_lon=lon, 
            material=payload.material, 
            facilities=filtered_facilities,
            weight=payload.weight,
            appraisal_data=appraisal_data
        )
        
        return {"success": True, "data": ranked_data}
    except Exception as e:
        print(f"Appraisal Error: {e}")
        raise HTTPException(status_code=500, detail="Appraisal failed.")

@router.get("/smart-rank")
def get_smart_ranked_facilities(
    lat: float, lon: float, material: str, weight: float = 1.0, db: Session = Depends(get_db)
):
    # Kept for backward compatibility if needed
    try:
        facilities = db.query(Facility).all()
        filtered_facilities = [f for f in facilities if f.materials_accepted and material.lower().replace("-", "") in str(f.materials_accepted).lower().replace("-", "")]
        ranked_data = ai_engine.score_and_rank_facilities(user_lat=lat, user_lon=lon, material=material, facilities=filtered_facilities, weight=weight)
        return {"success": True, "data": ranked_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to rank facilities.")

@router.get("/nearby")
async def get_nearby_facilities(
    lat: float = Query(23.2156), lon: float = Query(72.6369), material: str = Query("plastic"),
    page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
):
    try:
        current_time = time.time()
        if FACILITY_CACHE["data"] is not None and (current_time - FACILITY_CACHE["last_updated"]) < CACHE_TTL_SECONDS:
            facilities = FACILITY_CACHE["data"]
        else:
            facilities = db.query(Facility).filter(Facility.is_open == True).all()
            FACILITY_CACHE["data"] = facilities
            FACILITY_CACHE["last_updated"] = current_time
        
        ranked_facilities = ai_engine.score_and_rank_facilities(user_lat=lat, lon=lon, material=material.lower(), facilities=facilities) if facilities else []
        start = (page - 1) * limit
        return {"success": True, "data": ranked_facilities[start:start + limit], "pagination": {"page": page, "limit": limit, "total": len(ranked_facilities)}}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "message": str(exc)})

@router.get("/{facility_id}")
def get_facility_details(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility: raise HTTPException(status_code=404, detail="Facility not found")
    return {"success": True, "data": facility}