"""Notification endpoints for alerts and user preferences."""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationStatsResponse,
    MarkAsReadRequest,
    NotificationSettingsResponse,
)
from app.services.notification_service import NotificationService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationListResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's notifications."""
    try:
        service = NotificationService(db)
        notifications = service.get_user_notifications(
            str(current_user.organization_id),
            str(current_user.id),
            limit=limit,
            skip=skip,
        )
        return notifications
    except AppException as e:
        raise http_exception(e)


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification statistics."""
    try:
        service = NotificationService(db)
        stats = service.get_notification_stats(
            str(current_user.organization_id),
            str(current_user.id),
        )
        return stats
    except AppException as e:
        raise http_exception(e)


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get unread notification count."""
    try:
        service = NotificationService(db)
        count = service.get_user_unread_count(
            str(current_user.organization_id),
            str(current_user.id),
        )
        return {"unread_count": count}
    except AppException as e:
        raise http_exception(e)


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification center summary (unread count + recent notifications)."""
    try:
        service = NotificationService(db)
        unread_count = service.get_user_unread_count(
            str(current_user.organization_id),
            str(current_user.id),
        )
        total_count = len(service.get_user_notifications(
            str(current_user.organization_id),
            str(current_user.id),
            limit=1000,
        ))
        recent = service.get_user_notifications(
            str(current_user.organization_id),
            str(current_user.id),
            limit=10,
        )
        has_critical = any(n["priority"] == "critical" and not n["is_read"] for n in recent)

        return {
            "unread_count": unread_count,
            "total_count": total_count,
            "recent_notifications": recent,
            "has_critical": has_critical,
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific notification."""
    try:
        service = NotificationService(db)
        notification = service.get_notification(
            notification_id,
            str(current_user.organization_id),
        )
        return notification
    except AppException as e:
        raise http_exception(e)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    try:
        service = NotificationService(db)
        notification = service.mark_as_read(
            notification_id,
            str(current_user.organization_id),
            str(current_user.id),
        )
        return notification
    except AppException as e:
        raise http_exception(e)


@router.patch("/read/multiple")
async def mark_multiple_as_read(
    request: MarkAsReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark multiple notifications as read."""
    try:
        service = NotificationService(db)
        result = service.mark_multiple_as_read(
            request.notification_ids,
            str(current_user.organization_id),
            str(current_user.id),
        )
        return result
    except AppException as e:
        raise http_exception(e)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a notification."""
    try:
        service = NotificationService(db)
        service.delete_notification(
            notification_id,
            str(current_user.organization_id),
            str(current_user.id),
        )
        return None
    except AppException as e:
        raise http_exception(e)


@router.get("/preferences/me", response_model=NotificationPreferenceResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's notification preferences."""
    try:
        service = NotificationService(db)
        prefs = service.get_or_create_preferences(
            str(current_user.organization_id),
            str(current_user.id),
        )
        return prefs
    except AppException as e:
        raise http_exception(e)


@router.put("/preferences/me", response_model=NotificationPreferenceResponse)
async def update_my_preferences(
    request: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's notification preferences."""
    try:
        service = NotificationService(db)
        prefs = service.update_preferences(
            str(current_user.organization_id),
            str(current_user.id),
            request,
        )
        return prefs
    except AppException as e:
        raise http_exception(e)
