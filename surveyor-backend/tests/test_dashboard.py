"""Dashboard endpoints tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_dashboard.db"
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

def test_get_projects_summary(admin_token, test_client_id):
    """Test getting project summary."""
    # Create projects with different statuses
    client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project 1",
            "client_id": test_client_id,
        }
    )

    client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-002",
            "name": "Test Project 2",
            "client_id": test_client_id,
        }
    )

    # Get summary
    response = client.get(
        "/api/v1/projects/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert 'total_projects' in data
    assert 'total_clients' in data
    assert 'total_survey_points' in data
    assert data['total_projects'] == 2
    assert data['total_clients'] == 1

def test_projects_summary_counts_survey_points(admin_token, test_client_id):
    """Test that summary correctly counts survey points."""
    # Create project
    project_response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "PRJ-001",
            "name": "Test Project",
            "client_id": test_client_id,
        }
    )
    project_id = project_response.json()["id"]

    # Import survey points
    client.post(
        f"/api/v1/projects/{project_id}/survey-points/bulk/import",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "points": [
                {
                    "point_number": "P-001",
                    "east": 327845.236,
                    "north": 2165487.421,
                    "elevation": 82.436
                },
                {
                    "point_number": "P-002",
                    "east": 327850.123,
                    "north": 2165490.456,
                    "elevation": 83.120
                }
            ]
        }
    )

    # Get summary
    response = client.get(
        "/api/v1/projects/summary",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['total_survey_points'] == 2
