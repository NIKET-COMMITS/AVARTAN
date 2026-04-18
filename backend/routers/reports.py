"""
Reports API Endpoints
Generates CSV and PDF reports for users
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.models import User
from backend.routers.auth import get_current_user
from backend.services.report_service import report_service

logger = logging.getLogger("avartan")

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/export/csv")
def export_csv(
    period: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export routes as CSV"""
    
    try:
        csv_content = report_service.generate_csv_report(current_user.id, period, db) or ""
        
        return {
            'success': True,
            'data': {
                'format': 'csv',
                'content': csv_content,
                'filename': f"avartan_report_{period}_{current_user.id}.csv"
            }
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
        logger.error(f"Error exporting CSV: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to export CSV",
                "error": str(e),
            },
        )


@router.get("/generate/pdf")
def generate_pdf(
    period: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF report"""
    
    try:
        report_data = report_service.generate_pdf_report(current_user.id, period, db) or {}
        
        return {
            'success': True,
            'data': report_data
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
        logger.error(f"Error generating PDF: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to generate PDF",
                "error": str(e),
            },
        )