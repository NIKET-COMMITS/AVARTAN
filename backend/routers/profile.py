from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import UserImpact

router = APIRouter(prefix="/profile", tags=["User Legacy (Phase 5)"])

def get_eco_title(points: int):
    """Simple, growth-based titles."""
    if points < 100: return "Sprout"
    if points < 500: return "Bloom"
    if points < 1500: return "Rooted"
    if points < 5000: return "Evergreen"
    return "Legendary Guardian"

@router.get("/{user_id}/impact")
def get_user_impact(user_id: int, db: Session = Depends(get_db)):
    """
    Returns a simple 'Environmental Legacy' report.
    """
    impact = db.query(UserImpact).filter(UserImpact.user_id == user_id).first()
    
    if not impact:
        return {
            "title": "New Sprout",
            "score": 0,
            "stats": {
                "co2_offset": 0,
                "tree_power": 0,
                "trips": 0
            }
        }

    # Calculations
    co2 = round(impact.total_co2_saved, 2)
    # Using 'Tree Power' instead of 'Trees Equivalent'
    tree_power = round(co2 / 21, 2) 

    return {
        "user_id": user_id,
        "title": get_eco_title(impact.points),
        "score": impact.points,
        "legacy": {
            "co2_offset_kg": co2,
            "tree_power": tree_power,  # How many trees you've "acted" as
            "total_trips": impact.total_waste_collected
        },
        "badge_summary": f"You have the carbon-offsetting power of {tree_power} mature trees!"
    }