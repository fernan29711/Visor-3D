"""User schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Create user schema."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field("agrimensor", description="User role")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "agrimensor@example.com",
                "password": "SecurePass123",
                "first_name": "Carlos",
                "last_name": "Rodríguez",
                "role": "agrimensor",
            }
        }

class UserUpdate(BaseModel):
    """Update user schema."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """User list response."""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
