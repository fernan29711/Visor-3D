"""Quote schemas for request/response validation."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class QuoteLineItemCreate(BaseModel):
    """Create quote line item."""
    description: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    unit: str = Field(default="unit", max_length=50)

class QuoteLineItem(QuoteLineItemCreate):
    """Quote line item response."""
    id: Optional[str] = None
    subtotal: Decimal

    class Config:
        from_attributes = True

class QuoteCreate(BaseModel):
    """Create quote."""
    code: str = Field(..., min_length=1, max_length=50)
    client_id: str
    line_items: List[QuoteLineItemCreate] = Field(..., min_items=1)
    tax_percentage: float = Field(default=18.0, ge=0, le=100)
    discount_percentage: float = Field(default=0, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=2000)
    valid_days: int = Field(default=30, gt=0)

class QuoteUpdate(BaseModel):
    """Update quote."""
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    valid_days: Optional[int] = Field(None, gt=0)

class QuoteResponse(BaseModel):
    """Quote response."""
    id: str
    code: str
    client_id: str
    status: str
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    valid_until: datetime
    created_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True

class QuoteDetailResponse(QuoteResponse):
    """Detailed quote response with line items."""
    line_items: List[QuoteLineItem]
    client_name: Optional[str]
    client_email: Optional[str]

class QuoteListResponse(BaseModel):
    """Quote list response."""
    id: str
    code: str
    client_id: str
    status: str
    total: Decimal
    valid_until: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class QuotePDFRequest(BaseModel):
    """Request to generate quote PDF."""
    quote_id: str
    include_terms: bool = False

class QuoteStatusUpdate(BaseModel):
    """Update quote status."""
    status: str = Field(..., pattern="^(draft|sent|accepted|rejected|expired)$")
