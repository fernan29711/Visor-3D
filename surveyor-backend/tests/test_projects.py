"""Project endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
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

def test_create_project(admin_token, test_client_id):
    """Test creating a project."""
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
            "description": "Test description",
            "municipality": "Santo Domingo",
            "province": "Santo Domingo",
            "budget": 5000.00,
        }
    )
    assert response.status_code == 201
    assert response.json()["code"] == "PRJ-001"
    assert response.json()["status"] == "pending"

def test_list_projects(admin_token, test_client_id):
    """Test listing projects."""
    # Create project first
    client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
        }
    )

    # List projects
    response = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_project(admin_token, test_client_id):
    """Test getting project details."""
    # Create project first
    create_response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
        }
    )
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == "PRJ-001"

def test_change_project_status(admin_token, test_client_id):
    """Test changing project status."""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
        }
    )
    project_id = create_response.json()["id"]

    # Change status
    response = client.post(
        f"/api/v1/projects/{project_id}/status/in_field",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_field"
