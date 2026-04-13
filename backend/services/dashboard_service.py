"""
Dashboard Service - Metrics calculation, rankings, achievements
Integrates with all existing services to provide comprehensive analytics
"""

from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from backend.models import (
    User, UserMetrics, FacilityMetrics, UserAchievement,
    CommunityMetrics, Facility, RouteHistory, WasteItem
)

logger = logging.getLogger("avartan")


class DashboardService:
    """Comprehensive dashboard and analytics service"""
    
    # Achievement definitions
    ACHIEVEMENTS = {
        'first_route': {
            'name': '🚀 First Step',
            'description': 'Complete your first waste disposal route',
            'icon': '🚀',
            'points': 50
        },
        'eco_warrior': {
            'name': '♻️ Eco Warrior',
            'description': 'Save 500kg CO2',
            'icon': '♻️',
            'points': 500
        },
        'material_master': {
            'name': '🔧 Material Master',
            'description': 'Recycle 50 different items',
            'icon': '🔧',
            'points': 300
        },
        'speed_demon': {
            'name': '⚡ Speed Demon',
            'description': 'Complete 5 routes in one day',
            'icon': '⚡',
            'points': 200
        },
        'value_hunter': {
            'name': '💰 Value Hunter',
            'description': 'Recover materials worth ₹10,000',
            'icon': '💰',
            'points': 400
        },
        'distance_master': {
            'name': '🗺️ Distance Master',
            'description': 'Travel 100km in routes',
            'icon': '🗺️',
            'points': 250
        },
        'helpful_rater': {
            'name': '⭐ Helpful Rater',
            'description': 'Submit 10 facility reviews',
            'icon': '⭐',
            'points': 150
        },
        'perfect_score': {
            'name': '🏆 Perfect Score',
            'description': 'Rate a facility 5 stars',
            'icon': '🏆',
            'points': 100
        },
        'consistency_king': {
            'name': '📈 Consistency King',
            'description': 'Maintain 7-day activity streak',
            'icon': '📈',
            'points': 350
        }
    }
    
    # User levels based on points
    LEVELS = [
        {'name': 'Beginner', 'min_points': 0, 'color': '#4285F4'},
        {'name': 'Contributor', 'min_points': 500, 'color': '#34A853'},
        {'name': 'Champion', 'min_points': 2000, 'color': '#FBBC04'},
        {'name': 'Master', 'min_points': 5000, 'color': '#EA4335'},
        {'name': 'Legend', 'min_points': 10000, 'color': '#9C27B0'},
    ]
    
    @staticmethod
    def calculate_user_metrics(user_id: int, db: Session) -> Dict:
        """Calculate comprehensive metrics for a user"""
        
        try:
            # Get user's routes
            routes = db.query(RouteHistory).filter(
                RouteHistory.user_id == user_id
            ).all()
            
            if not routes:
                return DashboardService._empty_metrics(user_id)
            
            # Calculate metrics
            total_routes = len(routes)
            total_co2_saved = sum(r.co2_saved_kg or 0 for r in routes)
            total_value = sum(r.material_value_rupees or 0 for r in routes)
            total_distance = sum(r.distance_km or 0 for r in routes)
            
            # Calculate user level
            total_points = total_routes * 50 + int(total_co2_saved) + int(total_value / 10)
            user_level = DashboardService._get_user_level(total_points)
            
            # Get today's metrics
            today = date.today()
            today_metrics = db.query(UserMetrics).filter(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date == today
            ).first()
            
            return {
                'user_id': user_id,
                'total_routes': total_routes,
                'co2_saved_kg': round(total_co2_saved, 2),
                'material_value_recovered': round(total_value, 0),
                'distance_traveled_km': round(total_distance, 2),
                'total_points': total_points,
                'current_level': user_level['name'],
                'level_color': user_level['color'],
                'progress_to_next_level': DashboardService._calculate_level_progress(total_points),
                'environmental_equivalents': DashboardService._calculate_equivalents(total_co2_saved),
            }
        
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return DashboardService._empty_metrics(user_id)
    
    @staticmethod
    def get_leaderboards(db: Session) -> Dict:
        """Get all leaderboards with top 10 in each category"""
        
        try:
            # Get all users with metrics
            user_metrics = db.query(
                User.id, User.name,
                func.count(RouteHistory.id).label('route_count'),
                func.sum(RouteHistory.co2_saved_kg).label('co2_sum'),
                func.sum(RouteHistory.material_value_rupees).label('value_sum'),
                func.sum(RouteHistory.distance_km).label('distance_sum')
            ).outerjoin(RouteHistory).group_by(User.id).all()
            
            # Top by CO2
            by_co2 = sorted(
                user_metrics,
                key=lambda x: x.co2_sum or 0,
                reverse=True
            )[:10]
            
            # Top by Value
            by_value = sorted(
                user_metrics,
                key=lambda x: x.value_sum or 0,
                reverse=True
            )[:10]
            
            # Top by Routes
            by_routes = sorted(
                user_metrics,
                key=lambda x: x.route_count,
                reverse=True
            )[:10]
            
            # Top by Distance
            by_distance = sorted(
                user_metrics,
                key=lambda x: x.distance_sum or 0,
                reverse=True
            )[:10]
            
            return {
                'by_co2_saved': [
                    {
                        'rank': idx + 1,
                        'user_id': m.id,
                        'name': m.name,
                        'value': round(m.co2_sum or 0, 2),
                        'unit': 'kg CO2'
                    }
                    for idx, m in enumerate(by_co2)
                ],
                'by_value_recovered': [
                    {
                        'rank': idx + 1,
                        'user_id': m.id,
                        'name': m.name,
                        'value': round(m.value_sum or 0, 0),
                        'unit': '₹'
                    }
                    for idx, m in enumerate(by_value)
                ],
                'by_routes_completed': [
                    {
                        'rank': idx + 1,
                        'user_id': m.id,
                        'name': m.name,
                        'value': m.route_count,
                        'unit': 'routes'
                    }
                    for idx, m in enumerate(by_routes)
                ],
                'by_distance': [
                    {
                        'rank': idx + 1,
                        'user_id': m.id,
                        'name': m.name,
                        'value': round(m.distance_sum or 0, 2),
                        'unit': 'km'
                    }
                    for idx, m in enumerate(by_distance)
                ]
            }
        
        except Exception as e:
            logger.error(f"Error getting leaderboards: {e}")
            return {}
    
    @staticmethod
    def get_user_achievements(user_id: int, db: Session) -> List[Dict]:
        """Get all achievements for a user"""
        
        try:
            achievements = db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.is_active == True
            ).all()
            
            return [
                {
                    'id': a.id,
                    'name': a.achievement_name,
                    'description': a.achievement_description,
                    'icon': a.icon,
                    'points': a.points_awarded,
                    'achieved_at': a.achieved_at.isoformat(),
                    'type': a.achievement_type
                }
                for a in achievements
            ]
        
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return []
    
    @staticmethod
    def get_community_stats(db: Session) -> Dict:
        """Get aggregate community statistics"""
        
        try:
            today = date.today()
            
            # Try to get today's community metrics
            community = db.query(CommunityMetrics).filter(
                CommunityMetrics.metric_date == today
            ).first()
            
            if community:
                return {
                    'total_users': community.total_users,
                    'total_routes': community.total_routes,
                    'co2_saved_kg': round(community.total_co2_saved_kg, 2),
                    'material_recovered_kg': round(community.total_material_recovered_kg, 2),
                    'value_recovered': round(community.total_value_recovered, 0),
                    'ecosystem_health': community.ecosystem_health_score,
                    'avg_user_level': community.avg_user_level,
                    'total_facility_transactions': community.total_facility_transactions,
                    'environmental_equivalents': DashboardService._calculate_equivalents(
                        community.total_co2_saved_kg
                    )
                }
            
            # Calculate on the fly if not cached
            all_routes = db.query(RouteHistory).all()
            total_co2 = sum(r.co2_saved_kg or 0 for r in all_routes)
            total_value = sum(r.material_value_rupees or 0 for r in all_routes)
            total_users = db.query(func.count(User.id)).scalar()
            
            return {
                'total_users': total_users,
                'total_routes': len(all_routes),
                'co2_saved_kg': round(total_co2, 2),
                'material_recovered_kg': 0,
                'value_recovered': round(total_value, 0),
                'ecosystem_health': min(100, len(all_routes) / 10),
                'avg_user_level': 'Contributor',
                'total_facility_transactions': len(all_routes),
                'environmental_equivalents': DashboardService._calculate_equivalents(total_co2)
            }
        
        except Exception as e:
            logger.error(f"Error calculating community stats: {e}")
            return {}
    
    @staticmethod
    def _calculate_equivalents(co2_kg: float) -> Dict:
        """Calculate environmental equivalents"""
        
        return {
            'trees_planted': round(co2_kg / 21, 1),  # 1 tree saves ~21kg CO2/year
            'car_miles_offset': round(co2_kg / 0.41, 1),  # 1 mile car = 0.41kg CO2
            'lightbulbs_powered_hours': round(co2_kg * 10, 0),  # 1kg CO2 = 10 bulb-hours
            'plastic_bottles_saved': round(co2_kg * 5, 0),  # Rough estimate
        }
    
    @staticmethod
    def _get_user_level(points: int) -> Dict:
        """Get user level based on points"""
        
        level = DashboardService.LEVELS[0]
        for lvl in DashboardService.LEVELS:
            if points >= lvl['min_points']:
                level = lvl
        
        return level
    
    @staticmethod
    def _calculate_level_progress(points: int) -> Dict:
        """Calculate progress towards next level"""
        
        current_level_idx = 0
        for idx, lvl in enumerate(DashboardService.LEVELS):
            if points >= lvl['min_points']:
                current_level_idx = idx
        
        if current_level_idx >= len(DashboardService.LEVELS) - 1:
            return {'current': 100, 'next_level': 'Legend', 'progress': 100}
        
        current_min = DashboardService.LEVELS[current_level_idx]['min_points']
        next_min = DashboardService.LEVELS[current_level_idx + 1]['min_points']
        
        progress = ((points - current_min) / (next_min - current_min)) * 100
        
        return {
            'current': round(min(100, progress), 1),
            'next_level': DashboardService.LEVELS[current_level_idx + 1]['name'],
            'points_needed': next_min - points
        }
    
    @staticmethod
    def _empty_metrics(user_id: int) -> Dict:
        """Return empty metrics structure"""
        
        return {
            'user_id': user_id,
            'total_routes': 0,
            'co2_saved_kg': 0,
            'material_value_recovered': 0,
            'distance_traveled_km': 0,
            'total_points': 0,
            'current_level': 'Beginner',
            'level_color': '#4285F4',
            'progress_to_next_level': {'current': 0, 'next_level': 'Contributor', 'points_needed': 500},
            'environmental_equivalents': {'trees_planted': 0, 'car_miles_offset': 0, 'lightbulbs_powered_hours': 0, 'plastic_bottles_saved': 0}
        }


dashboard_service = DashboardService()