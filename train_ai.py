from backend.database import SessionLocal, init_ml_training_data
from backend.services.ml_service import ml_service

def run_training():
    db = SessionLocal()
    try:
        print("🤖 1. Initializing synthetic ML data in database...")
        init_ml_training_data(db)
        
        print("🧠 2. Training Machine Learning Models...")
        success = ml_service.train_all_models(db)
        
        if success:
            print("✅ All models trained successfully!")
        else:
            print("❌ Training failed.")
    finally:
        db.close()

if __name__ == "__main__":
    run_training()