"""Tests for notification endpoints."""

import pytest
from datetime import datetime, timedelta
from app.schemas.notifications import (
    NotificationCreate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
)


def test_create_notification(admin_token, client):
    """Test creating a notification."""
    response = client.post(
        "/api/v1/notifications",
        json={
            "notification_type": "quote_sent",
            "title": "Nueva Cotización",
            "message": "Se ha enviado una nueva cotización",
            "priority": "medium",
            "related_entity_type": "quote",
            "related_entity_id": "quote-123",
            "channels": "in_app,email",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["notification_type"] == "quote_sent"
    assert data["is_read"] == False


def test_get_notifications(admin_token, client):
    """Test getting user notifications."""
    response = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_notifications_with_pagination(admin_token, client):
    """Test getting notifications with pagination."""
    response = client.get(
        "/api/v1/notifications?skip=0&limit=50",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_unread_count(admin_token, client):
    """Test getting unread notification count."""
    response = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "unread_count" in data
    assert isinstance(data["unread_count"], int)


def test_get_notification_stats(admin_token, client):
    """Test getting notification statistics."""
    response = client.get(
        "/api/v1/notifications/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unread" in data
    assert "by_priority" in data
    assert "by_type" in data


def test_get_notification_settings(admin_token, client):
    """Test getting notification center settings."""
    response = client.get(
        "/api/v1/notifications/settings",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "unread_count" in data
    assert "total_count" in data
    assert "recent_notifications" in data
    assert "has_critical" in data
    assert isinstance(data["recent_notifications"], list)


def test_mark_notification_as_read(admin_token, client):
    """Test marking a notification as read."""
    # Create a notification first
    create_response = client.post(
        "/api/v1/notifications",
        json={
            "notification_type": "quote_sent",
            "title": "Nueva Cotización",
            "message": "Se ha enviado una nueva cotización",
            "priority": "medium",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    notification_id = create_response.json()["id"]

    # Mark as read
    response = client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] == True
    assert data["read_at"] is not None


def test_mark_multiple_as_read(admin_token, client):
    """Test marking multiple notifications as read."""
    # Create notifications
    ids = []
    for i in range(3):
        create_response = client.post(
            "/api/v1/notifications",
            json={
                "notification_type": "invoice_issued",
                "title": f"Factura {i+1}",
                "message": f"Se ha emitido la factura {i+1}",
                "priority": "medium",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        ids.append(create_response.json()["id"])

    # Mark multiple as read
    response = client.patch(
        "/api/v1/notifications/read/multiple",
        json={"notification_ids": ids},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["marked_as_read"] == 3


def test_delete_notification(admin_token, client):
    """Test deleting a notification."""
    # Create a notification
    create_response = client.post(
        "/api/v1/notifications",
        json={
            "notification_type": "quote_sent",
            "title": "Nueva Cotización",
            "message": "Se ha enviado una nueva cotización",
            "priority": "medium",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    notification_id = create_response.json()["id"]

    # Delete it
    response = client.delete(
        f"/api/v1/notifications/{notification_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


def test_get_notification_preferences(admin_token, client):
    """Test getting notification preferences."""
    response = client.get(
        "/api/v1/notifications/preferences/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "quote_notifications" in data
    assert "invoice_notifications" in data
    assert "email_enabled" in data
    assert "quiet_hours_enabled" in data


def test_update_notification_preferences(admin_token, client):
    """Test updating notification preferences."""
    response = client.put(
        "/api/v1/notifications/preferences/me",
        json={
            "quote_notifications": False,
            "invoice_notifications": True,
            "email_enabled": False,
            "quiet_hours_enabled": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "email_frequency": "daily",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quote_notifications"] == False
    assert data["invoice_notifications"] == True
    assert data["email_enabled"] == False
    assert data["quiet_hours_enabled"] == True
    assert data["quiet_hours_start"] == "22:00"
    assert data["quiet_hours_end"] == "08:00"
    assert data["email_frequency"] == "daily"


def test_notification_requires_authentication(client):
    """Test that notification endpoints require authentication."""
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401

    response = client.patch("/api/v1/notifications/some-id/read")
    assert response.status_code == 401

    response = client.delete("/api/v1/notifications/some-id")
    assert response.status_code == 401


def test_get_nonexistent_notification(admin_token, client):
    """Test getting a non-existent notification."""
    response = client.get(
        "/api/v1/notifications/nonexistent-id",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_notification_type_values(admin_token, client):
    """Test creating notifications with different types."""
    types = [
        "quote_sent",
        "quote_accepted",
        "invoice_issued",
        "invoice_paid",
        "project_created",
        "flight_completed",
        "model_3d_ready",
    ]

    for notif_type in types:
        response = client.post(
            "/api/v1/notifications",
            json={
                "notification_type": notif_type,
                "title": f"{notif_type} Notification",
                "message": f"This is a {notif_type} notification",
                "priority": "medium",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        assert response.json()["notification_type"] == notif_type


def test_notification_priority_levels(admin_token, client):
    """Test creating notifications with different priorities."""
    priorities = ["low", "medium", "high", "critical"]

    for priority in priorities:
        response = client.post(
            "/api/v1/notifications",
            json={
                "notification_type": "system_alert",
                "title": f"Priority {priority}",
                "message": f"Test notification with {priority} priority",
                "priority": priority,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        assert response.json()["priority"] == priority


def test_notification_with_expiration(admin_token, client):
    """Test creating a notification with expiration."""
    expiration = datetime.utcnow() + timedelta(days=7)

    response = client.post(
        "/api/v1/notifications",
        json={
            "notification_type": "system_alert",
            "title": "Temporary Alert",
            "message": "This notification will expire in 7 days",
            "priority": "low",
            "expires_at": expiration.isoformat(),
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] is not None


def test_partial_preference_update(admin_token, client):
    """Test updating only specific preference fields."""
    # Update only email_enabled
    response = client.put(
        "/api/v1/notifications/preferences/me",
        json={"email_enabled": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email_enabled"] == False

    # Other fields should remain at defaults
    assert "id" in data
    assert isinstance(data["quote_notifications"], bool)


def test_notification_channels(admin_token, client):
    """Test creating notifications with different channels."""
    response = client.post(
        "/api/v1/notifications",
        json={
            "notification_type": "invoice_issued",
            "title": "Multi-channel Notification",
            "message": "Sent via multiple channels",
            "priority": "high",
            "channels": "in_app,email,sms",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "in_app" in data["channels"]
    assert "email" in data["channels"]
    assert "sms" in data["channels"]
