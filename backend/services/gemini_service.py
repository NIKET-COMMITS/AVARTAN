"""
Gemini AI Service - Phase 2 Final Production
Configured specifically for the available 2026 model stack.
"""

import google.generativeai as genai
import json
from typing import Dict, Any
from backend.config import settings
from backend.validators import sanitize_for_ai
from backend.logger import log_error, log_success, log_warning

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================

try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # EXACT MATCH from your diagnostic script
        model_name = 'models/gemini-2.5-flash' 
        model = genai.GenerativeModel(model_name)
        log_success("Gemini Init", f"Model {model_name} loaded successfully")
    else:
        log_warning("Gemini Init", "No API Key found. Running in Fallback Mode.")
        model = None
except Exception as e:
    log_error(f"Failed to initialize Gemini: {str(e)}")
    model = None

# ==========================================
# 2. CORE ANALYSIS FUNCTION
# ==========================================

def validate_waste_with_gemini(user_input: str) -> Dict[str, Any]:
    """
    Analyzes waste description using the verified available model.
    """
    print(f"\n[AI-GATEWAY] Routing Request to gemini-2.5-flash: '{user_input}'")
    
    # Security: Length Check
    max_len = getattr(settings, "MAX_DESCRIPTION_LENGTH", 500)
    if len(user_input) > max_len:
        return {"success": False, "error": "Description too long.", "use_fallback": True}
    
    # Security: Sanitize input
    sanitized_input = sanitize_for_ai(user_input)
    
    if not model:
        return get_fallback_response(sanitized_input)

    # Prompt Engineering: Forces strict JSON output
    prompt = f"""
    Analyze this waste item: "{sanitized_input}"
    Return ONLY a valid JSON object with exact keys:
    {{
        "item_name": "string",
        "item_type": "Electronics, Plastic, Metal, Paper, Organic, or Other",
        "condition": "mint, good, fair, poor, or broken",
        "confidence": 0.95,
        "materials": {{ "primary_material": 100 }},
        "total_weight_grams": 500,
        "estimated_value_rupees": 100,
        "estimated_co2_saved_kg": 0.5
    }}
    """

    try:
        # Standard Execution
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty response from AI Safety Filters.")

        text_response = response.text.strip()
        
        # Clean JSON markdown blocks
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text_response)
        log_success("Gemini Analysis", f"Successfully analyzed: {data.get('item_name')}")
        
        return {"success": True, "data": data}

    except Exception as e:
        error_msg = str(e)
        print("\n" + "="*60)
        print(f"EXECUTION ERROR: {error_msg}")
        print("="*60 + "\n")
        
        log_error(f"Execution Error: {error_msg}")
        return {
            "success": False,
            "error": f"AI service error: {error_msg}",
            "use_fallback": True
        }

# ==========================================
# 3. FALLBACK MECHANISM
# ==========================================

def get_fallback_response(user_input: str) -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "item_name": f"(Fallback) {user_input[:15]}",
            "item_type": "Other",
            "condition": "fair",
            "confidence": 0.5,
            "materials": {"unknown": 100},
            "total_weight_grams": 250,
            "estimated_value_rupees": 50,
            "estimated_co2_saved_kg": 0.5
        }
    }