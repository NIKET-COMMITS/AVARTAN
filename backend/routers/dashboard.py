"""
Dashboard API Endpoints - MODIFIED FOR DEMO (BYPASS AUTH)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.models import User
# from backend.routers.auth import get_current_user # Disabled for demo
from backend.services.dashboard_service import dashboard_service

logger = logging.getLogger("avartan")

router = APIRouter(prefix="/dashboard", tags=["analytics"])

@router.get("/metrics")
def get_user_metrics(
    # current_user: User = Depends(get_current_user), # REMOVED SECURITY
    db: Session = Depends(get_db)
):
    """Get personal metrics for User 1 (Demo Mode)"""
    try:
        # HARDCODED USER_ID TO 1 FOR PRESENTATION
        metrics = dashboard_service.calculate_user_metrics(1, db)
        
        return {
            'success': True,
            'data': metrics
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics"
        )

@router.get("/leaderboards")
def get_leaderboards(db: Session = Depends(get_db)):
    try:
        leaderboards = dashboard_service.get_leaderboards(db)
        return {'success': True, 'data': leaderboards}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error")

@router.get("/achievements")
def get_user_achievements(db: Session = Depends(get_db)):
    try:
        # HARDCODED USER_ID TO 1
        achievements = dashboard_service.get_user_achievements(1, db)
        return {'success': True, 'data': achievements}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error")