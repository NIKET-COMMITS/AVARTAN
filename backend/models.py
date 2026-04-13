"""
Updated Database Models - Production Ready
Includes new fields for validation and audit trail.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, LargeBinary, Text, Date
from sqlalchemy.orm import declarative_base
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

# ============ PHASE 4: MACHINE LEARNING MODELS ============

class MLTrainingData(Base):
    """Historical data for training ML models"""
    __tablename__ = "ml_training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Input features
    user_distance_to_facility = Column(Float)
    facility_rating = Column(Float)
    material_match_percentage = Column(Float)
    user_eco_preference = Column(Float)  # 0-1 (0=economy, 1=eco)
    
    # Output (what user chose)
    selected_facility_id = Column(Integer, ForeignKey("facilities.id"))
    selected = Column(Boolean, default=True)
    
    # Target value (for value predictor)
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
    model_type = Column(String(50))  # 'facility_predictor', 'value_predictor'
    
    # Model performance metrics
    accuracy_score = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    
    # Model data
    model_pickle = Column(LargeBinary)  # Serialized model
    feature_names = Column(JSON)
    class_labels = Column(JSON)
    
    # Training info
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
    
    # TWO columns point to facilities, so we must be explicit
    selected_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    predicted_facility_id = Column(Integer, ForeignKey("facilities.id"))
    
    # Route details
    distance_km = Column(Float)
    travel_time_minutes = Column(Float)
    material_value_rupees = Column(Float)
    co2_saved_kg = Column(Float)
    
    # ML metadata
    prediction_confidence = Column(Float)
    was_prediction_correct = Column(Boolean)
    
    # User feedback
    user_satisfied = Column(Boolean)
    facility_quality_rating = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # UPDATED RELATIONSHIPS: Added foreign_keys to resolve ambiguity
    user = relationship("User", foreign_keys=[user_id])
    waste_item = relationship("WasteItem", foreign_keys=[waste_id])
    
    # This specifically links 'facility' to the 'selected_facility_id' column
    facility = relationship("Facility", foreign_keys=[selected_facility_id])
    
    # Optional: You can add this if you want to access the predicted facility object too
    predicted_facility = relationship("Facility", foreign_keys=[predicted_facility_id])

class RoutePrediction(Base):
    """ML predictions for routes"""
    __tablename__ = "route_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Input
    waste_id = Column(Integer, ForeignKey("waste_items.id"), nullable=False)
    
    # Top 5 predictions
    top_5_facilities = Column(JSON)  # [{"facility_id": 1, "confidence": 0.92}, ...]
    top_5_values = Column(JSON)      # Predicted values for each
    top_5_co2 = Column(JSON)         # Predicted CO2 for each
    
    # Best option
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
    current_level = Column(String(50), default="Beginner")
    
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
    
    achievement_type = Column(String(100), nullable=False)  # badge, milestone, streak
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(String(500))
    icon = Column(String(200))  # emoji or icon path
    
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
    
    ecosystem_health_score = Column(Float, default=0)  # 0-100
    avg_user_level = Column(String(50))
    most_active_category = Column(String(100))
    total_value_recovered = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardPreference(Base):
    """User dashboard preferences"""
    __tablename__ = "dashboard_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    theme = Column(String(20), default="light")  # light, dark
    featured_metrics = Column(JSON, default=list)  # Which metrics to show
    chart_type_preference = Column(String(50), default="line")  # line, bar, pie
    
    notifications_enabled = Column(Boolean, default=True)
    auto_report_enabled = Column(Boolean, default=False)
    auto_report_frequency = Column(String(20), default="weekly")  # daily, weekly, monthly
    
    refresh_interval_seconds = Column(Integer, default=300)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    report_type = Column(String(50), nullable=False)  # pdf, csv, json
    report_period = Column(String(50))  # daily, weekly, monthly
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
    
    notification_type = Column(String(100), nullable=False)  # achievement, milestone, level_up
    title = Column(String(200), nullable=False)
    message = Column(String(1000), nullable=False)
    
    related_achievement_id = Column(Integer, ForeignKey("user_achievements.id"))
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    scheduled_for = Column(DateTime)
    delivery_status = Column(String(50), default="pending")  # pending, sent, delivered