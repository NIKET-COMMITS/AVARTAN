"""
Reports API Endpoints
Generates CSV and PDF reports for users
"""

from fastapi import APIRouter, Depends, HTTPException, status
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
        csv_content = report_service.generate_csv_report(current_user.id, period, db)
        
        return {
            'success': True,
            'data': {
                'format': 'csv',
                'content': csv_content,
                'filename': f"avartan_report_{period}_{current_user.id}.csv"
            }
        }
    
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export CSV"
        )


@router.get("/generate/pdf")
def generate_pdf(
    period: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF report"""
    
    try:
        report_data = report_service.generate_pdf_report(current_user.id, period, db)
        
        return {
            'success': True,
            'data': report_data
        }
    
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF"
        )