"""
Authentication & Authorization - Enterprise Grade
Features: OAuth2 Native, GDPR Account Deletion, and Crash-Proof Logging
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta, datetime, timezone
import secrets

from backend.database import get_db
from backend.models import User, LoginAttempt, PasswordReset, UserImpact, WasteItem, RouteHistory
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

logger = logging.getLogger("avartan")
router = APIRouter(prefix="/auth", tags=["authentication"])

# Native FastAPI OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ============ PYDANTIC SCHEMAS ============

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# ============ DEPENDENCY ============

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    # --- ROBUST TOKEN DECODING ---
    if isinstance(payload, str):
        token_sub = payload
    else:
        token_sub = payload.get("sub")
        
    if token_sub is None:
        raise credentials_exception
        
    # --- BULLETPROOF USER LOOKUP ---
    # Smartly checks if the token is using an email or a numeric ID
    if "@" in str(token_sub):
        # Handle older tokens that stored the email address
        user = db.query(User).filter(User.email == str(token_sub)).first()
    else:
        # Handle newer tokens that store the numeric ID
        try:
            user = db.query(User).filter(User.id == int(token_sub)).first()
        except ValueError:
            raise credentials_exception
            
    if user is None:
        raise credentials_exception
        
    return user

# ============ ROUTES ============

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered.")
        
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            name=request.name
        )
        db.add(new_user)
        db.flush() 
        
        # Auto-Initialize Gamification
        initial_impact = UserImpact(user_id=new_user.id, total_waste_collected=0, points=0)
        db.add(initial_impact)
        
        db.commit()
        db.refresh(new_user)
        return {"success": True, "data": {"message": "User registered successfully."}}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create user account.")

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Upgraded Login with Crash Prevention. 
    If you get a 500 error here, check your terminal logs!
    """
    client_ip = request.client.host if request.client else "Unknown"
    
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        
        # 1. Validate Password Safely
        if not user or not verify_password(form_data.password, user.password_hash):
            attempt = LoginAttempt(ip_address=client_ip, email=form_data.username, success=False)
            db.add(attempt)
            db.commit()
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        # 2. Log Success
        attempt = LoginAttempt(ip_address=client_ip, email=user.email, success=True)
        db.add(attempt)
        db.commit()

        # 3. Generate Token Safely
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": user.id or 0,
            },
        }
        
    except HTTPException:
        raise # Reraise the 401 Unauthorized normally
    except Exception as e:
        # THIS WILL CATCH YOUR 500 ERROR AND PRINT IT TO THE TERMINAL
        logger.error(f"CRITICAL LOGIN CRASH: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error during login: {str(e)}"
        )

@router.delete("/delete-account")
def delete_user_account(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    GDPR Compliance: Permanently deletes the user and all associated data.
    Requires a valid JWT token to execute.
    """
    try:
        # In SQLAlchemy, depending on your relationship setups, you may need to 
        # manually delete child records to avoid Foreign Key constraint crashes.
        db.query(WasteItem).filter(WasteItem.user_id == current_user.id).delete()
        db.query(RouteHistory).filter(RouteHistory.user_id == current_user.id).delete()
        db.query(UserImpact).filter(UserImpact.user_id == current_user.id).delete()
        db.query(LoginAttempt).filter(LoginAttempt.email == current_user.email).delete()
        db.query(PasswordReset).filter(PasswordReset.user_id == current_user.id).delete()
        
        # Finally, delete the user
        db.delete(current_user)
        db.commit()
        
        logger.info(f"User {current_user.email} securely deleted their account.")
        return {
            "success": True,
            "data": {"message": "Account and all associated data permanently deleted."},
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete account for {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete account. Please contact support.")

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return {
                "success": True,
                "data": {"message": "If the email exists, a reset link will be sent."},
            }
        
        reset_token = secrets.token_urlsafe(32)
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db.add(password_reset)
        db.commit()
        return {
            "success": True,
            "data": {"message": "If the email exists, a reset link will be sent."},
        }
    except HTTPException as exc:
        db.rollback()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error": "Request failed",
            },
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to process forgot password request.",
                "error": str(exc),
            },
        )

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == data.token,
            PasswordReset.is_used == False,
            PasswordReset.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not reset:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": "Invalid or expired reset token.",
                    "error": "Bad Request",
                },
            )
        
        user = reset.user
        user.password_hash = hash_password(data.new_password)
        reset.is_used = True
        db.commit()
        return {
            "success": True,
            "data": {"message": "Password reset successful."},
        }
    except HTTPException as exc:
        db.rollback()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error": "Request failed",
            },
        )
    except Exception as exc:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to reset password.",
                "error": str(exc),
            },
        )