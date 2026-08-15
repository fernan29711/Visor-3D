"""Tests for webhook endpoints."""

import pytest
from app.db.models_webhooks import Webhook
from app.schemas.webhooks import WebhookEventType


def test_get_available_events(client):
    """Test getting list of available webhook events."""
    response = client.get("/api/v1/webhooks/events")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(e["value"] == "project.created" for e in data)
    assert any(e["value"] == "invoice.paid" for e in data)
    for event in data:
        assert "value" in event
        assert "label" in event
        assert "description" in event


def test_create_webhook(admin_token, client):
    """Test creating a webhook."""
    payload = {
        "name": "Test Webhook",
        "url": "https://example.com/webhook",
        "events": ["project.created", "invoice.paid"],
        "is_active": True,
        "retry_count": 3,
        "retry_delay_seconds": 300
    }

    response = client.post(
        "/api/v1/webhooks",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Webhook"
    assert data["url"] == "https://example.com/webhook"
    assert "project.created" in data["events"]
    assert "invoice.paid" in data["events"]
    assert data["is_active"] is True
    assert "id" in data


def test_list_webhooks(admin_token, client):
    """Test listing webhooks."""
    response = client.get(
        "/api/v1/webhooks",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_webhook_requires_auth(client):
    """Test webhook creation requires authentication."""
    payload = {
        "name": "Test Webhook",
        "url": "https://example.com/webhook",
        "events": ["project.created"],
    }

    response = client.post("/api/v1/webhooks", json=payload)
    assert response.status_code == 401


def test_get_webhook(admin_token, client, db, test_organization_id, test_user_id):
    """Test getting a specific webhook."""
    webhook = Webhook(
        organization_id=test_organization_id,
        name="Test Webhook",
        url="https://example.com/webhook",
        events=["project.created"],
        secret="test-secret",
        created_by_user_id=test_user_id
    )
    db.add(webhook)
    db.commit()

    response = client.get(
        f"/api/v1/webhooks/{webhook.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(webhook.id)
    assert data["name"] == "Test Webhook"


def test_get_nonexistent_webhook(admin_token, client):
    """Test getting non-existent webhook."""
    import uuid
    fake_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/webhooks/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


def test_update_webhook(admin_token, client, db, test_organization_id, test_user_id):
    """Test updating a webhook."""
    webhook = Webhook(
        organization_id=test_organization_id,
        name="Original Name",
        url="https://example.com/webhook",
        events=["project.created"],
        secret="test-secret",
        created_by_user_id=test_user_id
    )
    db.add(webhook)
    db.commit()

    update_payload = {
        "name": "Updated Name",
        "events": ["invoice.paid", "quote.accepted"]
    }

    response = client.patch(
        f"/api/v1/webhooks/{webhook.id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert "invoice.paid" in data["events"]


def test_delete_webhook(admin_token, client, db, test_organization_id, test_user_id):
    """Test deleting a webhook."""
    webhook = Webhook(
        organization_id=test_organization_id,
        name="Test Webhook",
        url="https://example.com/webhook",
        events=["project.created"],
        secret="test-secret",
        created_by_user_id=test_user_id
    )
    db.add(webhook)
    db.commit()
    webhook_id = webhook.id

    response = client.delete(
        f"/api/v1/webhooks/{webhook_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    check_response = client.get(
        f"/api/v1/webhooks/{webhook_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert check_response.status_code == 404


def test_get_webhook_deliveries(admin_token, client, db, test_organization_id, test_user_id):
    """Test getting webhook delivery logs."""
    webhook = Webhook(
        organization_id=test_organization_id,
        name="Test Webhook",
        url="https://example.com/webhook",
        events=["project.created"],
        secret="test-secret",
        created_by_user_id=test_user_id
    )
    db.add(webhook)
    db.commit()

    response = client.get(
        f"/api/v1/webhooks/{webhook.id}/deliveries",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_webhook_validation(admin_token, client):
    """Test webhook payload validation."""
    invalid_payloads = [
        {
            "name": "",
            "url": "https://example.com/webhook",
            "events": ["project.created"]
        },
        {
            "name": "Test",
            "url": "invalid-url",
            "events": ["project.created"]
        },
        {
            "name": "Test",
            "url": "https://example.com/webhook",
            "events": []
        },
        {
            "name": "Test",
            "url": "https://example.com/webhook",
            "events": ["project.created"],
            "retry_count": 20
        }
    ]

    for payload in invalid_payloads:
        response = client.post(
            "/api/v1/webhooks",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code in [400, 422]


def test_webhook_isolation(admin_token, client, technician_token, db, test_organization_id, test_user_id):
    """Test webhook data isolation between organizations."""
    webhook = Webhook(
        organization_id=test_organization_id,
        name="Test Webhook",
        url="https://example.com/webhook",
        events=["project.created"],
        secret="test-secret",
        created_by_user_id=test_user_id
    )
    db.add(webhook)
    db.commit()

    response = client.get(
        f"/api/v1/webhooks/{webhook.id}",
        headers={"Authorization": f"Bearer {technician_token}"},
    )

    assert response.status_code == 404
