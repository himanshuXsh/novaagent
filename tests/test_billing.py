def test_billing_balance(client, db_session):
    from backend.gateway.middleware.auth_guard import get_current_user
    from backend.main import app
    from backend.shared.db.models import User
    
    user = User(email="billing@test.com", name="Test User", google_id="456", credits=90)
    db_session.add(user)
    db_session.commit()
    
    def override_get_current_user():
        return {"user_id": user.id}
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    response = client.get("/api/v1/billing/balance")
    assert response.status_code == 200
    assert response.json()["credits"] == 90
    
    app.dependency_overrides.clear()
