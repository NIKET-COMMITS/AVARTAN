"""
Marketplace Router
Zero-budget, peer-to-peer local scrap marketplace.
Allows users to list bulk waste and local scrappers to claim it.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import MarketplaceListing, User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# --- Pydantic Schemas ---
class ListingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    material_type: str = Field(..., description="e.g., plastic, metal, e-waste")
    quantity_kg: float = Field(..., gt=0)
    price_expected: float = Field(default=0.0, ge=0, description="0 means free pickup")

# --- Endpoints ---

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_listing(
    listing: ListingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new marketplace listing to sell or give away bulk scrap."""
    new_listing = MarketplaceListing(
        seller_id=current_user.id,
        title=listing.title,
        description=listing.description,
        material_type=listing.material_type.lower(),
        quantity_kg=listing.quantity_kg,
        price_expected=listing.price_expected,
        status="active"
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    
    return {
        "success": True,
        "message": "Listing created successfully",
        "data": {
            "id": new_listing.id,
            "title": new_listing.title
        }
    }

@router.get("/")
def get_active_listings(
    material: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Browse active listings. Optional filter by material type."""
    query = db.query(MarketplaceListing).filter(MarketplaceListing.status == "active")
    
    if material:
        query = query.filter(MarketplaceListing.material_type == material.lower())
        
    listings = query.order_by(MarketplaceListing.created_at.desc()).limit(limit).all()
    
    results = []
    for item in listings:
        results.append({
            "id": item.id,
            "title": item.title,
            "material_type": item.material_type,
            "quantity_kg": item.quantity_kg,
            "price_expected": item.price_expected,
            "created_at": item.created_at
        })
        
    return {
        "success": True,
        "data": results
    }

@router.post("/{listing_id}/claim")
def claim_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buyer claims an active listing."""
    listing = db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    if listing.status != "active":
        raise HTTPException(status_code=400, detail=f"Listing is already {listing.status}")
        
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot claim your own listing")
        
    # Process the claim
    listing.buyer_id = current_user.id
    listing.status = "claimed"
    db.commit()
    
    return {
        "success": True,
        "message": "You have successfully claimed this listing. Contact the seller for pickup details."
    }