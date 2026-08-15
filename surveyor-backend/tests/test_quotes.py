"""Quote endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_quotes.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def admin_token():
    """Create admin user and return token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "AdminPassword123",
            "first_name": "Admin",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def test_client_id(admin_token):
    """Create a test client and return ID."""
    response = client.post(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Client",
            "client_type": "person",
            "email": "client@example.com",
        }
    )
    return response.json()["id"]

def test_create_quote(admin_token, test_client_id):
    """Test creating a quote."""
    response = client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "QT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento topográfico",
                    "quantity": 1,
                    "unit_price": 5000.00,
                    "unit": "project"
                }
            ],
            "tax_percentage": 18.0,
            "discount_percentage": 0
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "QT-001"
    assert data["status"] == "draft"
    assert data["total"] > 0
    assert len(data["line_items"]) == 1

def test_list_quotes(admin_token, test_client_id):
    """Test listing quotes."""
    # Create quote first
    client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "QT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento",
                    "quantity": 1,
                    "unit_price": 5000.00
                }
            ]
        }
    )

    # List quotes
    response = client.get(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    quotes = response.json()
    assert len(quotes) >= 1
    assert quotes[0]["code"] == "QT-001"

def test_get_quote(admin_token, test_client_id):
    """Test getting quote details."""
    # Create quote
    create_response = client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "QT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento",
                    "quantity": 1,
                    "unit_price": 5000.00
                }
            ]
        }
    )
    quote_id = create_response.json()["id"]

    # Get quote
    response = client.get(
        f"/api/v1/quotes/{quote_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == "QT-001"

def test_change_quote_status(admin_token, test_client_id):
    """Test changing quote status."""
    # Create quote
    create_response = client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "QT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento",
                    "quantity": 1,
                    "unit_price": 5000.00
                }
            ]
        }
    )
    quote_id = create_response.json()["id"]

    # Change status to sent
    response = client.post(
        f"/api/v1/quotes/{quote_id}/status/sent",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sent"

def test_quote_with_multiple_line_items(admin_token, test_client_id):
    """Test creating quote with multiple line items."""
    response = client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "QT-002",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento topográfico",
                    "quantity": 1,
                    "unit_price": 5000.00
                },
                {
                    "description": "Procesamiento de datos",
                    "quantity": 1,
                    "unit_price": 2000.00
                },
                {
                    "description": "Informe técnico",
                    "quantity": 1,
                    "unit_price": 1500.00
                }
            ],
            "tax_percentage": 18.0,
            "discount_percentage": 10
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["line_items"]) == 3
    # Verify calculations
    subtotal = Decimal("8500.00")  # 5000 + 2000 + 1500
    discount = subtotal * Decimal("0.10")  # 10% discount
    after_discount = subtotal - discount
    tax = after_discount * Decimal("0.18")  # 18% tax
    expected_total = after_discount + tax
    assert data["total"] == expected_total
