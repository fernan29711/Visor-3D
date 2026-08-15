"""Notification models for alerts and activity tracking."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from app.db.database import Base


class NotificationType(str, Enum):
    """Notification type enumeration."""
    QUOTE_SENT = "quote_sent"
    QUOTE_ACCEPTED = "quote_accepted"
    QUOTE_REJECTED = "quote_rejected"
    QUOTE_EXPIRED = "quote_expired"
    INVOICE_ISSUED = "invoice_issued"
    INVOICE_PAID = "invoice_paid"
    INVOICE_OVERDUE = "invoice_overdue"
    INVOICE_PAYMENT_REMINDER = "invoice_payment_reminder"
    PROJECT_CREATED = "project_created"
    PROJECT_COMPLETED = "project_completed"
    FLIGHT_COMPLETED = "flight_completed"
    MODEL_3D_READY = "model_3d_ready"
    PAYMENT_RECEIVED = "payment_received"
    USER_INVITED = "user_invited"
    SYSTEM_ALERT = "system_alert"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    """Notification channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(Base):
    """Notification model for storing user alerts and activity."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_organization_user", "organization_id", "user_id"),
        Index("idx_user_read_status", "user_id", "is_read"),
        Index("idx_created_at", "created_at"),
    )

    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    notification_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default=NotificationPriority.MEDIUM)

    related_entity_type = Column(String(50))  # 'quote', 'invoice', 'project', 'flight', 'model_3d'
    related_entity_id = Column(String(36))

    is_read = Column(Boolean, default=False)
    channels = Column(String(200), default="in_app")  # Comma-separated: 'in_app,email,sms'

    action_url = Column(String(500))  # URL to navigate when clicked
    metadata = Column(Text)  # JSON string with additional data

    scheduled_for = Column(DateTime)  # For scheduled notifications
    sent_at = Column(DateTime)  # When actually sent
    expires_at = Column(DateTime)  # When notification expires/auto-deletes

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    read_at = Column(DateTime)

    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    organization = relationship("Organization", foreign_keys=[organization_id])


class NotificationPreference(Base):
    """User notification preferences for controlling alert delivery."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        Index("idx_org_user", "organization_id", "user_id"),
    )

    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Enable/disable by type
    quote_notifications = Column(Boolean, default=True)
    invoice_notifications = Column(Boolean, default=True)
    project_notifications = Column(Boolean, default=True)
    flight_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)

    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=False)

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # HH:MM
    quiet_hours_end = Column(String(5))    # HH:MM

    # Email settings
    email_digest = Column(Boolean, default=False)  # Daily digest vs real-time
    email_frequency = Column(String(20), default="realtime")  # realtime, daily, weekly

    # Critical alerts always enabled
    critical_alerts_always_on = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], backref="notification_preferences", uselist=False)
    organization = relationship("Organization", foreign_keys=[organization_id])


class NotificationLog(Base):
    """Activity log for tracking notification delivery and engagement."""

    __tablename__ = "notification_logs"
    __table_args__ = (
        Index("idx_notification_id", "notification_id"),
        Index("idx_user_created", "user_id", "created_at"),
    )

    id = Column(String(36), primary_key=True)
    notification_id = Column(String(36), ForeignKey("notifications.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    action = Column(String(50))  # 'sent', 'delivered', 'read', 'clicked', 'dismissed'
    channel = Column(String(20))  # 'in_app', 'email', 'sms', 'push'

    delivery_status = Column(String(50))  # 'success', 'failed', 'pending'
    delivery_error = Column(Text)  # Error message if failed

    clicked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertRule(Base):
    """Rules for triggering automatic alerts based on business conditions."""

    __tablename__ = "alert_rules"
    __table_args__ = (
        Index("idx_org_enabled", "organization_id", "is_enabled"),
    )

    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    rule_type = Column(String(50), nullable=False)  # 'invoice_overdue', 'quote_expiring', 'large_amount', 'payment_threshold'

    # Trigger conditions (JSON stored as string)
    conditions = Column(Text, nullable=False)  # {"threshold_days": 7, "amount_min": 50000}

    notification_type = Column(String(50), nullable=False)
    priority = Column(String(20), default=NotificationPriority.MEDIUM)

    is_enabled = Column(Boolean, default=True)

    # Who should be notified
    notify_roles = Column(String(200))  # 'admin,agrimensor' (comma-separated)
    notify_specific_users = Column(String(500))  # User IDs (comma-separated)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", foreign_keys=[organization_id])
