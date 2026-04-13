from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from backend.database import get_db
from backend.models import Facility, UserImpact, RouteHistory
from backend.services.route_optimizer import route_optimizer
from backend.services.cost_analyzer import cost_analyzer

# Initialize logging for debugging
logger = logging.getLogger("avartan")

router = APIRouter(prefix="/routes", tags=["Route Optimization (Phase 4)"])

@router.get("/optimize")
def get_optimized_routes(
    user_lat: float, 
    user_lon: float, 
    waste_value: float = 500.0, 
    co2_potential: float = 5.0, 
    eco_preference: float = 0.5,
    db: Session = Depends(get_db)
):
    """
    Calculates the best 5 routes balancing distance, money, and CO2 emissions.
    Includes cost analysis and environmental impact summary for the top choice.
    """
    # 1. Fetch facilities
    facilities = db.query(Facility).all()
    fac_list = [
        {
            "id": f.id, 
            "name": f.name, 
            "latitude": f.latitude, 
            "longitude": f.longitude, 
            "rating": f.rating
        } for f in facilities
    ]
    
    if not fac_list:
        return {"success": False, "message": "No facilities found in database."}

    # 2. Run Route Optimizer
    best_routes = route_optimizer.optimize_route(
        (user_lat, user_lon), waste_value, co2_potential, fac_list, eco_preference
    )
    
    # 3. Add Deep Analysis to the #1 Result
    if best_routes:
        top = best_routes[0]
        analysis = cost_analyzer.analyze_route(
            estimated_value=top['estimated_value'],
            co2_saved_kg=top['estimated_co2_saved'],
            distance_km=top['distance_km'],
            facility_rating=top['facility_rating'],
            user_eco_preference=eco_preference
        )
        
        # Environmental context (Trees equivalent)
        co2_val = top['estimated_co2_saved']
        tree_equiv = round(co2_val / 21, 3) # 21kg CO2/year per tree
        
        analysis['environmental_impact'] = {
            "trees_saved_equivalent": tree_equiv,
            "description": f"Recycling this is like having {tree_equiv} trees absorbing CO2 for a year."
        }
        
        top['cost_analysis'] = analysis
        
    return {"success": True, "optimized_routes": best_routes}


@router.post("/select")
def select_route(user_id: int, route_data: dict, db: Session = Depends(get_db)):
    """
    Finalizes route selection, updates user leaderboard stats, and logs history.
    """
    # 1. Validate/Get User Impact Profile
    impact = db.query(UserImpact).filter(UserImpact.user_id == user_id).first()
    if not impact:
        impact = UserImpact(
            user_id=user_id, 
            total_waste_collected=0, 
            total_co2_saved=0.0, 
            points=0
        )
        db.add(impact)

    # 2. Process Stats with strict type casting
    try:
        co2_saved = float(route_data.get('estimated_co2_saved', 0.0))
        distance = float(route_data.get('distance_km', 0.0))
        pts_earned = int(co2_saved * 10)

        # Update Leaderboard Stats
        impact.total_co2_saved += co2_saved
        impact.total_waste_collected += 1
        impact.points += pts_earned

        # 3. Prepare History Log
        # Use a safe constructor to avoid crashes if columns are missing
        history = RouteHistory(
            user_id=user_id,
            waste_id=int(route_data.get('waste_id', 1)),
            selected_facility_id=int(route_data.get('facility_id', 1)),
            distance_km=distance,
            co2_saved_kg=co2_saved
        )

        # Check for optional column 'points_earned' in models.py
        if hasattr(history, 'points_earned'):
            history.points_earned = pts_earned

        db.add(history)
        db.commit()

        return {
            "success": True,
            "message": "Route finalized successfully",
            "earned": {
                "points": pts_earned,
                "co2_saved": co2_saved
            },
            "new_total_points": impact.points
        }

    except Exception as e:
        db.rollback()
        logger.error(f"DATABASE CRASH in /select: {str(e)}")
        # Brutal honesty: returning the exact error so you can fix it
        raise HTTPException(
            status_code=500, 
            detail=f"Logic Error: {str(e)}. Check if all IDs exist."
        )