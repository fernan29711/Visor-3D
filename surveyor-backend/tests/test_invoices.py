"""Invoice endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_invoices.db"
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

@pytest.fixture
def test_project_id(admin_token, test_client_id):
    """Create a test project and return ID."""
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
        }
    )
    return response.json()["id"]

def test_create_invoice(admin_token, test_client_id):
    """Test creating an invoice."""
    response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00,
            "tax": 1800.00,
            "due_days": 30
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ncf"] == "F01200001"
    assert data["status"] == "draft"
    assert data["total"] == 10000.00

def test_list_invoices(admin_token, test_client_id):
    """Test listing invoices."""
    # Create invoice first
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

    # List invoices
    response = client.get(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    invoices = response.json()
    assert len(invoices) >= 1
    assert invoices[0]["ncf"] == "F01200001"

def test_get_invoice(admin_token, test_client_id):
    """Test getting invoice details."""
    # Create invoice
    create_response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )
    invoice_id = create_response.json()["id"]

    # Get invoice
    response = client.get(
        f"/api/v1/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["ncf"] == "F01200001"

def test_change_invoice_status(admin_token, test_client_id):
    """Test changing invoice status."""
    # Create invoice
    create_response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )
    invoice_id = create_response.json()["id"]

    # Change status to sent
    response = client.post(
        f"/api/v1/invoices/{invoice_id}/status/sent",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sent"

def test_invoice_with_project(admin_token, test_client_id, test_project_id):
    """Test creating invoice associated with a project."""
    response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "project_id": test_project_id,
            "client_id": test_client_id,
            "total": 10000.00,
            "tax": 1800.00
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == test_project_id

def test_get_invoices_summary(admin_token, test_client_id):
    """Test getting invoices summary."""
    # Create several invoices with different statuses
    create_response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00
        }
    )
    invoice_id = create_response.json()["id"]

    # Change one to paid
    client.post(
        f"/api/v1/invoices/{invoice_id}/status/paid",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Create another draft
    client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200002",
            "client_id": test_client_id,
            "total": 5000.00
        }
    )

    # Get summary
    response = client.get(
        "/api/v1/invoices/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_invoices"] == 2
    assert data["paid"] >= 1
    assert data["draft"] >= 1
