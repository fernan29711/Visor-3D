"""Pydantic schemas for notifications."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    notification_type: str
    title: str
    message: str
    priority: str = "medium"
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    channels: str = "in_app"
    action_url: Optional[str] = None
    metadata: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Response schema for a notification."""
    id: str
    notification_type: str
    title: str
    message: str
    priority: str
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    is_read: bool
    channels: str
    action_url: Optional[str]
    metadata: Optional[str]
    created_at: datetime
    read_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response schema for notification list."""
    id: str
    notification_type: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    action_url: Optional[str]

    class Config:
        from_attributes = True


class NotificationPreferenceCreate(BaseModel):
    """Schema for creating notification preferences."""
    quote_notifications: bool = True
    invoice_notifications: bool = True
    project_notifications: bool = True
    flight_notifications: bool = True
    system_notifications: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = False
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    email_digest: bool = False
    email_frequency: str = "realtime"
    critical_alerts_always_on: bool = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    quote_notifications: Optional[bool] = None
    invoice_notifications: Optional[bool] = None
    project_notifications: Optional[bool] = None
    flight_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    email_digest: Optional[bool] = None
    email_frequency: Optional[str] = None
    critical_alerts_always_on: Optional[bool] = None


class NotificationPreferenceResponse(BaseModel):
    """Response schema for notification preferences."""
    id: str
    quote_notifications: bool
    invoice_notifications: bool
    project_notifications: bool
    flight_notifications: bool
    system_notifications: bool
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    email_digest: bool
    email_frequency: str
    critical_alerts_always_on: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    """Response schema for notification statistics."""
    total: int
    unread: int
    by_priority: dict
    by_type: dict


class MarkAsReadRequest(BaseModel):
    """Request to mark notifications as read."""
    notification_ids: List[str]


class NotificationSettingsResponse(BaseModel):
    """Response with notification center summary."""
    unread_count: int
    total_count: int
    recent_notifications: List[NotificationListResponse]
    has_critical: bool
