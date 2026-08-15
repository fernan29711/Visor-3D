"""Webhook API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.db.models import User
from app.db.models_webhooks import WebhookEvent
from app.services.webhook_service import WebhookService
from app.schemas.webhooks import (
    WebhookCreateRequest, WebhookUpdateRequest, WebhookResponse,
    WebhookDeliveryResponse, WebhookDeliveryListResponse,
    WebhookTestRequest, WebhookTestResponse, WebhookEventTypeResponse
)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.get("/events", response_model=list[WebhookEventTypeResponse])
async def get_available_events():
    """Get list of available webhook events."""
    events = [
        {"value": "project.created", "label": "Project Created", "description": "When a new project is created"},
        {"value": "project.updated", "label": "Project Updated", "description": "When a project is updated"},
        {"value": "project.completed", "label": "Project Completed", "description": "When a project is completed"},
        {"value": "quote.created", "label": "Quote Created", "description": "When a new quote is created"},
        {"value": "quote.sent", "label": "Quote Sent", "description": "When a quote is sent to client"},
        {"value": "quote.accepted", "label": "Quote Accepted", "description": "When a quote is accepted"},
        {"value": "quote.rejected", "label": "Quote Rejected", "description": "When a quote is rejected"},
        {"value": "invoice.created", "label": "Invoice Created", "description": "When a new invoice is created"},
        {"value": "invoice.sent", "label": "Invoice Sent", "description": "When an invoice is sent"},
        {"value": "invoice.paid", "label": "Invoice Paid", "description": "When an invoice is paid"},
        {"value": "invoice.overdue", "label": "Invoice Overdue", "description": "When an invoice becomes overdue"},
        {"value": "drone_flight.completed", "label": "Drone Flight Completed", "description": "When a drone flight completes"},
        {"value": "notification.created", "label": "Notification Created", "description": "When a notification is created"},
    ]
    return events


@router.post("", response_model=WebhookResponse)
def create_webhook(
    request: WebhookCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new webhook."""
    webhook = WebhookService.create_webhook(
        db, current_user.organization_id, current_user.id, request
    )
    return webhook


@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List webhooks for organization."""
    webhooks = WebhookService.get_organization_webhooks(db, current_user.organization_id, skip, limit)
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get webhook by ID."""
    webhook = WebhookService.get_webhook(db, webhook_id)
    if not webhook or webhook.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.patch("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: UUID,
    request: WebhookUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update webhook."""
    webhook = WebhookService.get_webhook(db, webhook_id)
    if not webhook or webhook.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")

    updated_webhook = WebhookService.update_webhook(db, webhook_id, request)
    return updated_webhook


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete webhook."""
    webhook = WebhookService.get_webhook(db, webhook_id)
    if not webhook or webhook.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")

    WebhookService.delete_webhook(db, webhook_id)
    return {"message": "Webhook deleted"}


@router.get("/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
def get_webhook_deliveries(
    webhook_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get delivery logs for webhook."""
    webhook = WebhookService.get_webhook(db, webhook_id)
    if not webhook or webhook.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")

    total, deliveries = WebhookService.get_webhook_deliveries(db, webhook_id, skip, limit)
    return {
        "total": total,
        "items": deliveries
    }


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test webhook delivery."""
    webhook = WebhookService.get_webhook(db, webhook_id)
    if not webhook or webhook.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")

    result = await WebhookService.test_webhook(webhook.url, "test.event", webhook.headers)
    return result


@router.post("/test", response_model=WebhookTestResponse)
async def test_webhook_url(
    request: WebhookTestRequest,
    current_user: User = Depends(get_current_user),
):
    """Test webhook URL before saving."""
    result = await WebhookService.test_webhook(request.url, request.event.value, request.custom_headers)
    return result
