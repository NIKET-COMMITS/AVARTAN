"""
Dashboard API Endpoints - Enterprise Grade
Features: Secure JWT Auth, Dynamic User Context, and Comprehensive Error Logging
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.models import User
from backend.routers.auth import get_current_user # SECURITY RESTORED
from backend.services.dashboard_service import dashboard_service

logger = logging.getLogger("avartan")

router = APIRouter(prefix="/dashboard", tags=["analytics"])

@router.get("/metrics")
def get_user_metrics(
    current_user: User = Depends(get_current_user), # SECURED: Requires valid JWT
    db: Session = Depends(get_db)
):
    """
    Fetches real-time personalized metrics for the authenticated user.
    """
    try:
        # Dynamic context: Only fetches data for the logged-in user
        metrics = dashboard_service.calculate_user_metrics(current_user.id, db) or {}
        
        return {
            'success': True,
            'data': metrics
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
        logger.error(f"Error fetching metrics for User {current_user.id}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to fetch personalized metrics. Please try again later.",
                "error": str(e),
            },
        )

@router.get("/leaderboards")
def get_leaderboards(
    current_user: User = Depends(get_current_user), # Ensures only registered users can view rankings
    db: Session = Depends(get_db)
):
    """
    Fetches global gamification rankings.
    """
    try:
        leaderboards = dashboard_service.get_leaderboards(db) or {}
        return {
            'success': True, 
            'data': leaderboards
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
        logger.error(f"Error fetching leaderboards: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Could not load leaderboard data.",
                "error": str(e),
            },
        )

@router.get("/achievements")
def get_user_achievements(
    current_user: User = Depends(get_current_user), # SECURED
    db: Session = Depends(get_db)
):
    """
    Fetches the unlocked badges and achievements for the authenticated user.
    """
    try:
        # Dynamic context: No more hardcoded ID
        achievements = dashboard_service.get_user_achievements(current_user.id, db) or []
        return {
            'success': True, 
            'data': achievements
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
        logger.error(f"Error fetching achievements for User {current_user.id}: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Could not load user achievements.",
                "error": str(e),
            },
        )