"""Client schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ClientCreate(BaseModel):
    """Create client schema."""
    name: str = Field(..., min_length=1, max_length=255)
    client_type: str = Field("person", description="person or company")
    cedula_rnc: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Pérez Rodríguez",
                "client_type": "person",
                "cedula_rnc": "00112233445",
                "email": "juan@example.com",
                "phone": "+1-809-555-1234",
                "address": "Calle Principal 123",
                "municipality": "Santo Domingo",
                "province": "Santo Domingo",
                "notes": "Cliente VIP",
            }
        }

class ClientUpdate(BaseModel):
    """Update client schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    client_type: Optional[str] = None
    cedula_rnc: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    notes: Optional[str] = None

class ClientResponse(BaseModel):
    """Client response schema."""
    id: str
    name: str
    client_type: str
    cedula_rnc: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    municipality: Optional[str]
    province: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientListResponse(BaseModel):
    """Client list response."""
    id: str
    name: str
    client_type: str
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
