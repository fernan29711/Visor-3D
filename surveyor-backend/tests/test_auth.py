"""Authentication tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.db.models import User, Organization

# Test database
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

def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )
    assert response.status_code == 201
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]
    assert response.json()["user"]["email"] == "test@example.com"

def test_register_duplicate_email():
    """Test registration with duplicate email."""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )

    # Second registration with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword456",
            "first_name": "Another",
            "last_name": "User",
            "organization_name": "Another Org",
        }
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_login_success():
    """Test successful login."""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
        }
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "test@example.com"

def test_login_invalid_password():
    """Test login with invalid password."""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )

    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword",
        }
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]

def test_login_nonexistent_user():
    """Test login with non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "TestPassword123",
        }
    )
    assert response.status_code == 401

def test_refresh_token():
    """Test token refresh."""
    # Register and login
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org",
        }
    )
    refresh_token = response.json()["refresh_token"]

    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]

def test_logout():
    """Test logout."""
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
