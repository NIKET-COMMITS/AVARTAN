"""
Waste Management Router
Features Threaded AI Diagnostics for both Image and Text inputs.
"""

import os
import json
import logging
import io
import asyncio
import socket
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from PIL import Image

# --- THE SPEED FIX 1: Windows IPv6 DNS Timeout Override ---
# This stops Python from hanging for 80+ seconds trying to route through dead IPv6 channels.
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo
# ----------------------------------------------------------

# NEW SDK IMPORT
from google import genai

from backend.database import get_db
from backend.models import WasteItem, UserImpact, User
from backend.routers.auth import get_current_user 
from backend.ai_engine import ai_engine, UNIVERSAL_APPRAISAL_LOGIC
from backend.validators import validate_quantity

logger = logging.getLogger("avartan")
router = APIRouter(prefix="/waste", tags=["Waste Management"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.warning("⚠️ GEMINI_API_KEY is not set. Vision AI will fail until configured.")
    client = None

# --- Endpoints ---

@router.post("/diagnose")
async def diagnose_item(
    image: Optional[UploadFile] = File(None),
    item_text: Optional[str] = Form(None),
    user_answers: Optional[str] = Form(None), # JSON string of previous answers
    current_user: User = Depends(get_current_user)
):
    if not image and not item_text:
        raise HTTPException(status_code=400, detail="You must provide either an image or a description.")
        
    if not client:
        raise HTTPException(status_code=500, detail="AI Engine is not configured.")

    try:
        contents = []
        
        # --- THE SPEED FIX 2: Threaded Image Compression ---
        if image:
            image_bytes = await image.read()
            
            def compress_image(data):
                original_kb = len(data) / 1024
                logger.info(f"📸 Original Image Payload: {original_kb:.2f} KB")

                img = Image.open(io.BytesIO(data)).convert("RGB")
                img.thumbnail((512, 512)) # Enforce 512px constraint
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=70)
                
                compressed_kb = len(buffer.getvalue()) / 1024
                logger.info(f"📉 Compressed Image Payload: {compressed_kb:.2f} KB")

                buffer.seek(0)
                return Image.open(buffer)

            # Offload heavy CPU work so FastAPI doesn't freeze
            processed_img = await asyncio.to_thread(compress_image, image_bytes)
            contents.append(processed_img)

        # 2. Add Text Context
        if item_text:
            contents.append(f"User stated item is: {item_text}")
            
        if user_answers:
            contents.append(f"User answered previous diagnostic questions: {user_answers}")

        # 3. The Multi-Turn Diagnostic Prompt
        prompt = """
        You are an elite electronics and e-waste appraiser for the Indian market.
        Analyze the provided image and/or text to determine the item's value.
        
        CRITICAL PRICING RULE: Electronics like smartphones, laptops, and appliances hold significant second-hand value. An iPhone (even cracked) is worth ₹5,000 - ₹30,000+ depending on the model and working condition. NEVER price a recognizable electronic device at raw scrap metal value (like ₹1000) unless the user explicitly states it is completely destroyed/burnt.
        
        INSTRUCTIONS:
        1. If you do not have enough info to give a precise final price, set "status" to "needs_info", provide an "estimated_value_range_inr", and ask 2-3 specific questions (e.g., "What is the storage capacity?", "Does it turn on?").
        2. If the user has provided enough answers to your questions, set "status" to "complete" and give a precise "final_value_inr".
        
        Respond ONLY with a valid JSON object matching this structure:
        {
            "status": "needs_info" OR "complete",
            "item_identified": "Name of item",
            "category": "ewaste, appliance, metal, plastic, paper, or glass",
            "estimated_value_range_inr": [min_val, max_val],
            "final_value_inr": integer (0 if status is needs_info),
            "questions_to_ask": ["Question 1?", "Question 2?"],
            "reasoning": "Brief explanation of your valuation"
        }
        """
        contents.append(prompt)

        # 4. ASYNC CALL - Strictly maintaining your gemini-2.5-flash configuration
        def call_gemini():
            return client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=contents
            )
            
        response = await asyncio.to_thread(call_gemini)
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        ai_data = json.loads(raw_text)

        return {
            "success": True,
            "data": ai_data
        }

    except Exception as e:
        logger.error(f"AI Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process diagnostics.")


# --- Legacy endpoints kept for backwards compatibility ---
class AIClassificationResponse(BaseModel):
    material: str
    confidence: float
    estimated_value_per_kg: float
    co2_saved_per_kg: float
    advice: str

@router.post("/classify", response_model=AIClassificationResponse)
def classify_waste_text(description: str):
    result = ai_engine.classify_waste(description)
    material = result["material"]
    base_value = UNIVERSAL_APPRAISAL_LOGIC.get(material, {}).get("base_value", 15.0)

    return AIClassificationResponse(
        material=material,
        confidence=result["confidence"],
        estimated_value_per_kg=base_value,
        co2_saved_per_kg=result["co2_saved_per_kg"],
        advice=result["advice"]
    )

class WasteSubmitRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=3, max_length=1000)
    quantity: float = Field(..., gt=0)
    condition: str = Field(default="good")
    final_ai_value: Optional[float] = Field(None)

@router.post("/log")
def log_waste(request: WasteSubmitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    safe_qty = validate_quantity(request.quantity)
    ai_result = ai_engine.classify_waste(f"{request.item_name} - {request.description}")
    
    if request.final_ai_value:
        total_value = request.final_ai_value
    else:
        base_value = UNIVERSAL_APPRAISAL_LOGIC.get(ai_result["material"], {}).get("base_value", 15.0)
        total_value = safe_qty * base_value
        
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
        return {"message": "Waste logged!", "waste_id": new_waste.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))