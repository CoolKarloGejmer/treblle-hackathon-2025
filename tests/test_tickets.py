"""
Comprehensive tests for ticket management endpoints.
"""
from fastapi.testclient import TestClient
from main import app
from app.database import Base, engine, SessionLocal
from app.models import Ticket, ApiRequest
import pytest


# Ensure tables exist for the test database before creating the TestClient.
Base.metadata.create_all(bind=engine)


client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database before each test."""
    yield
    # Clean up after test
    db = SessionLocal()
    try:
        db.query(Ticket).delete()
        db.query(ApiRequest).delete()
        db.commit()
    finally:
        db.close()


# ==================== TICKET TESTS ====================

def test_create_ticket_bug():
    """Test creating a ticket that should be categorized as bug."""
    payload = {
        "title": "App error on save",
        "description": "An exception occurs when saving data",
        "reporter_email": "user@example.com"
    }
    r = client.post("/api/tickets", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] > 0
    assert data["category"] == "bug"
    assert data["priority"] in ["medium", "high"]
    assert data["status"] == "open"


def test_create_ticket_feature_request():
    """Test creating a ticket that should be categorized as feature request."""
    payload = {
        "title": "Feature: add export",
        "description": "Please add csv export functionality",
        "reporter_email": "u2@example.com"
    }
    r = client.post("/api/tickets", json=payload)
    assert r.status_code == 200
    t = r.json()
    assert t["category"] == "feature_request"


def test_get_ticket():
    """Test retrieving a single ticket by ID."""
    # Create a ticket first
    payload = {"title": "Test ticket", "description": "Test description"}
    r = client.post("/api/tickets", json=payload)
    ticket_id = r.json()["id"]

    # Get the ticket
    r2 = client.get(f"/api/tickets/{ticket_id}")
    assert r2.status_code == 200
    data = r2.json()
    assert data["id"] == ticket_id
    assert data["title"] == "Test ticket"


def test_get_nonexistent_ticket():
    """Test getting a ticket that doesn't exist."""
    r = client.get("/api/tickets/99999")
    assert r.status_code == 404


def test_list_tickets():
    """Test listing all tickets."""
    # Create multiple tickets
    client.post("/api/tickets", json={"title": "Bug 1", "description": "error here"})
    client.post("/api/tickets", json={"title": "Feature 1", "description": "add feature"})

    r = client.get("/api/tickets")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2


def test_list_tickets_filter_by_category():
    """Test filtering tickets by category."""
    client.post("/api/tickets", json={"title": "Bug report", "description": "exception found"})
    client.post("/api/tickets", json={"title": "Feature request", "description": "add export"})

    r = client.get("/api/tickets?category=bug")
    assert r.status_code == 200
    items = r.json()
    assert all(item["category"] == "bug" for item in items)


def test_search_tickets():
    """Test searching tickets by text."""
    client.post("/api/tickets", json={"title": "Payment issue", "description": "Can't process payment"})
    client.post("/api/tickets", json={"title": "Login problem", "description": "Can't log in"})

    r = client.get("/api/tickets/search?search=payment")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any("payment" in item["title"].lower() or "payment" in item["description"].lower()
               for item in data["items"])


def test_search_tickets_with_filters():
    """Test searching tickets with multiple filters."""
    # Create tickets
    client.post("/api/tickets", json={"title": "Critical bug", "description": "urgent error"})
    client.post("/api/tickets", json={"title": "Minor feature", "description": "add nice feature"})

    r = client.get("/api/tickets/search?category=bug&sort_by=created_at&sort_order=desc")
    assert r.status_code == 200
    data = r.json()
    assert all(item["category"] == "bug" for item in data["items"])


def test_search_tickets_pagination():
    """Test pagination in search."""
    # Create multiple tickets
    for i in range(5):
        client.post("/api/tickets", json={"title": f"Ticket {i}", "description": f"Description {i}"})

    r = client.get("/api/tickets/search?limit=2&skip=0")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5


def test_update_ticket():
    """Test updating a ticket."""
    # Create a ticket
    r = client.post("/api/tickets", json={"title": "Original title", "description": "Original description"})
    ticket_id = r.json()["id"]

    # Update the ticket
    update_data = {
        "title": "Updated title",
        "priority": "high",
        "status": "open"
    }
    r2 = client.patch(f"/api/tickets/{ticket_id}", json=update_data)
    assert r2.status_code == 200
    updated = r2.json()
    assert updated["title"] == "Updated title"
    assert updated["priority"] == "high"


def test_update_nonexistent_ticket():
    """Test updating a ticket that doesn't exist."""
    r = client.patch("/api/tickets/99999", json={"title": "New title"})
    assert r.status_code == 404


def test_delete_ticket():
    """Test deleting a ticket."""
    # Create a ticket
    r = client.post("/api/tickets", json={"title": "To be deleted", "description": "Delete me"})
    ticket_id = r.json()["id"]

    # Delete the ticket
    r2 = client.delete(f"/api/tickets/{ticket_id}")
    assert r2.status_code == 200

    # Verify it's deleted
    r3 = client.get(f"/api/tickets/{ticket_id}")
    assert r3.status_code == 404


def test_delete_nonexistent_ticket():
    """Test deleting a ticket that doesn't exist."""
    r = client.delete("/api/tickets/99999")
    assert r.status_code == 404


