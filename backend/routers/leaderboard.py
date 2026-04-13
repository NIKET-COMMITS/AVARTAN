from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import UserImpact, User
from backend.services.gamification_service import gamification_service

router = APIRouter(prefix="/leaderboard", tags=["Gamification (Phase 5)"])

@router.get("/global")
def get_global_leaderboard(db: Session = Depends(get_db), limit: int = 10):
    """Fetches the top users based on CO2 savings"""
    top_impacts = db.query(UserImpact).order_by(desc(UserImpact.total_co2_saved)).limit(limit).all()
    
    results = []
    for rank, impact in enumerate(top_impacts, 1):
        user = db.query(User).filter(User.id == impact.user_id).first()
        level_data = gamification_service.get_level_info(impact.total_co2_saved)
        
        results.append({
            "rank": rank,
            "username": user.name if user else "Anonymous",
            "co2_saved": impact.total_co2_saved,
            "level": level_data["level_name"],
            "points": impact.points
        })
        
    return {"success": True, "leaderboard": results}