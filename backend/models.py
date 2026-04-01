# UNDERSTANDING: This file defines database tables using SQLAlchemy

# ============== IMPORTS ==============
# Import what we need to create tables

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
# Column = field in table
# Integer, String, Float, etc = data types
# DateTime = date and time
# JSON = flexible data (lists, dicts)
# ForeignKey = link to other table

from sqlalchemy.ext.declarative import declarative_base
# This creates base class that all tables inherit from
# It tells SQLAlchemy: "Classes inheriting from this are database tables"

from sqlalchemy.orm import relationship
# relationship = connection between tables
# Example: User has many Routes

from datetime import datetime
# For timestamps (created_at, updated_at)


# ============== BASE CLASS ==============

Base = declarative_base()
# All table classes inherit from Base
# This tells SQLAlchemy they're tables


# ============== USER TABLE ==============

class User(Base):
    """
    WHAT: Stores user account information
    WHY: We need to know who is using the app
    
    Columns:
    - id: Unique identifier
    - email: Login identifier
    - password_hash: Hashed password (never store plain!)
    - name: User's name
    - latitude, longitude: User's location
    - created_at: When account was created
    - updated_at: Last time user updated
    """
    
    __tablename__ = "users"  # Database table name
    
    # Column 1: ID (Primary Key)
    # PRIMARY KEY = unique identifier
    # AUTO_INCREMENT = automatically increases (1, 2, 3...)
    # INDEX = makes queries faster
    id = Column(Integer, primary_key=True, index=True)
    
    # Column 2: Email
    # String(100) = text up to 100 characters
    # UNIQUE = no two users can have same email
    # NULLABLE=FALSE = must provide email
    # INDEX = makes email lookup fast
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Column 3: Password Hash
    # String(255) = long string (hashes are long)
    # NULLABLE=FALSE = every user must have password
    # NOTE: Never store plain password!
    password_hash = Column(String(255), nullable=False)
    
    # Column 4: Name
    # Optional (nullable=True by default)
    name = Column(String(100))
    
    # Columns 5-6: Location
    # For finding nearby facilities
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Column 7-8: Timestamps
    # AUTO-SET to current time
    # created_at = never changes
    # updated_at = updates when user changes data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS (one-to-many)
    # A user has multiple routes
    # This creates relationship (not actual database column)
    # back_populates = reverse relationship
    routes = relationship("Route", back_populates="user")
    
    # A user has one impact record
    impact = relationship("UserImpact", back_populates="user", uselist=False)


# ============== WASTE ITEM TABLE ==============

class WasteItem(Base):
    """
    WHAT: What the user wants to recycle
    WHY: We need to know what waste to optimize routes for
    """
    
    __tablename__ = "waste_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # FOREIGN KEY: Links to users table
    # ForeignKey("users.id") = points to User.id
    # This means: "Every waste_item belongs to one user"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # What item is it?
    item_name = Column(String(200), nullable=False)
    
    # What category? (Electronics, Metal, etc)
    item_type = Column(String(100))
    
    # How many items?
    quantity = Column(Integer, nullable=False, default=1)
    
    # Unit: pieces, kg, grams, batch
    unit = Column(String(20), default="pieces")
    
    # Condition: mint, good, fair, poor, broken
    condition = Column(String(50), nullable=False)
    
    # MATERIALS in JSON format
    # Example: {"copper": 3, "gold": 0.034, "aluminum": 100}
    # JSON = flexible (different items have different materials)
    materials = Column(JSON)
    
    # Total weight in grams (standardized)
    total_weight_grams = Column(Float)
    
    # How much is this worth?
    estimated_value = Column(Float)
    
    # How much CO2 will be saved?
    estimated_co2_saved = Column(Float)
    
    # User input before AI processing
    ai_confidence = Column(Float)
    raw_user_input = Column(String(1000))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship back to User
    user = relationship("User")


# ============== FACILITY TABLE ==============

