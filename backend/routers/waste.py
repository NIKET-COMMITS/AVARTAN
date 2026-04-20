"""
Waste Management Router
Features Threaded AI Diagnostics for both Image and Text inputs.
Includes Last-Mile Receipt Verification.
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
from backend.config import Settings

logger = logging.getLogger("avartan")


def _unique_gemini_models(primary: str, *extras: str) -> List[str]:
    seen: set = set()
    out: List[str] = []
    for m in (primary, *extras):
        m = (m or "").strip()
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _gemini_try_next_model(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg
        or "404" in msg
        or "not found" in msg
        or "503" in msg           # NEW: Catches server overload
        or "unavailable" in msg   # NEW: Catches server overload
    )


def _get_genai_client():
    """Fresh read of GEMINI_API_KEY so a new key in .env works after server restart."""
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key:
        return None
    return genai.Client(api_key=key)


def _quota_placeholder_enabled() -> bool:
    v = os.getenv("GEMINI_QUOTA_PLACEHOLDER", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _diagnose_quota_placeholder(item_text: Optional[str]) -> dict:
    label = (item_text or "").strip()[:120] or "your item"
    return {
        "status": "needs_info",
        "item_identified": label or "Unnamed item",
        "category": "ewaste",
        "estimated_value_range_inr": [500, 8000],
        "final_value_inr": 0,
        "questions_to_ask": [
            "What is the brand and model?",
            "Does it power on and hold a charge?",
            "What are the technical specifications (RAM/Storage)?",
            "Are there any visible scratches or dents?"
        ],
        "reasoning": (
            "Gemini API quotas are exhausted for this API key or project (free-tier limits). "
            "This is a placeholder so you can keep testing the app. "
            "Use a key with available quota in Google AI Studio, enable billing if needed, or wait for the daily reset."
        ),
    }


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

    gemini_client = _get_genai_client()
    if not gemini_client:
        raise HTTPException(status_code=500, detail="AI Engine is not configured.")

    try:
        contents = []
        
        # --- THE SPEED FIX 2: Threaded Image Compression & Payload Limits ---
        if image:
            image_bytes = await image.read()
            
            # --- 15MB Payload Limit (Server Protection) ---
            MAX_FILE_SIZE = 15 * 1024 * 1024 # 15 MB
            if len(image_bytes) > MAX_FILE_SIZE:
                logger.warning(f"Blocked oversized image payload: {len(image_bytes)/1024/1024:.2f} MB")
                raise HTTPException(status_code=400, detail="Image is too large. Please upload an image under 15MB.")
            # ----------------------------------------------

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

        # 3. The Multi-Turn Diagnostic Prompt (ADAPTIVE QUESTIONING up to 8)
        prompt = """
        You are an elite electronics and e-waste appraiser for the Indian market.
        Analyze the provided image and/or text to determine the item's value.
        
        CRITICAL PRICING RULE: Electronics like smartphones, laptops, and appliances hold significant second-hand value. NEVER price a recognizable electronic device at raw scrap metal value (like ₹1000) unless the user explicitly states it is completely destroyed/burnt.
        
        DYNAMIC QUESTIONING RULES (UP TO 8 MAX):
        1. Max Limit: You may ask up to a MAXIMUM of 8 specific questions, but ONLY if the item's complexity demands it.
        2. Adaptive Scaling (Crucial): The number of questions MUST vary based on the item type and visible condition:
           - Scrap/Obvious Junk (wires, shattered plastics, basic metals, old papers): 0 questions. Just give a price and set status to "complete".
           - Mid-tier items (basic working electronics, standard home appliances): 1-3 questions (e.g. "Does it turn on?", "How old is it?").
           - High-value/Complex items (Laptops, iPhones, DSLRs, Gaming Consoles, high-end appliances): Ask 3-8 necessary questions to determine exact specs (RAM, storage, processor), battery health, accessories, and functional condition. Only ask what is strictly necessary to price it accurately.
        3. One-Round Limit: If the user has provided ANY answers in the 'User Follow-up' context, you MUST set status to "complete" and provide a final price. NEVER ask follow-up questions to an answer.
        
        Respond ONLY with a valid JSON object matching this structure:
        {
            "status": "needs_info" OR "complete",
            "item_identified": "Name of item",
            "category": "ewaste, appliance, metal, plastic, paper, or glass",
            "estimated_value_range_inr": [min_val, max_val],
            "final_value_inr": integer (0 if status is needs_info),
            "questions_to_ask": ["Q1", "Q2", "... up to 8 depending on item complexity"],
            "reasoning": "Brief explanation of your valuation"
        }
        """
        contents.append(prompt)

        # 4. ASYNC CALL — GEMINI_MODEL from env (fresh), then extra model ids if quota / 404
        primary = (os.getenv("GEMINI_MODEL") or "").strip() or Settings.GEMINI_MODEL
        model_ids = _unique_gemini_models(
            primary,
            "gemini-2.5-flash",
            "gemini-2.5-flash-preview-05-20",
            "gemini-1.5-flash",
            "gemini-2.0-flash",
        )
        response = None
        last_exc: Optional[Exception] = None
        for mid in model_ids:

            def call_gemini(model_name: str = mid):
                return gemini_client.models.generate_content(model=model_name, contents=contents)

            try:
                response = await asyncio.to_thread(call_gemini, mid)
                break
            except Exception as e:
                last_exc = e
                if _gemini_try_next_model(e):
                    logger.warning(
                        "Gemini model %s failed (%s): %s",
                        mid,
                        type(e).__name__,
                        str(e)[:400],
                    )
                    continue
                raise

        if response is None:
            logger.error(f"AI Processing Error: {last_exc!s}")
            if last_exc is not None and _gemini_try_next_model(last_exc) and _quota_placeholder_enabled():
                logger.warning("Returning quota placeholder diagnostic (GEMINI_QUOTA_PLACEHOLDER is enabled).")
                return {
                    "success": True,
                    "data": _diagnose_quota_placeholder(item_text),
                    "quota_placeholder": True,
                }
            if last_exc is not None and _gemini_try_next_model(last_exc):
                raise HTTPException(
                    status_code=429,
                    detail="AI service is temporarily over capacity. Please try again in a minute.",
                )
            raise HTTPException(status_code=500, detail="Failed to process diagnostics.")
        
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process diagnostics.")


# --- NEW: AI Receipt Verification Endpoint ---

@router.post("/verify-action")
async def verify_receipt(
    receipt_image: UploadFile = File(...),
    action_type: str = Form(...), # 'Sell', 'Donate', 'Recycle'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Forensic AI Verification of user actions (receipts, screenshots).
    Awards points ONLY if the AI confirms the action is legitimate.
    """
    gemini_client = _get_genai_client()
    if not gemini_client:
        raise HTTPException(status_code=500, detail="AI Engine is not configured.")

    try:
        image_bytes = await receipt_image.read()
        
        # Security: Prevent massive file uploads
        if len(image_bytes) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large.")

        def process_receipt(data):
            img = Image.open(io.BytesIO(data)).convert("RGB")
            img.thumbnail((1024, 1024)) # Slightly larger for reading text
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            return Image.open(buffer)

        processed_img = await asyncio.to_thread(process_receipt, image_bytes)

        prompt = f"""
        Analyze this image. It is supposed to be a receipt, screenshot, or photographic proof that the user successfully completed a '{action_type}' transaction for an item.

        Task: Verify if this is legitimate proof of a completed transaction (e.g., an OLX chat showing sold, a Cashify receipt, a donation center slip, or a picture of an item in a recycling bin).
        
        Respond ONLY with a valid JSON object:
        {{
            "verified": true/false,
            "vendor_or_platform": "Name of place if visible, else 'Unknown'",
            "reasoning": "Why you approved or rejected this proof."
        }}
        """

        # Using env-driven model with sensible default
        primary = (os.getenv("GEMINI_MODEL") or "").strip() or Settings.GEMINI_MODEL

        def call_verifier():
            return gemini_client.models.generate_content(
                model=primary,
                contents=[processed_img, prompt]
            )

        response = await asyncio.to_thread(call_verifier)
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        verification_data = json.loads(raw_text)

        # Award points ONLY if verified — scales slightly with lifetime CO2 saved (dashboard metric)
        if verification_data.get("verified") is True:
            impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
            if not impact:
                impact = UserImpact(user_id=current_user.id)
                db.add(impact)
            
            total_co2 = float(impact.total_co2_saved or 0)
            co2_bonus = min(350, int(total_co2 * 18))
            points_awarded = 200 + co2_bonus
            impact.points += points_awarded
            
            db.commit()
            
            return {
                "success": True,
                "verified": True,
                "points_awarded": points_awarded,
                "message": f"Proof verified! You earned {points_awarded} community points (includes a bonus tied to your CO₂ saved on the dashboard).",
                "details": verification_data
            }
        else:
            return {
                "success": True,
                "verified": False,
                "message": "AI could not verify this proof.",
                "details": verification_data
            }

    except Exception as e:
        logger.error(f"Verification Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify receipt.")


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
    # NOTE: I have REMOVED the automatic point awarding here to prevent leaderboard spam.
    # Users must now use the /verify-action endpoint to get points.
    
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
    
    # We still track CO2 and weight, but points are zeroed out until verified.
    impact = db.query(UserImpact).filter(UserImpact.user_id == current_user.id).first()
    if not impact:
        impact = UserImpact(user_id=current_user.id)
        db.add(impact)
    
    impact.total_waste_collected += safe_qty
    impact.total_co2_saved += total_co2
    
    try:
        db.commit()
        return {"message": "Waste logged! Upload proof to earn points.", "waste_id": new_waste.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))