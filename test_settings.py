import requests
import uuid
import asyncio
from backend.services.auth_service.jwt_utils import create_access_token
from backend.shared.redis_client import redis_client
from backend.shared.db.session import SessionLocal
from backend.shared.db.models import User

async def main():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(email="test@test.com", name="Test User", google_id="mock_id")
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    
    session_id = str(uuid.uuid4())
    await redis_client.set(f"session:{session_id}", str(user.id), ex=3600)
    
    token = create_access_token(data={"sub": user.email, "session_id": session_id})
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get current name
    res1 = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
    print("Initial Profile:", res1.json())
    
    # 2. Patch new name
    print("\n--- Patching name ---")
    new_name = f"Updated Name {uuid.uuid4().hex[:4]}"
    res2 = requests.patch("http://localhost:8000/api/v1/auth/me", headers=headers, json={"name": new_name})
    print("Patch Status:", res2.status_code)
    print("Patch Response:", res2.json())
    
    # 3. Get new name to confirm persistence
    res3 = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
    print("Profile after patch:", res3.json())
    
    if res3.json()["name"] == new_name:
        print("\n✅ Name successfully persisted!")
    else:
        print("\n❌ Name did not persist.")

if __name__ == "__main__":
    asyncio.run(main())
