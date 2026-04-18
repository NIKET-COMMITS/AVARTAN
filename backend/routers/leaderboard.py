"""
Leaderboard Router - Enterprise Grade
Features: Dynamic User Ranking, Global Top 10, JWT Secured
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import User, UserImpact
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/leaderboards", tags=["gamification"])

@router.get("/global")
def get_global_leaderboard(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # SECURED
):
    try:
        query = db.query(UserImpact, User.name)\
            .join(User, UserImpact.user_id == User.id)\
            .order_by(desc(UserImpact.points))
        total = query.count()
        offset = (page - 1) * limit
        top_impacts = query.offset(offset).limit(limit).all()

        leaderboard_data = []
        for rank, (impact, user_name) in enumerate(top_impacts, start=offset + 1):
            leaderboard_data.append({
                "rank": rank,
                "user_id": impact.user_id,
                "name": user_name or "",
                "points": impact.points or 0,
                "co2_saved": round(impact.total_co2_saved or 0, 2),
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
                    "rank": user_rank or 0,
                    "points": user_impact.points if user_impact else 0,
                    "name": current_user.name or ""
                },
            },
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Could not load leaderboard",
                "error": str(e),
            },
        )