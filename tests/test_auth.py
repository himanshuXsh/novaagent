def test_auth_me(client, db_session):
    from backend.gateway.middleware.auth_guard import get_current_user
    from backend.main import app
    from backend.shared.db.models import User
    
    user = User(email="test@test.com", name="Test User", google_id="123")
    db_session.add(user)
    db_session.commit()
    
    def override_get_current_user():
        return {"user_id": user.id}
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"
    
    response2 = client.patch("/api/v1/auth/me", json={"name": "New Name"})
    assert response2.status_code == 200
    assert response2.json()["name"] == "New Name"
    
    app.dependency_overrides.clear()
