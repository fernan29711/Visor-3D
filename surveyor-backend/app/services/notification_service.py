"""Service for managing notifications and alerts."""

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.db.models_notifications import (
    Notification, NotificationPreference, NotificationLog, AlertRule,
    NotificationType, NotificationPriority, NotificationChannel
)
from app.db.models import User
from app.schemas.notifications import (
    NotificationCreate, NotificationPreferenceCreate, NotificationPreferenceUpdate
)
from app.core.exceptions import NotFoundError, ValidationError


class NotificationService:
    """Service for managing notifications, preferences, and alert rules."""

    def __init__(self, db: Session):
        self.db = db

    # Notification Management

    def create_notification(self, org_id: str, user_id: str, request: NotificationCreate) -> dict:
        """Create a new notification for a user."""
        notification = Notification(
            id=str(uuid4()),
            organization_id=org_id,
            user_id=user_id,
            notification_type=request.notification_type,
            title=request.title,
            message=request.message,
            priority=request.priority,
            related_entity_type=request.related_entity_type,
            related_entity_id=request.related_entity_id,
            channels=request.channels,
            action_url=request.action_url,
            metadata=request.metadata,
            scheduled_for=request.scheduled_for,
            expires_at=request.expires_at,
            sent_at=datetime.utcnow() if not request.scheduled_for else None,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return self._notification_to_dict(notification)

    def get_user_notifications(self, org_id: str, user_id: str, limit: int = 50, skip: int = 0) -> list[dict]:
        """Get notifications for a specific user."""
        notifications = self.db.query(Notification).filter(
            Notification.organization_id == org_id,
            Notification.user_id == user_id,
            Notification.expires_at > datetime.utcnow() or Notification.expires_at.is_(None)
        ).order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

        return [self._notification_to_dict(n) for n in notifications]

    def get_user_unread_count(self, org_id: str, user_id: str) -> int:
        """Get count of unread notifications for a user."""
        return self.db.query(Notification).filter(
            Notification.organization_id == org_id,
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.expires_at > datetime.utcnow() or Notification.expires_at.is_(None)
        ).count()

    def get_notification(self, notification_id: str, org_id: str) -> dict:
        """Get a specific notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.organization_id == org_id
        ).first()

        if not notification:
            raise NotFoundError("Notification not found")

        return self._notification_to_dict(notification)

    def mark_as_read(self, notification_id: str, org_id: str, user_id: str) -> dict:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.organization_id == org_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise NotFoundError("Notification not found")

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(notification)
        return self._notification_to_dict(notification)

    def mark_multiple_as_read(self, notification_ids: list[str], org_id: str, user_id: str) -> dict:
        """Mark multiple notifications as read."""
        count = self.db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.organization_id == org_id,
            Notification.user_id == user_id
        ).update(
            {
                Notification.is_read: True,
                Notification.read_at: datetime.utcnow()
            },
            synchronize_session=False
        )
        self.db.commit()
        return {"marked_as_read": count}

    def delete_notification(self, notification_id: str, org_id: str, user_id: str) -> None:
        """Delete a notification."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.organization_id == org_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise NotFoundError("Notification not found")

        self.db.delete(notification)
        self.db.commit()

    def get_notification_stats(self, org_id: str, user_id: str) -> dict:
        """Get notification statistics for a user."""
        notifications = self.db.query(Notification).filter(
            Notification.organization_id == org_id,
            Notification.user_id == user_id,
            Notification.expires_at > datetime.utcnow() or Notification.expires_at.is_(None)
        ).all()

        total = len(notifications)
        unread = sum(1 for n in notifications if not n.is_read)

        by_priority = {}
        by_type = {}
        for n in notifications:
            by_priority[n.priority] = by_priority.get(n.priority, 0) + 1
            by_type[n.notification_type] = by_type.get(n.notification_type, 0) + 1

        return {
            "total": total,
            "unread": unread,
            "by_priority": by_priority,
            "by_type": by_type,
        }

    # Notification Preferences

    def get_or_create_preferences(self, org_id: str, user_id: str) -> dict:
        """Get or create notification preferences for a user."""
        prefs = self.db.query(NotificationPreference).filter(
            NotificationPreference.organization_id == org_id,
            NotificationPreference.user_id == user_id
        ).first()

        if not prefs:
            prefs = NotificationPreference(
                id=str(uuid4()),
                organization_id=org_id,
                user_id=user_id,
            )
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)

        return self._preferences_to_dict(prefs)

    def update_preferences(self, org_id: str, user_id: str, request: NotificationPreferenceUpdate) -> dict:
        """Update notification preferences for a user."""
        prefs = self.db.query(NotificationPreference).filter(
            NotificationPreference.organization_id == org_id,
            NotificationPreference.user_id == user_id
        ).first()

        if not prefs:
            prefs = NotificationPreference(
                id=str(uuid4()),
                organization_id=org_id,
                user_id=user_id,
            )
            self.db.add(prefs)

        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(prefs, field, value)

        prefs.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(prefs)
        return self._preferences_to_dict(prefs)

    # Bulk Notification Dispatch

    def notify_users(self, org_id: str, user_ids: list[str], notification_data: NotificationCreate) -> dict:
        """Send notification to multiple users."""
        created_count = 0
        for user_id in user_ids:
            try:
                self.create_notification(org_id, user_id, notification_data)
                created_count += 1
            except Exception:
                pass

        return {"created": created_count, "total_users": len(user_ids)}

    def notify_by_role(self, org_id: str, roles: list[str], notification_data: NotificationCreate) -> dict:
        """Send notification to all users with specific roles."""
        users = self.db.query(User).filter(
            User.organization_id == org_id,
            User.role.in_(roles)
        ).all()

        user_ids = [u.id for u in users]
        return self.notify_users(org_id, user_ids, notification_data)

    # Helper Methods

    def _notification_to_dict(self, notification: Notification) -> dict:
        """Convert notification to dictionary."""
        return {
            "id": notification.id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "related_entity_type": notification.related_entity_type,
            "related_entity_id": notification.related_entity_id,
            "is_read": notification.is_read,
            "channels": notification.channels,
            "action_url": notification.action_url,
            "metadata": notification.metadata,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
            "expires_at": notification.expires_at,
        }

    def _preferences_to_dict(self, prefs: NotificationPreference) -> dict:
        """Convert preferences to dictionary."""
        return {
            "id": prefs.id,
            "quote_notifications": prefs.quote_notifications,
            "invoice_notifications": prefs.invoice_notifications,
            "project_notifications": prefs.project_notifications,
            "flight_notifications": prefs.flight_notifications,
            "system_notifications": prefs.system_notifications,
            "email_enabled": prefs.email_enabled,
            "sms_enabled": prefs.sms_enabled,
            "push_enabled": prefs.push_enabled,
            "quiet_hours_enabled": prefs.quiet_hours_enabled,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "email_digest": prefs.email_digest,
            "email_frequency": prefs.email_frequency,
            "critical_alerts_always_on": prefs.critical_alerts_always_on,
            "created_at": prefs.created_at,
            "updated_at": prefs.updated_at,
        }
