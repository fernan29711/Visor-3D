"""Pydantic schemas for client portal."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClientDashboardStatsResponse(BaseModel):
    """Client dashboard statistics."""
    total_quotes: int
    pending_quotes: int
    accepted_quotes: int
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    overdue_invoices: int
    total_amount_invoiced: float
    total_amount_paid: float
    total_amount_pending: float
    active_projects: int


class ClientQuoteListResponse(BaseModel):
    """Quote in client view (simplified)."""
    id: str
    quote_code: str
    project_name: str
    quote_date: datetime
    expiration_date: Optional[datetime]
    status: str
    total_amount: float
    discount_amount: float
    tax_amount: float
    subtotal_amount: float

    class Config:
        from_attributes = True


class ClientInvoiceListResponse(BaseModel):
    """Invoice in client view (simplified)."""
    id: str
    ncf: str
    project_name: str
    issue_date: datetime
    due_date: datetime
    status: str
    subtotal_amount: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    days_overdue: int

    class Config:
        from_attributes = True


class ClientProjectListResponse(BaseModel):
    """Project in client view (simplified)."""
    id: str
    project_name: str
    location: str
    status: str
    start_date: datetime
    estimated_end_date: Optional[datetime]
    total_budget: float
    total_spent: float
    progress_percentage: int
    description: Optional[str]

    class Config:
        from_attributes = True


class ClientProjectDetailResponse(BaseModel):
    """Detailed project view for client."""
    id: str
    project_name: str
    location: str
    description: Optional[str]
    status: str
    start_date: datetime
    estimated_end_date: Optional[datetime]
    total_budget: float
    total_spent: float
    progress_percentage: int

    # Associated data
    quotes_count: int
    invoices_count: int
    related_quotes: list[ClientQuoteListResponse]
    related_invoices: list[ClientInvoiceListResponse]

    class Config:
        from_attributes = True


class ClientProfileResponse(BaseModel):
    """Client profile information."""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    avatar_url: Optional[str]
    organization_name: str
    organization_website: Optional[str]

    class Config:
        from_attributes = True


class ClientQuoteDetailResponse(BaseModel):
    """Detailed quote view for client."""
    id: str
    quote_code: str
    project_name: str
    description: Optional[str]
    quote_date: datetime
    expiration_date: Optional[datetime]
    status: str

    # Items
    items: list[dict]  # Quote items

    # Totals
    subtotal_amount: float
    discount_amount: float
    discount_percentage: float
    tax_amount: float
    total_amount: float

    # Notes and attachments
    notes: Optional[str]
    terms_and_conditions: Optional[str]
    pdf_url: Optional[str]

    class Config:
        from_attributes = True


class ClientInvoiceDetailResponse(BaseModel):
    """Detailed invoice view for client."""
    id: str
    ncf: str
    project_name: str
    quote_code: Optional[str]
    invoice_date: datetime
    issue_date: datetime
    due_date: datetime
    status: str

    # Items
    items: list[dict]  # Invoice items

    # Totals
    subtotal_amount: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    remaining_amount: float

    # Payment info
    days_overdue: int
    payment_methods: list[dict]
    payment_history: list[dict]

    # Notes
    notes: Optional[str]
    pdf_url: Optional[str]

    class Config:
        from_attributes = True


class ClientPaymentResponse(BaseModel):
    """Payment information for invoice."""
    id: str
    amount: float
    payment_date: datetime
    payment_method: str
    reference: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ClientNotificationResponse(BaseModel):
    """Notification in client view."""
    id: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    action_url: Optional[str]

    class Config:
        from_attributes = True
