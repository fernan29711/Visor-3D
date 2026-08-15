"""Financial service tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_financial.db"
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

def test_financial_summary(admin_token, test_client_id):
    """Test financial summary endpoint."""
    # Create invoices with different statuses
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00,
            "tax": 1800.00
        }
    )

    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200002",
            "client_id": test_client_id,
            "total": 5000.00,
            "tax": 900.00
        }
    )

    # Get summary
    response = client.get(
        "/api/v1/financial/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_issued" in data
    assert "total_paid" in data
    assert "total_pending" in data
    assert "collection_rate" in data

def test_revenue_by_month(admin_token, test_client_id):
    """Test revenue by month endpoint."""
    # Create invoice
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00,
            "tax": 1800.00
        }
    )

    response = client.get(
        "/api/v1/financial/revenue-by-month?months=12",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_payment_status_distribution(admin_token, test_client_id):
    """Test payment status distribution endpoint."""
    # Create invoices
    create_response1 = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )
    invoice_id = create_response1.json()["id"]

    # Change one to paid
    client.post(
        f"/api/v1/invoices/{invoice_id}/status/paid",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    response = client.get(
        "/api/v1/financial/payment-status-distribution",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "total" in data
    assert data["distribution"]["paid"] >= 1

def test_top_clients(admin_token, test_client_id):
    """Test top clients endpoint."""
    # Create invoices
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )

    response = client.get(
        "/api/v1/financial/top-clients?limit=5",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_quote_conversion(admin_token, test_client_id):
    """Test quote conversion endpoint."""
    # Create quote
    client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "COT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Service",
                    "quantity": 1,
                    "unit_price": 5000
                }
            ]
        }
    )

    response = client.get(
        "/api/v1/financial/quote-conversion",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_quotes" in data
    assert "conversion_rate" in data

def test_collection_forecast(admin_token, test_client_id):
    """Test collection forecast endpoint."""
    # Create invoice
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00,
            "due_days": 30
        }
    )

    response = client.get(
        "/api/v1/financial/collection-forecast?days=30",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "forecast_days" in data
    assert "expected_collection" in data
    assert "overdue_amount" in data
