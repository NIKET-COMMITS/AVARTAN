"""
Report Service - PDF and CSV report generation
"""

from typing import Dict, List
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import logging
import json
import csv
from io import StringIO

from backend.models import User, RouteHistory, Report

logger = logging.getLogger("avartan")


class ReportService:
    """Generates and manages user reports"""
    
    @staticmethod
    def generate_csv_report(user_id: int, period: str, db: Session) -> str:
        """Generate CSV report for user routes"""
        
        try:
            # Get routes for period
            routes = ReportService._get_routes_for_period(user_id, period, db)
            
            # Create CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                'Date', 'Facility', 'Distance (km)', 'CO2 Saved (kg)',
                'Material Value (₹)', 'Travel Time (min)', 'Satisfaction'
            ])
            
            # Data rows
            for route in routes:
                writer.writerow([
                    route.created_at.strftime('%Y-%m-%d'),
                    route.facility.name if route.facility else 'Unknown',
                    round(route.distance_km or 0, 2),
                    round(route.co2_saved_kg or 0, 2),
                    round(route.material_value_rupees or 0, 0),
                    route.travel_time_minutes or 0,
                    'Yes' if route.user_satisfied else 'No'
                ])
            
            return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            return ""
    
    @staticmethod
    def generate_pdf_report(user_id: int, period: str, db: Session) -> Dict:
        """Generate PDF report structure"""
        
        try:
            routes = ReportService._get_routes_for_period(user_id, period, db)
            
            # Calculate metrics for period
            total_routes = len(routes)
            total_co2 = sum(r.co2_saved_kg or 0 for r in routes)
            total_value = sum(r.material_value_rupees or 0 for r in routes)
            total_distance = sum(r.distance_km or 0 for r in routes)
            
            return {
                'user_id': user_id,
                'period': period,
                'generated_date': datetime.now().isoformat(),
                'summary': {
                    'total_routes': total_routes,
                    'co2_saved_kg': round(total_co2, 2),
                    'material_value': round(total_value, 0),
                    'distance_km': round(total_distance, 2),
                    'avg_co2_per_route': round(total_co2 / total_routes, 2) if total_routes > 0 else 0
                },
                'routes': [
                    {
                        'date': r.created_at.strftime('%Y-%m-%d'),
                        'facility': r.facility.name if r.facility else 'Unknown',
                        'distance_km': round(r.distance_km or 0, 2),
                        'co2_saved_kg': round(r.co2_saved_kg or 0, 2),
                        'material_value': round(r.material_value_rupees or 0, 0)
                    }
                    for r in routes
                ]
            }
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return {}
    
    @staticmethod
    def _get_routes_for_period(user_id: int, period: str, db: Session):
        """Get routes for specified period"""
        
        query = db.query(RouteHistory).filter(RouteHistory.user_id == user_id)
        
        if period == 'daily':
            start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start = datetime.now() - timedelta(days=7)
        elif period == 'monthly':
            start = datetime.now() - timedelta(days=30)
        else:
            start = datetime.now() - timedelta(days=365)
        
        return query.filter(RouteHistory.created_at >= start).all()


report_service = ReportService()