"""Webhook schemas."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class WebhookEventType(str, Enum):
    """Webhook event types."""
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_COMPLETED = "project.completed"
    QUOTE_CREATED = "quote.created"
    QUOTE_SENT = "quote.sent"
    QUOTE_ACCEPTED = "quote.accepted"
    QUOTE_REJECTED = "quote.rejected"
    INVOICE_CREATED = "invoice.created"
    INVOICE_SENT = "invoice.sent"
    INVOICE_PAID = "invoice.paid"
    INVOICE_OVERDUE = "invoice.overdue"
    DRONE_FLIGHT_COMPLETED = "drone_flight.completed"
    NOTIFICATION_CREATED = "notification.created"


class WebhookCreateRequest(BaseModel):
    """Create webhook request."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., description="Webhook URL to receive events")
    events: List[WebhookEventType] = Field(..., min_items=1, description="Events to subscribe to")
    is_active: bool = Field(True, description="Whether webhook is active")
    retry_count: int = Field(3, ge=0, le=10, description="Number of retry attempts")
    retry_delay_seconds: int = Field(300, ge=60, le=3600, description="Delay between retries")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers to send with webhook")


class WebhookUpdateRequest(BaseModel):
    """Update webhook request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = None
    events: Optional[List[WebhookEventType]] = None
    is_active: Optional[bool] = None
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=60, le=3600)
    headers: Optional[Dict[str, str]] = None


class WebhookResponse(BaseModel):
    """Webhook response."""
    id: UUID
    organization_id: UUID
    name: str
    url: str
    events: List[str]
    is_active: bool
    status: str
    retry_count: int
    retry_delay_seconds: int
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery log response."""
    id: UUID
    webhook_id: UUID
    event_type: str
    status: str
    response_status: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_count: int
    next_retry_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryListResponse(BaseModel):
    """Paginated webhook delivery logs."""
    total: int
    items: List[WebhookDeliveryResponse]


class WebhookPayload(BaseModel):
    """Webhook event payload."""
    id: str
    timestamp: datetime
    event: str
    organization_id: str
    data: Dict[str, Any]


class WebhookTestRequest(BaseModel):
    """Test webhook request."""
    url: str = Field(..., description="URL to test")
    event: WebhookEventType = Field(...)
    custom_headers: Optional[Dict[str, str]] = None


class WebhookTestResponse(BaseModel):
    """Test webhook response."""
    success: bool
    status_code: Optional[int]
    response_time_ms: int
    error: Optional[str]


class WebhookEventTypeResponse(BaseModel):
    """Available webhook event type."""
    value: str
    label: str
    description: str
