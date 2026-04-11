"""
DATABASE MODELS - Define all tables

This file defines the structure of database tables.
Each class = one table.
Each Column = one field in table.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, TEXT
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Base class that all tables inherit from
Base = declarative_base()


class User(Base):
    """User accounts table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    routes = relationship("Route", back_populates="user")
    impact = relationship("UserImpact", back_populates="user", uselist=False)
    waste_items = relationship("WasteItem", back_populates="user")
    reviews = relationship("FacilityReview", back_populates="user")

class WasteItem(Base):
    """Items user wants to recycle"""
    __tablename__ = "waste_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    item_type = Column(String(100))
    quantity = Column(Integer, nullable=False, default=1)
    unit = Column(String(20), default="pieces")
    condition = Column(String(50), nullable=False)
    materials = Column(JSON)
    total_weight_grams = Column(Float)
    estimated_value = Column(Float)
    estimated_co2_saved = Column(Float)
    ai_confidence = Column(Float)
    raw_user_input = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="waste_items")


class Facility(Base):
    """Recycling facilities"""
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(20))
    website = Column(String(500))
    email = Column(String(100))
    accepts_materials = Column(JSON)
    opening_hours = Column(String(500))
    processing_capacity = Column(Float)
    rating = Column(Float, default=0)
    user_ratings_total = Column(Integer, default=0)
    overall_experience = Column(Float, default=0)
    certifications = Column(JSON)
    images = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    reviews = relationship("FacilityReview", back_populates="facility")


class FacilityReview(Base):
    """User reviews of facilities"""
    __tablename__ = "facility_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)
    title = Column(String(200))
    text = Column(String(1000))
    cleanliness = Column(Float)
    staff_behavior = Column(Float)
    pricing_fairness = Column(Float)
    processing_speed = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    facility = relationship("Facility", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Route(Base):
    """Completed recycling routes"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_id = Column(Integer, ForeignKey("waste_items.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    material_value = Column(Float)
    co2_saved = Column(Float)
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="routes")


class UserImpact(Base):
    """Environmental impact stats"""
    __tablename__ = "user_impact"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_routes_completed = Column(Integer, default=0)
    total_co2_saved_kg = Column(Float, default=0)
    total_material_value_recovered = Column(Float, default=0)
    total_distance_km = Column(Float, default=0)
    equivalent_trees_saved = Column(Float, default=0)
    equivalent_car_miles_not_driven = Column(Float, default=0)
    impact_level = Column(String(20), default="Beginner")
    environmental_score = Column(Float, default=0)
    eco_warrior = Column(Integer, default=0)
    carbon_crusher = Column(Integer, default=0)
    serial_recycler = Column(Integer, default=0)
    explorer = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="impact")


class LoginAttempt(Base):
    """Track failed login attempts (for security)"""
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    success = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)


class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)