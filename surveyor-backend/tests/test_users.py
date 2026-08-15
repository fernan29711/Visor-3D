"""User endpoint tests."""

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

def test_get_current_user(admin_token):
    """Test getting current user info."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert response.json()["first_name"] == "Admin"

def test_list_users(admin_token):
    """Test listing users."""
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_create_user(admin_token):
    """Test creating new user."""
    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newuser@example.com",
            "password": "NewUserPass123",
            "first_name": "New",
            "last_name": "User",
            "role": "agrimensor",
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["role"] == "agrimensor"

def test_update_user(admin_token):
    """Test updating user."""
    # Create user first
    create_response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "updateuser@example.com",
            "password": "UpdatePass123",
            "first_name": "Update",
            "last_name": "User",
            "role": "agrimensor",
        }
    )
    user_id = create_response.json()["id"]

    # Update user
    response = client.patch(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Updated",
            "last_name": "Name",
        }
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"
    assert response.json()["last_name"] == "Name"

def test_delete_user(admin_token):
    """Test deleting user."""
    # Create user first
    create_response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "deleteuser@example.com",
            "password": "DeletePass123",
            "first_name": "Delete",
            "last_name": "User",
            "role": "agrimensor",
        }
    )
    user_id = create_response.json()["id"]

    # Delete user
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

def test_delete_self_fails(admin_token):
    """Test that user cannot delete themselves."""
    response = client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code in [400, 404]