def test_resolve_ticket():
    """Test resolving a ticket."""
    # Create a ticket
    r = client.post("/api/tickets", json={"title": "Issue", "description": "Problem here"})
    ticket_id = r.json()["id"]

    # Resolve it
    r2 = client.post(f"/api/tickets/{ticket_id}/resolve")
    assert r2.status_code == 200
    resolved = r2.json()
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None


def test_resolve_nonexistent_ticket():
    """Test resolving a ticket that doesn't exist."""
    r = client.post("/api/tickets/99999/resolve")
    assert r.status_code == 404


# ==================== API REQUEST TESTS ====================

def test_create_api_request():
    """Test creating an API request record."""
    payload = {
        "method": "GET",
        "path": "/api/users",
        "response_code": 200,
        "response_time": 0.123,
        "user_agent": "Mozilla/5.0",
        "ip_address": "192.168.1.1"
    }
    r = client.post("/api/requests", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] > 0
    assert data["method"] == "GET"
    assert data["response_code"] == 200


def test_create_api_request_minimal():
    """Test creating an API request with minimal data."""
    payload = {
        "method": "POST",
        "path": "/api/tickets",
        "response_code": 201,
        "response_time": 0.056
    }
    r = client.post("/api/requests", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["method"] == "POST"


def test_get_api_request():
    """Test retrieving a single API request by ID."""
    # Create a request first
    payload = {
        "method": "GET",
        "path": "/test",
        "response_code": 200,
        "response_time": 0.1
    }
    r = client.post("/api/requests", json=payload)
    request_id = r.json()["id"]

    # Get the request
    r2 = client.get(f"/api/requests/{request_id}")
    assert r2.status_code == 200
    data = r2.json()
    assert data["id"] == request_id


def test_get_nonexistent_api_request():
    """Test getting an API request that doesn't exist."""
    r = client.get("/api/requests/99999")
    assert r.status_code == 404


def test_list_api_requests():
    """Test listing API requests."""
    # Create multiple requests
    client.post("/api/requests", json={"method": "GET", "path": "/api/test1", "response_code": 200, "response_time": 0.1})
    client.post("/api/requests", json={"method": "POST", "path": "/api/test2", "response_code": 201, "response_time": 0.2})

    r = client.get("/api/requests")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_filter_api_requests_by_method():
    """Test filtering API requests by HTTP method."""
    client.post("/api/requests", json={"method": "GET", "path": "/test", "response_code": 200, "response_time": 0.1})
    client.post("/api/requests", json={"method": "POST", "path": "/test", "response_code": 201, "response_time": 0.2})

    r = client.get("/api/requests?method=GET")
    assert r.status_code == 200
    data = r.json()
    assert all(item["method"] == "GET" for item in data["items"])


def test_filter_api_requests_by_response_code():
    """Test filtering API requests by response code."""
    client.post("/api/requests", json={"method": "GET", "path": "/test", "response_code": 200, "response_time": 0.1})
    client.post("/api/requests", json={"method": "GET", "path": "/test", "response_code": 404, "response_time": 0.05})

    r = client.get("/api/requests?response_code=404")
    assert r.status_code == 200
    data = r.json()
    assert all(item["response_code"] == 404 for item in data["items"])


def test_filter_api_requests_by_response_time():
    """Test filtering API requests by response time range."""
    client.post("/api/requests", json={"method": "GET", "path": "/fast", "response_code": 200, "response_time": 0.05})
    client.post("/api/requests", json={"method": "GET", "path": "/slow", "response_code": 200, "response_time": 0.5})

    r = client.get("/api/requests?min_response_time=0.1&max_response_time=1.0")
    assert r.status_code == 200
    data = r.json()
    assert all(0.1 <= item["response_time"] <= 1.0 for item in data["items"])


def test_filter_api_requests_by_path():
    """Test filtering API requests by path."""
    client.post("/api/requests", json={"method": "GET", "path": "/api/users", "response_code": 200, "response_time": 0.1})
    client.post("/api/requests", json={"method": "GET", "path": "/api/tickets", "response_code": 200, "response_time": 0.1})

    r = client.get("/api/requests?path_contains=users")
    assert r.status_code == 200
    data = r.json()
    assert all("users" in item["path"] for item in data["items"])


def test_sort_api_requests_by_response_time():
    """Test sorting API requests by response time."""
    client.post("/api/requests", json={"method": "GET", "path": "/test1", "response_code": 200, "response_time": 0.3})
    client.post("/api/requests", json={"method": "GET", "path": "/test2", "response_code": 200, "response_time": 0.1})
    client.post("/api/requests", json={"method": "GET", "path": "/test3", "response_code": 200, "response_time": 0.2})

    r = client.get("/api/requests?sort_by=response_time&sort_order=asc")
    assert r.status_code == 200
    data = r.json()
    times = [item["response_time"] for item in data["items"]]
    assert times == sorted(times)


def test_api_requests_pagination():
    """Test pagination for API requests."""
    # Create multiple requests
    for i in range(5):
        client.post("/api/requests", json={"method": "GET", "path": f"/test{i}", "response_code": 200, "response_time": 0.1})

    r = client.get("/api/requests?limit=2&skip=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5


# ==================== HEALTH CHECK TESTS ====================

def test_root_endpoint():
    """Test root endpoint."""
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
