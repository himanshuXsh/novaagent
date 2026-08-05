from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.shared.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Checks connection before using it
    pool_size=10,        # Default pool size
    max_overflow=20      # Max extra connections if pool is full
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
