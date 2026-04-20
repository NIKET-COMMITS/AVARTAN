"""
Database Seeder - Populates the app with realistic dummy users and leaderboard stats.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import random

from backend.database import SessionLocal, engine
from backend.models import Base, User, UserImpact
from backend.security import hash_password

# Ensure all tables are created
Base.metadata.create_all(bind=engine)

def determine_tier(points):
    if points < 500: return "Bronze"
    if points < 1500: return "Silver"
    if points < 5000: return "Gold"
    if points < 10000: return "Platinum"
    return "Eco-Warrior"

def seed_database():
    db: Session = SessionLocal()
    
    # 1. Realistic Local Users (Gandhinagar / Gujarat demographic)
   # 1. Realistic Local Users (Launch Week Stats)
    fake_users = [
        {"name": "Aarav Patel", "email": "aarav.p@example.com", "points": 1450, "waste": 24.5, "co2": 41.2},
        {"name": "Priya Sharma", "email": "priya.s@example.com", "points": 980, "waste": 18.0, "co2": 32.8},
        {"name": "Rahul Desai", "email": "rahul.d@example.com", "points": 745, "waste": 14.2, "co2": 25.4},
        {"name": "Neha Mehta", "email": "neha.m@example.com", "points": 512, "waste": 9.5, "co2": 18.1},
        {"name": "Vikram Singh", "email": "vikram.s@example.com", "points": 489, "waste": 8.8, "co2": 16.5},
        {"name": "Anjali Joshi", "email": "anjali.j@example.com", "points": 320, "waste": 6.4, "co2": 11.2},
        {"name": "Karan Shah", "email": "karan.s@example.com", "points": 215, "waste": 4.1, "co2": 7.8},
        {"name": "Pooja Trivedi", "email": "pooja.t@example.com", "points": 134, "waste": 2.8, "co2": 4.5},
        {"name": "Suresh Patel", "email": "suresh.p@example.com", "points": 89, "waste": 1.5, "co2": 2.5},
        {"name": "Riya Chauhan", "email": "riya.c@example.com", "points": 42, "waste": 0.8, "co2": 1.2},
    ]
    print("🌱 Seeding database with realistic users...")

    users_added = 0
    for data in fake_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == data["email"]).first()
        if not existing_user:
            # Create User
            new_user = User(
                email=data["email"],
                name=data["name"],
                password_hash=hash_password("SecurePass123!"), # Standard dummy password
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_user)
            db.flush() # Get the new_user.id

            # Create UserImpact (Leaderboard Stats)
            new_impact = UserImpact(
                user_id=new_user.id,
                total_waste_collected=data["waste"],
                total_co2_saved=data["co2"],
                points=data["points"],
                current_tier=determine_tier(data["points"])
            )
            db.add(new_impact)
            users_added += 1

    db.commit()
    db.close()

    if users_added > 0:
        print(f"✅ Successfully added {users_added} active users to the Leaderboard!")
        print("🏆 Go check your Dashboard, it should look incredibly active now.")
    else:
        print("⚠️ Users already exist in the database. No new users added.")

if __name__ == "__main__":
    seed_database()