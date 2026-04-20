"""
Updated Database Models - Production Ready
Integrated with Profile Upgrades, AI Forensic Analysis, Enterprise Analytics.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, LargeBinary, Text, Date
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

# ============ PHASE 1 & 2: CORE MODELS ============

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    
    # --- Profile & Social Upgrades ---
    profile_photo_base64 = Column(Text, nullable=True) 
    social_links = Column(JSON, default=dict) # Stores {"instagram": "...", "twitter": "..."}
    
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
    quantity = Column(Float, nullable=False, default=1.0, index=True) # Float for KG precision
    unit = Column(String(20), default="kg")
    condition = Column(String(50)) # mint, good, fair, poor, broken
    description = Column(String(1000))
    
    # --- NEW: AI Verification Status ---
    status = Column(String(50), default="pending_action") # pending_action, verified, rejected
    
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
    total_waste_collected = Column(Float, default=0.0) # Float for KG tracking
    total_co2_saved = Column(Float, default=0.0)
    points = Column(Integer, default=0, index=True)
    
    # --- NEW: Gamified Leaderboard Fields ---
    current_tier = Column(String(50), default="Bronze")
    global_rank = Column(Integer, nullable=True) 
    last_rank_update = Column(DateTime, default=datetime.utcnow)
    
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
    """User reviews for recycling facilities"""
    __tablename__ = "facility_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    rating = Column(Float, nullable=False) # Float allows for 4.5 stars
    comment = Column(Text, nullable=True)  # Text allows for long reviews
    created_at = Column(DateTime, default=datetime.utcnow)
    
    facility = relationship("Facility", back_populates="reviews")
    user = relationship("User")


# ============ PHASE 4: MACHINE LEARNING MODELS ============

class MLTrainingData(Base):
    """Historical data for training ML models"""
    __tablename__ = "ml_training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_distance_to_facility = Column(Float)
    facility_rating = Column(Float)
    material_match_percentage = Column(Float)
    user_eco_preference = Column(Float)
    selected_facility_id = Column(Integer, ForeignKey("facilities.id"))
    selected = Column(Boolean, default=True)
    estimated_value = Column(Float)
    condition = Column(String(50))
    material_primary = Column(String(100))
    weight_grams = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class MLModel(Base):
    """Persisted trained ML models"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False)
    model_type = Column(String(50))
    accuracy_score = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    model_pickle = Column(LargeBinary)
    feature_names = Column(JSON)
    class_labels = Column(JSON)
    trained_on_samples = Column(Integer)
    training_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class RouteHistory(Base):
    """Track user's route selections for learning"""
    __tablename__ = "route_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_id = Column(Integer, ForeignKey("waste_items.id"), nullable=False)
    selected_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    predicted_facility_id = Column(Integer, ForeignKey("facilities.id"))
    distance_km = Column(Float)
    travel_time_minutes = Column(Float)
    material_value_rupees = Column(Float)
    co2_saved_kg = Column(Float)
    prediction_confidence = Column(Float)
    was_prediction_correct = Column(Boolean)
    user_satisfied = Column(Boolean)
    facility_quality_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", foreign_keys=[user_id])
    waste_item = relationship("WasteItem", foreign_keys=[waste_id])
    facility = relationship("Facility", foreign_keys=[selected_facility_id])
    predicted_facility = relationship("Facility", foreign_keys=[predicted_facility_id])


class RoutePrediction(Base):
    """ML predictions for routes"""
    __tablename__ = "route_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_id = Column(Integer, ForeignKey("waste_items.id"), nullable=False)
    top_5_facilities = Column(JSON)
    top_5_values = Column(JSON)
    top_5_co2 = Column(JSON)
    recommended_facility_id = Column(Integer)
    recommendation_confidence = Column(Float)
    predicted_value = Column(Float)
    predicted_co2_saved = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============ PHASE 5: DASHBOARD & ANALYTICS ============

class UserMetrics(Base):
    """Daily aggregated user metrics"""
    __tablename__ = "user_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    routes_completed = Column(Integer, default=0)
    co2_saved_kg = Column(Float, default=0)
    material_value_recovered = Column(Float, default=0)
    distance_traveled_km = Column(Float, default=0)
    points_earned = Column(Integer, default=0)
    current_tier = Column(String(50), default="Bronze") # UPDATED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FacilityMetrics(Base):
    """Facility performance metrics"""
    __tablename__ = "facility_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    total_routes = Column(Integer, default=0)
    total_material_processed_kg = Column(Float, default=0)
    total_value_processed = Column(Float, default=0)
    avg_rating = Column(Float, default=0)
    requests_received = Column(Integer, default=0)
    user_satisfaction_pct = Column(Float, default=0)
    operational_efficiency_pct = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserAchievement(Base):
    """User achievements and badges"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_type = Column(String(100), nullable=False)
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(String(500))
    icon = Column(String(200))
    points_awarded = Column(Integer, default=0)
    achieved_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CommunityMetrics(Base):
    """Aggregate community statistics"""
    __tablename__ = "community_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, nullable=False, unique=True, index=True)
    total_users = Column(Integer, default=0)
    total_routes = Column(Integer, default=0)
    total_co2_saved_kg = Column(Float, default=0)
    total_material_recovered_kg = Column(Float, default=0)
    total_facility_transactions = Column(Integer, default=0)
    ecosystem_health_score = Column(Float, default=0)
    avg_user_level = Column(String(50))
    most_active_category = Column(String(100))
    total_value_recovered = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardPreference(Base):
    """User dashboard preferences"""
    __tablename__ = "dashboard_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(20), default="light")
    featured_metrics = Column(JSON, default=list)
    chart_type_preference = Column(String(50), default="line")
    notifications_enabled = Column(Boolean, default=True)
    auto_report_enabled = Column(Boolean, default=False)
    auto_report_frequency = Column(String(20), default="weekly")
    refresh_interval_seconds = Column(Integer, default=300)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    report_type = Column(String(50), nullable=False)
    report_period = Column(String(50))
    report_title = Column(String(200))
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    generated_at = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(1000), nullable=False)
    related_achievement_id = Column(Integer, ForeignKey("user_achievements.id"))
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    scheduled_for = Column(DateTime)
    delivery_status = Column(String(50), default="pending")


class WasteLog(Base):
    __tablename__ = "waste_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    material = Column(String, index=True)
    weight = Column(Float, default=0.0)
    points_earned = Column(Integer, default=0)
    co2_saved = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
# ============ NEW: MARKETPLACE MODELS ============

class MarketplaceListing(Base):
    """Local peer-to-peer marketplace listings for bulk waste/scrap."""
    __tablename__ = "marketplace_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    material_type = Column(String(100), index=True)
    quantity_kg = Column(Float, nullable=False)
    price_expected = Column(Float, default=0.0)  # 0 means Free Pickup
    
    status = Column(String(50), default="active")  # active, claimed, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    seller = relationship("User", foreign_keys=[seller_id])
    buyer = relationship("User", foreign_keys=[buyer_id])

class EmailOTP(Base):
    __tablename__ = "email_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    expires_at = Column(DateTime)