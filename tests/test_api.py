from fastapi.testclient import TestClient
from app.main import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the simple health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}

def test_ingest_trigger():
    """Test triggering the ingestion (Mocking the background task)."""
    # We call the endpoint
    response = client.post("/ingest")
    
    # Assert the request was accepted
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "Ingestion started" in data["message"]

def test_search_empty():
    """Test searching without parameters."""
    response = client.get("/search")
    assert response.status_code == 200
    data = response.json()
    
    # It should return a list (even if empty)
    assert "count" in data
    assert isinstance(data["results"], list)

def test_search_with_query():
    """Test searching with a query parameter."""
    # We assume the DB might be empty or have data, but the call should succeed
    response = client.get("/search?q=Python")
    assert response.status_code == 200
    assert "results" in response.json()