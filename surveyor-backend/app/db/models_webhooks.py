"""Webhook database models."""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Integer, Text, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum as PyEnum
from datetime import datetime
from app.db.database import Base


class WebhookEvent(str, PyEnum):
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


class WebhookStatus(str, PyEnum):
    """Webhook status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class WebhookDeliveryStatus(str, PyEnum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base):
    """Webhook configuration model."""
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(JSONB, nullable=False, default=list)
    secret = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    status = Column(SQLEnum(WebhookStatus), default=WebhookStatus.ACTIVE)
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)
    headers = Column(JSONB, nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_triggered_at = Column(DateTime, nullable=True)

    organization = relationship("Organization")
    created_by = relationship("User")
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Webhook {self.name}>"


class WebhookDelivery(Base):
    """Webhook delivery attempt log."""
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False, index=True)
    event_type = Column(Enum(WebhookEvent), nullable=False)
    status = Column(SQLEnum(WebhookDeliveryStatus), default=WebhookDeliveryStatus.PENDING, index=True)
    payload = Column(JSONB, nullable=False)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=1)
    next_retry_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    webhook = relationship("Webhook", back_populates="deliveries")

    def __repr__(self):
        return f"<WebhookDelivery {self.event_type} ({self.status})>"


# Add relationship to Organization model
from app.db.models import Organization
Organization.webhooks = relationship("Webhook", back_populates="organization", cascade="all, delete-orphan")
