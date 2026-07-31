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
    
    # 1. Get Balance
    res1 = requests.get("http://localhost:8000/api/v1/billing/balance", headers=headers)
    print("Initial Balance:", res1.json())
    initial_credits = res1.json()["credits"]
    
    # 2. Successful chat
    print("\n--- Successful Chat Call ---")
    res2 = requests.post("http://localhost:8000/api/v1/chat/message", headers=headers, json={"content": "Hello", "agent_type": "chat"})
    print("Chat Status:", res2.status_code)
    
    # 3. Get Balance
    res3 = requests.get("http://localhost:8000/api/v1/billing/balance", headers=headers)
    print("Balance after success:", res3.json())
    
    # 4. Failed chat
    print("\n--- Failed Chat Call ---")
    res4 = requests.post("http://localhost:8000/api/v1/chat/message", headers=headers, json={}) # Missing required field
    print("Chat Status:", res4.status_code)
    
    # 5. Get Balance
    res5 = requests.get("http://localhost:8000/api/v1/billing/balance", headers=headers)
    print("Balance after failure:", res5.json())

if __name__ == "__main__":
    asyncio.run(main())
