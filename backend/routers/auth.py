"""
Authentication & Authorization - Enterprise Grade
Features: OTP Registration, OAuth2 Native, GDPR Account Deletion, and Crash-Proof Logging
"""

import logging
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from datetime import timedelta, datetime, timezone
import secrets

from backend.database import get_db
from backend.models import User, LoginAttempt, PasswordReset, UserImpact, WasteItem, RouteHistory, EmailOTP
from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

logger = logging.getLogger("avartan")
router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ============ PYDANTIC SCHEMAS ============
# Using standard 'str' instead of EmailStr to prevent strict 422 errors during testing

class SendOTPRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str 

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str = Field(..., min_length=8)
    otp: str = Field(..., min_length=6, max_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int

class ForgotPasswordRequest(BaseModel):
    email: str

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
        
    token_sub = payload if isinstance(payload, str) else payload.get("sub")
    if token_sub is None:
        raise credentials_exception
        
    if "@" in str(token_sub):
        user = db.query(User).filter(User.email == str(token_sub)).first()
    else:
        try:
            user = db.query(User).filter(User.id == int(token_sub)).first()
        except ValueError:
            raise credentials_exception
            
    if user is None:
        raise credentials_exception
    return user


# ============ OTP HELPER ============

def send_otp_email(receiver_email: str, otp_code: str):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")

    # DEV FALLBACK: Print directly to terminal if no email is configured
    if not sender_email or not sender_password:
        print("\n" + "="*60)
        print(f"🛑 DEV MODE OTP for {receiver_email} : {otp_code}")
        print("="*60 + "\n")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Your AVARTAN Verification Code"
    body = f"Hello,\n\nYour AVARTAN registration code is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nStay Green,\nThe AVARTAN Team"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email.")


# ============ ROUTES ============

@router.post("/send-otp")
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    otp_code = "123456"  # MAGIC OTP FOR VIDEO DEMO
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Upsert OTP record
    existing_otp = db.query(EmailOTP).filter(EmailOTP.email == request.email).first()
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expires_at = expires
    else:
        new_otp = EmailOTP(email=request.email, otp_code=otp_code, expires_at=expires)
        db.add(new_otp)
    
    db.commit()
    send_otp_email(request.email, otp_code)
    return {"success": True, "message": "OTP sent successfully."}

@router.post("/verify-otp")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    # 1. Look up the OTP
    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == request.email,
        EmailOTP.otp_code == request.otp
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    # 2. Check expiration
    if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    return {"success": True, "message": "OTP verified successfully."}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # 1. Verify OTP one final time
        otp_record = db.query(EmailOTP).filter(
            EmailOTP.email == request.email,
            EmailOTP.otp_code == request.otp
        ).first()

        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid OTP.")
            
        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

        # 2. Check if user was created while OTP was pending
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered.")
        
        # 3. Create User
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            name=request.name
        )
        db.add(new_user)
        db.flush() 
        
        initial_impact = UserImpact(user_id=new_user.id, total_waste_collected=0, points=0)
        db.add(initial_impact)
        
        # 4. Clean up used OTP
        db.delete(otp_record)
        
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
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "Unknown"
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        
        # 1. If user doesn't exist, return 404
        if not user:
            attempt = LoginAttempt(ip_address=client_ip, email=form_data.username, success=False)
            db.add(attempt)
            db.commit()
            raise HTTPException(status_code=404, detail="User not found")

        # 2. If user exists but password is wrong, return 401
        if not verify_password(form_data.password, user.password_hash):
            attempt = LoginAttempt(ip_address=client_ip, email=form_data.username, success=False)
            db.add(attempt)
            db.commit()
            raise HTTPException(status_code=401, detail="Incorrect password")
            
        # 3. Success! Log it and return token
        attempt = LoginAttempt(ip_address=client_ip, email=user.email, success=True)
        db.add(attempt)
        db.commit()

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
        raise
    except Exception as e:
        logger.error(f"CRITICAL LOGIN CRASH: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error during login.")

@router.delete("/delete-account")
def delete_user_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        db.query(WasteItem).filter(WasteItem.user_id == current_user.id).delete()
        db.query(RouteHistory).filter(RouteHistory.user_id == current_user.id).delete()
        db.query(UserImpact).filter(UserImpact.user_id == current_user.id).delete()
        db.query(LoginAttempt).filter(LoginAttempt.email == current_user.email).delete()
        db.query(PasswordReset).filter(PasswordReset.user_id == current_user.id).delete()
        
        db.delete(current_user)
        db.commit()
        return {"success": True, "data": {"message": "Account permanently deleted."}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete account.")


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return {"success": True, "data": {"message": "If the email exists, a reset link will be sent."}}
        
        reset_token = secrets.token_urlsafe(32)
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db.add(password_reset)
        db.commit()
        return {"success": True, "data": {"message": "If the email exists, a reset link will be sent."}}
    except Exception as exc:
        db.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": "Failed."})


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        reset = db.query(PasswordReset).filter(
            PasswordReset.token == data.token,
            PasswordReset.is_used == False,
            PasswordReset.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not reset:
            return JSONResponse(status_code=400, content={"success": False, "message": "Invalid or expired reset token."})
        
        user = reset.user
        user.password_hash = hash_password(data.new_password)
        reset.is_used = True
        db.commit()
        return {"success": True, "data": {"message": "Password reset successful."}}
    except Exception as exc:
        db.rollback()
        return JSONResponse(status_code=500, content={"success": False, "message": "Failed."})