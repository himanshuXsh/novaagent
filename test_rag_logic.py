import requests
import uuid
import asyncio
from backend.services.auth_service.jwt_utils import create_access_token
from backend.shared.redis_client import redis_client
from backend.shared.db.session import SessionLocal
from backend.shared.db.models import User

async def main():
    # Get or create a real user ID from DB
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(email="test@test.com", name="Test User", google_id="mock_id")
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
        
    user_id = str(user.id)
    print(f"Using test user: {user.email} (ID: {user_id})")
    
    # 1. Create a dummy user session in redis
    session_id = str(uuid.uuid4())
    await redis_client.set(f"session:{session_id}", user_id, ex=3600)
    
    token = create_access_token(data={"sub": user.email, "session_id": session_id})
    headers = {"Authorization": f"Bearer {token}"}
    
    print("--- Uploading test_rag.pdf ---")
    with open("test_rag.pdf", "rb") as f:
        files = {"file": ("test_rag.pdf", f, "application/pdf")}
        res = requests.post("http://localhost:8000/api/v1/agents/rag/upload", headers=headers, files=files)
        
    print(res.status_code)
    print(res.text)
    
    if res.status_code != 200:
        return
        
    doc_id = res.json()["document_id"]
    print(f"Uploaded successfully. Doc ID: {doc_id}")
    
    print("\n--- Test 1: Answerable Question ---")
    query_in = "What is the secret password for the mainframe?"
    print(f"Query: {query_in}")
    res_in = requests.post("http://localhost:8000/api/v1/agents/rag/query", headers=headers, json={"document_id": doc_id, "query": query_in})
    print(f"Answer: {res_in.json().get('answer')}")
    
    print("\n--- Test 2: Unanswerable Question (Similarity Fallback) ---")
    query_out = "What is the recipe for chocolate chip cookies?"
    print(f"Query: {query_out}")
    res_out = requests.post("http://localhost:8000/api/v1/agents/rag/query", headers=headers, json={"document_id": doc_id, "query": query_out})
    print(f"Answer: {res_out.json().get('answer')}")

if __name__ == "__main__":
    asyncio.run(main())
