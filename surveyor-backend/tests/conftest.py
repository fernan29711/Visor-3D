"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    """Provide database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean database before and after each test."""
    # Clean before
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    # Clean after
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "organization_name": "Test Org",
    }

@pytest.fixture
def registered_user(client, test_user_data):
    """Register a test user and return response."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    return response

@pytest.fixture
def admin_token(client, test_user_data):
    """Create admin user and return access token."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    """Provide auth headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}
