"""
Leaderboard Router - Enterprise Grade
Features: Dynamic User Ranking, Global Top 10, JWT Secured
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import User, UserImpact
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/leaderboards", tags=["gamification"])

@router.get("/global")
def get_global_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # SECURED
):
    try:
        # 1. Fetch Top 10 Users globally
        top_impacts = db.query(UserImpact, User.name)\
            .join(User, UserImpact.user_id == User.id)\
            .order_by(desc(UserImpact.points))\
            .limit(10).all()

        leaderboard_data = []
        for rank, (impact, user_name) in enumerate(top_impacts, start=1):
            leaderboard_data.append({
                "rank": rank,
                "user_id": impact.user_id,
                "name": user_name,
                "points": impact.points,
                "co2_saved": round(impact.total_co2_saved, 2),
                "is_current_user": impact.user_id == current_user.id # Highlights the user in the UI
            })

        # 2. Find Current User's Rank (if not in top 10)
        # This is crucial for a good UI experience
        user_impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
        user_rank = None
        if user_impact:
            user_rank = db.query(UserImpact).filter(UserImpact.points > user_impact.points).count() + 1

        return {
            "success": True,
            "data": {
                "top_10": leaderboard_data,
                "current_user": {
                    "rank": user_rank or "-",
                    "points": user_impact.points if user_impact else 0,
                    "name": current_user.name
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not load leaderboard")