"""Invoice schemas for request/response validation."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class InvoiceCreate(BaseModel):
    """Create invoice."""
    ncf: Optional[str] = Field(None, max_length=50)
    project_id: Optional[str] = None
    client_id: str
    total: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    tax: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    due_days: int = Field(default=30, gt=0)
    notes: Optional[str] = Field(None, max_length=2000)

class InvoiceUpdate(BaseModel):
    """Update invoice."""
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)

class InvoiceResponse(BaseModel):
    """Invoice response."""
    id: str
    ncf: Optional[str]
    project_id: Optional[str]
    client_id: str
    status: str
    total: Decimal
    tax: Optional[Decimal]
    issue_date: datetime
    due_date: Optional[datetime]
    created_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True

class InvoiceListResponse(BaseModel):
    """Invoice list response."""
    id: str
    ncf: Optional[str]
    status: str
    total: Decimal
    issue_date: datetime
    due_date: Optional[datetime]

    class Config:
        from_attributes = True

class InvoiceDetailResponse(InvoiceResponse):
    """Detailed invoice response with client info."""
    client_name: Optional[str]
    project_name: Optional[str]
