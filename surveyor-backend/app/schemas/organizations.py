"""Organization schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrganizationCreate(BaseModel):
    """Create organization schema."""
    name: str = Field(..., min_length=1, max_length=255)
    rnc: Optional[str] = Field(None, max_length=20)
    subscription_plan: Optional[str] = Field("free", description="Subscription plan")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Agrimensura Professional",
                "rnc": "101234567",
                "subscription_plan": "professional",
            }
        }

class OrganizationUpdate(BaseModel):
    """Update organization schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    rnc: Optional[str] = Field(None, max_length=20)
    subscription_plan: Optional[str] = None

class OrganizationResponse(BaseModel):
    """Organization response schema."""
    id: str
    name: str
    rnc: Optional[str]
    logo_url: Optional[str]
    subscription_plan: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
