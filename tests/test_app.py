import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.app import app

@pytest.mark.asyncio
async def test_root_redirect():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 200
        # Since it's a redirect to static, but in test it might serve the file
        # Actually, FastAPI TestClient handles redirects, but for async, let's use TestClient for simplicity
        # Wait, better to use TestClient for FastAPI tests as it's synchronous.

# Actually, for FastAPI, TestClient is preferred for testing, and it's synchronous.
# But since the user asked for pytest, and async, but TestClient works fine.

# Let's use TestClient

def test_root_redirect():
    client = TestClient(app, follow_redirects=False)
    response = client.get("/")
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    client = TestClient(app)
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "description" in data["Basketball Team"]

def test_signup_success():
    client = TestClient(app)
    response = client.post("/activities/Basketball Team/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Basketball Team" == data["message"]

def test_signup_already_signed_up():
    client = TestClient(app)
    # First signup
    client.post("/activities/Basketball Team/signup", params={"email": "test2@example.com"})
    # Second signup
    response = client.post("/activities/Basketball Team/signup", params={"email": "test2@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is already signed up" == data["detail"]

def test_signup_activity_not_found():
    client = TestClient(app)
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

def test_unregister_success():
    client = TestClient(app)
    # First signup
    client.post("/activities/Soccer Club/signup", params={"email": "test3@example.com"})
    # Then unregister
    response = client.post("/activities/Soccer Club/unregister", json={"email": "test3@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered test3@example.com from Soccer Club" == data["message"]

def test_unregister_not_signed_up():
    client = TestClient(app)
    response = client.post("/activities/Soccer Club/unregister", json={"email": "notsigned@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up" == data["detail"]

def test_unregister_activity_not_found():
    client = TestClient(app)
    response = client.post("/activities/Nonexistent Activity/unregister", json={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]