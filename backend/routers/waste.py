"""
Waste Management Router
Integrates Advanced Vision-Language AI (Gemini 2.5 Flash) and Text Classification.
"""

import os
import json
import logging
import io
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from PIL import Image

# NEW SDK IMPORT
from google import genai

from backend.database import get_db
from backend.models import WasteItem, UserImpact, User
from backend.routers.auth import get_current_user 
from backend.ai_engine import ai_engine
from backend.validators import validate_quantity

logger = logging.getLogger("avartan")
router = APIRouter(prefix="/waste", tags=["Waste Management"])

# --- CONFIGURE ADVANCED VISION AI (NEW SDK) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.warning("⚠️ GEMINI_API_KEY is not set. Vision AI will fail until configured.")
    client = None

# --- Pydantic Schemas ---
class WasteSubmitRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=3, max_length=1000)
    quantity: float = Field(..., gt=0, description="Quantity in KG")
    condition: str = Field(default="good")

class AIClassificationResponse(BaseModel):
    material: str
    confidence: float
    estimated_value_per_kg: float
    co2_saved_per_kg: float
    advice: str

# --- Endpoints ---

@router.post("/analyze")
async def analyze_waste_image(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
        
    if not client:
        raise HTTPException(status_code=500, detail="AI Engine is not configured. Missing API Key.")

    try:
        image_bytes = await files[0].read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # UPGRADED PROMPT: Smarter Valuations & strict Troll-proofing
        prompt = """
        You are an expert e-waste appraiser, thrift store valuer, and recycling specialist. 
        Analyze this image and identify the item with extreme precision.
        
        🛑 CRITICAL GUARDRAIL: If the image is completely unrelated to waste, recyclable materials, appliances, electronics, or household items (e.g., a human face, a pet, a landscape, a meme), you MUST reject it by returning this exact JSON:
        {
            "item_name": "Invalid Input Detected",
            "category": "None",
            "brand": "None",
            "model": "None",
            "visible_damage": "This does not appear to be a valid item for recycling or appraisal.",
            "estimated_value_inr": 0,
            "co2_saved_kg": 0.0,
            "premium_insight": "Please upload a clear image of actual waste, electronics, or recyclable materials."
        }
        
        If the image IS valid waste/recyclable, evaluate it carefully. Factor in brand depreciation, visible damage, and raw scrap weight value. Respond ONLY with a valid JSON object using this exact structure:
        {
            "item_name": "Full name of the item (e.g., Apple iPhone 12 Pro, LG Refrigerator, Cardboard Box)",
            "category": "Broad category (e.g., 'Electronics', 'Home Appliance', 'Furniture', 'Clothing', 'Raw Recyclable')",
            "brand": "Brand name if visible, else 'Unknown'",
            "model": "Exact model if visible, else 'Unknown'",
            "visible_damage": "Describe any cracks, scratches, rust, tears, or wear you see.",
            "estimated_value_inr": integer (Provide a highly realistic, conservative baseline second-hand or scrap value in INR. Do not over-estimate.),
            "co2_saved_kg": float (Estimate CO2 saved by recycling or reusing this specific item),
            "premium_insight": "A short 1-sentence observation. (e.g., 'Screen is shattered, but salvage value remains high.')"
        }
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        ai_data = json.loads(raw_text)

        return {
            "success": True,
            "message": "AI Diagnostics Complete",
            "data": ai_data
        }

    except json.JSONDecodeError:
        logger.error(f"AI returned invalid JSON: {response.text}")
        raise HTTPException(status_code=500, detail="AI returned an unreadable format. Please try another angle.")
        
    except Exception as e:
        logger.error(f"AI Image Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process image through AI Engine: {str(e)}")


@router.post("/classify", response_model=AIClassificationResponse)
def classify_waste_text(description: str):
    result = ai_engine.classify_waste(description)
    return AIClassificationResponse(
        material=result["material"],
        confidence=result["confidence"],
        estimated_value_per_kg=result["estimated_value_per_kg"],
        co2_saved_per_kg=result["co2_saved_per_kg"],
        advice=result["advice"]
    )


@router.post("/log")
def log_waste(
    request: WasteSubmitRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    safe_qty = validate_quantity(request.quantity)
    ai_result = ai_engine.classify_waste(f"{request.item_name} - {request.description}")
    
    total_value = safe_qty * ai_result["estimated_value_per_kg"]
    total_co2 = safe_qty * ai_result["co2_saved_per_kg"]
    
    new_waste = WasteItem(
        user_id=current_user.id,
        item_name=request.item_name,
        description=request.description,
        quantity_kg=safe_qty,
        condition=request.condition,
        confidence_score=ai_result["confidence"],
        estimated_value=total_value,
        estimated_co2_saved=total_co2,
        material_composition={"primary": ai_result["material"]}
    )
    db.add(new_waste)
    
    impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
    if not impact:
        impact = UserImpact(user_id=current_user.id)
        db.add(impact)
    
    impact.total_waste_collected += safe_qty
    impact.total_co2_saved += total_co2
    impact.points += int(safe_qty * 10)
    
    try:
        db.commit()
        db.refresh(new_waste)
        return {
            "message": "Waste logged successfully!",
            "ai_insights": ai_result,
            "waste_id": new_waste.id,
            "impact_updated": {"co2_saved": total_co2, "points_earned": int(safe_qty * 10)}
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/history")
def get_user_waste_history(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(WasteItem).filter(WasteItem.user_id == current_user.id).order_by(WasteItem.created_at.desc()).limit(limit).all()
    return {"success": True, "data": items}