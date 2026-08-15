"""Report generation tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_reports.db"
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

def test_financial_report_download(admin_token, test_client_id):
    """Test downloading financial report."""
    # Create invoices first
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
        "/api/v1/reports/financial/excel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_invoices_report_download(admin_token, test_client_id):
    """Test downloading invoices report."""
    # Create invoices
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
        "/api/v1/reports/invoices/excel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_invoices_report_with_dates(admin_token, test_client_id):
    """Test downloading invoices report with date filter."""
    # Create invoice
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )

    today = datetime.now().strftime("%Y-%m-%d")
    response = client.get(
        f"/api/v1/reports/invoices/excel?start_date=2026-01-01&end_date={today}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]

def test_quotes_report_download(admin_token, test_client_id):
    """Test downloading quotes report."""
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
        "/api/v1/reports/quotes/excel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_clients_report_download(admin_token, test_client_id):
    """Test downloading clients report."""
    response = client.get(
        "/api/v1/reports/clients/excel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0

def test_report_requires_authentication():
    """Test that reports require authentication."""
    response = client.get("/api/v1/reports/financial/excel")
    assert response.status_code == 401
