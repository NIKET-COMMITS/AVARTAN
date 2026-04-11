from backend.database import engine
from backend.models import Base

print("Dropping and recreating all tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Database is now clean and synchronized with new models!")