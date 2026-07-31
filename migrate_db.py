from backend.shared.db.session import engine
from backend.shared.db.models import Base
import sqlalchemy as sa

def update_db():
    # Create new tables (e.g. credit_transactions)
    Base.metadata.create_all(bind=engine)
    
    # Add credits column to users
    with engine.connect() as conn:
        try:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN credits INTEGER NOT NULL DEFAULT 100;"))
            conn.commit()
            print("Added credits column.")
        except Exception as e:
            print("Column might already exist or error:", e)

if __name__ == "__main__":
    update_db()
