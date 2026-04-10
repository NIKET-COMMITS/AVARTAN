from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime, timezone
import secrets

# Assuming your project structure remains as 'backend.x'
from backend.database import get_db
from backend.models import User, LoginAttempt, PasswordReset
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# --- Pydantic Schemas ---

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int

# --- Dependency ---

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), # Updated type hint here
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    user_email = verify_token(token)
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# --- Routes ---

@router.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_pass = hash_password(request.password)
    
    new_user = User(
        email=request.email,
        password_hash=hashed_pass,
        name=request.name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "user_id": new_user.id,
        "email": new_user.email,
        "message": "User registered successfully"
    }

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(request.password, user.password_hash):
        # Log the failed attempt
        attempt = LoginAttempt(
            ip_address="0.0.0.0", # Consider extracting actual IP from request
            email=request.email,
            success=False
        )
        db.add(attempt)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user_id": user.id
    }

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {
        "message": "Logged out successfully",
        "status": "success"
    }

@router.post("/token/refresh", response_model=TokenResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user_id": current_user.id
    }

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {"message": "If email exists, password reset link will be sent"}
    
    reset_token = secrets.token_urlsafe(32)
    
    password_reset = PasswordReset(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    db.add(password_reset)
    db.commit()
    
    return {"message": "If email exists, password reset link will be sent"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    # Find valid, unused, non-expired token
    reset = db.query(PasswordReset).filter(
        PasswordReset.token == token,
        PasswordReset.is_used == False,
        PasswordReset.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Update user password
    user = reset.user
    user.password_hash = hash_password(new_password)
    
    # Mark token as used
    reset.is_used = True
    
    db.commit()
    
    return {"message": "Password reset successful"}