class Facility(Base):
    """
    WHAT: Recycling facilities where waste goes
    WHY: We need to rank and recommend facilities
    """
    
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    
    # Location (GPS coordinates)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Contact
    phone = Column(String(20))
    website = Column(String(500))
    email = Column(String(100))
    
    # What materials can it process?
    # JSON array: ["copper", "aluminum", "gold"]
    accepts_materials = Column(JSON)
    
    # Hours of operation
    opening_hours = Column(String(500))
    
    # How much can process per day (kg)?
    processing_capacity = Column(Float)
    
    # Quality ratings
    rating = Column(Float, default=0)  # 1-5 stars
    user_ratings_total = Column(Integer, default=0)
    overall_experience = Column(Float, default=0)
    
    # Certifications: ISO 14001, E-Stewards, etc
    certifications = Column(JSON)
    
    # Images/photos
    images = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    reviews = relationship("FacilityReview", back_populates="facility")


# ============== FACILITY REVIEW TABLE ==============

class FacilityReview(Base):
    """
    WHAT: Users review facilities they've visited
    WHY: Help other users find good facilities
    """
    
    __tablename__ = "facility_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Overall rating
    rating = Column(Float, nullable=False)  # 1-5
    
    # Review text
    title = Column(String(200))
    text = Column(String(1000))
    
    # Specific aspects (1-5 scale)
    cleanliness = Column(Float)
    staff_behavior = Column(Float)
    pricing_fairness = Column(Float)
    processing_speed = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    facility = relationship("Facility", back_populates="reviews")
    user = relationship("User")


# ============== ROUTE TABLE ==============

class Route(Base):
    """
    WHAT: User completed a recycling route
    WHY: Track what routes users take, calculate impact
    """
    
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (connects to other tables)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_id = Column(Integer, ForeignKey("waste_items.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    
    # Route details
    distance_km = Column(Float, nullable=False)
    material_value = Column(Float)
    co2_saved = Column(Float)
    
    # When was it done?
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="routes")


# ============== USER IMPACT TABLE ==============

class UserImpact(Base):
    """
    WHAT: Cumulative environmental impact of user
    WHY: Show users how much good they're doing
    """
    
    __tablename__ = "user_impact"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Each user has one impact record
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Cumulative statistics
    total_routes_completed = Column(Integer, default=0)
    total_co2_saved_kg = Column(Float, default=0)
    total_material_value_recovered = Column(Float, default=0)
    total_distance_km = Column(Float, default=0)
    
    # Environmental metrics
    equivalent_trees_saved = Column(Float, default=0)
    equivalent_car_miles_not_driven = Column(Float, default=0)
    
    # Scoring
    impact_level = Column(String(20), default="Beginner")  # Beginner → Expert
    environmental_score = Column(Float, default=0)  # 0-100
    
    # Badges earned
    eco_warrior = Column(Integer, default=0)
    carbon_crusher = Column(Integer, default=0)
    serial_recycler = Column(Integer, default=0)
    explorer = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="impact")


# ============== LOGIN ATTEMPT TABLE ==============

class LoginAttempt(Base):
    """
    WHAT: Track failed login attempts
    WHY: Prevent brute force attacks (too many wrong passwords)
    """
    
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who tried to login?
    ip_address = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    
    # Was it successful?
    success = Column(Boolean, default=False)
    
    # When?
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============== PASSWORD RESET TABLE ==============

class PasswordReset(Base):
    """
    WHAT: Password reset tokens
    WHY: Allow users to reset password via email
    
    Process:
    1. User clicks "Forgot password"
    2. System creates random token
    3. Sends token in email link
    4. User clicks link with token
    5. User enters new password
    6. System validates token and updates password
    """
    
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Whose password reset?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Random token in email link
    # Example: abc123def456xyz789abc123def456xyz789
    token = Column(String(500), unique=True, nullable=False)
    
    # When does token expire?
    # Tokens only valid for 1 hour
    expires_at = Column(DateTime, nullable=False)
    
    # Was it already used?
    # User can only use reset link once
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# SUMMARY OF TABLES:
# users - user accounts
# waste_items - items to recycle
# facilities - recycling centers
# facility_reviews - ratings of facilities
# routes - completed recycling routes
# user_impact - environmental impact stats
# login_attempts - security tracking
# password_resets - password reset tokens
#
# RELATIONSHIPS:
# User → many Routes
# User → one UserImpact
# WasteItem → one User
# Facility → many Reviews
# Route → User, WasteItem, Facility 