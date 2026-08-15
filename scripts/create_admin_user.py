#!/usr/bin/env python3
"""
Script to create an admin user for Surveyor SaaS
Usage: python scripts/create_admin_user.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "surveyor-backend"))

from app.db.database import SessionLocal
from app.db.models import Organization, User, UserRole
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user():
    """Create a default admin user for testing."""
    db = SessionLocal()

    try:
        # Check if admin org already exists
        admin_org = db.query(Organization).filter(
            Organization.name == "Admin Organization"
        ).first()

        if not admin_org:
            admin_org = Organization(
                id=uuid.uuid4(),
                name="Admin Organization",
                rnc="00000000000",
                subscription_plan="premium"
            )
            db.add(admin_org)
            db.commit()
            print(f"✅ Created organization: {admin_org.name}")
        else:
            print(f"ℹ️  Organization already exists: {admin_org.name}")

        # Check if admin user already exists
        admin_user = db.query(User).filter(
            User.email == "admin@surveyor.local"
        ).first()

        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                organization_id=admin_org.id,
                email="admin@surveyor.local",
                password_hash=pwd_context.hash("Admin123!@#"),
                first_name="Admin",
                last_name="User",
                role=UserRole.SUPERADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ Created admin user")
            print(f"\n📧 Email: admin@surveyor.local")
            print(f"🔐 Password: Admin123!@#")
        else:
            print(f"ℹ️  Admin user already exists")

        # Create a test client
        test_client = db.query(User).filter(
            User.email == "client@surveyor.local"
        ).first()

        if not test_client:
            test_client = User(
                id=uuid.uuid4(),
                organization_id=admin_org.id,
                email="client@surveyor.local",
                password_hash=pwd_context.hash("Client123!@#"),
                first_name="Client",
                last_name="Test",
                role=UserRole.CLIENT,
                is_active=True
            )
            db.add(test_client)
            db.commit()
            print(f"\n✅ Created test client user")
            print(f"📧 Email: client@surveyor.local")
            print(f"🔐 Password: Client123!@#")
        else:
            print(f"\nℹ️  Test client user already exists")

        print(f"\n✨ Setup complete!")
        print(f"\n📍 API Documentation: http://localhost:8000/docs")
        print(f"🌐 Frontend: http://localhost:3000")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
