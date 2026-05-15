from app.db.database import engine, Base
from app.models import *

print("Initializing database...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully.")
