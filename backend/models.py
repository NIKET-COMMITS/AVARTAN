"""
Updated Database Models - Production Ready
Includes new fields for validation and audit trail.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    routes = relationship("Route", back_populates="user")
    impact = relationship("UserImpact", back_populates="user", uselist=False)


class WasteItem(Base):
    __tablename__ = "waste_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Item details
    item_name = Column(String(200), nullable=False)
    item_type = Column(String(100))
    quantity = Column(Integer, nullable=False, default=1, index=True)
    unit = Column(String(20), default="pieces")
    condition = Column(String(50)) # mint, good, fair, poor, broken
    description = Column(String(1000))
    
    # AI Analysis Data
    confidence_score = Column(Float)
    estimated_value = Column(Float)
    estimated_co2_saved = Column(Float)
    material_composition = Column(JSON) # e.g., {"plastic": 60, "metal": 40}
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_point = Column(String(255))
    end_point = Column(String(255))
    distance_km = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="routes")


class UserImpact(Base):
    __tablename__ = "user_impact"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_waste_collected = Column(Integer, default=0)
    total_co2_saved = Column(Float, default=0.0)
    points = Column(Integer, default=0)
    
    # Badges/Achievements
    green_warrior = Column(Integer, default=0)
    serial_recycler = Column(Integer, default=0)
    explorer = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="impact")


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    success = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)


class PasswordReset(Base):
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Security: Track all important actions for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    details = Column(String(500))
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# ============ PHASE 3: FACILITY MODELS ============
from sqlalchemy import Float, Boolean, JSON

class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(1000))
    address = Column(String(500), nullable=False)
    city = Column(String(100), index=True)
    pincode = Column(String(10))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(20))
    is_open = Column(Boolean, default=True)
    materials_accepted = Column(JSON)
    rating = Column(Float, default=0)
    total_reviews = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship("FacilityReview", back_populates="facility", cascade="all, delete-orphan")

class FacilityReview(Base):
    __tablename__ = "facility_reviews"
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    text = Column(String(2000))
    overall_rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    facility = relationship("Facility", back_populates="reviews")
    user = relationship("User")