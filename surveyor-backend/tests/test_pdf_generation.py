"""PDF generation service tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.main import app
from app.db.database import Base, get_db
from app.services.pdf_service import PDFService

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_pdf.db"
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

def test_quote_pdf_generation():
    """Test PDF generation for quote."""
    quote_data = {
        "id": "quote-123",
        "code": "COT-001",
        "client_name": "Test Client",
        "client_email": "client@example.com",
        "created_at": "2026-08-15",
        "status": "draft",
        "valid_until": "2026-09-15",
        "line_items": [
            {
                "description": "Levantamiento topográfico básico",
                "quantity": 1,
                "unit_price": Decimal("5000.00"),
                "subtotal": Decimal("5000.00")
            },
            {
                "description": "Procesamiento de datos",
                "quantity": 1,
                "unit_price": Decimal("2000.00"),
                "subtotal": Decimal("2000.00")
            }
        ],
        "subtotal": Decimal("7000.00"),
        "discount": Decimal("700.00"),
        "tax": Decimal("1134.00"),
        "total": Decimal("7434.00"),
        "notes": "Incluye procesamiento básico"
    }

    pdf_buffer = PDFService.generate_quote_pdf(quote_data)
    assert pdf_buffer is not None
    pdf_data = pdf_buffer.read()
    assert len(pdf_data) > 0
    assert pdf_data[:4] == b'%PDF'

def test_invoice_pdf_generation():
    """Test PDF generation for invoice."""
    invoice_data = {
        "id": "invoice-123",
        "ncf": "F01200001",
        "client_name": "Test Client",
        "client_email": "client@example.com",
        "project_name": "Proyecto Test",
        "issue_date": "2026-08-15",
        "due_date": "2026-09-15",
        "status": "draft",
        "subtotal": Decimal("10000.00"),
        "tax": Decimal("1800.00"),
        "total": Decimal("11800.00"),
    }

    pdf_buffer = PDFService.generate_invoice_pdf(invoice_data)
    assert pdf_buffer is not None
    pdf_data = pdf_buffer.read()
    assert len(pdf_data) > 0
    assert pdf_data[:4] == b'%PDF'

def test_quote_pdf_download_endpoint(admin_token, test_client_id):
    """Test downloading quote PDF via endpoint."""
    # Create quote
    create_response = client.post(
        "/api/v1/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "COT-001",
            "client_id": test_client_id,
            "line_items": [
                {
                    "description": "Levantamiento",
                    "quantity": 1,
                    "unit_price": 5000
                }
            ]
        }
    )
    quote_id = create_response.json()["id"]

    # Download PDF
    response = client.get(
        f"/api/v1/quotes/{quote_id}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert b'%PDF' in response.content[:10]

def test_invoice_pdf_download_endpoint(admin_token, test_client_id):
    """Test downloading invoice PDF via endpoint."""
    # Create invoice
    create_response = client.post(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "ncf": "F01200001",
            "client_id": test_client_id,
            "total": 10000.00,
            "tax": 1800.00
        }
    )
    invoice_id = create_response.json()["id"]

    # Download PDF
    response = client.get(
        f"/api/v1/invoices/{invoice_id}/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert b'%PDF' in response.content[:10]
