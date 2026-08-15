"""Webhook service for managing and delivering webhooks."""

import httpx
import asyncio
import hmac
import hashlib
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.db.models_webhooks import Webhook, WebhookDelivery, WebhookEvent, WebhookStatus, WebhookDeliveryStatus
from app.schemas.webhooks import WebhookCreateRequest, WebhookUpdateRequest, WebhookResponse


class WebhookService:
    """Service for webhook management and delivery."""

    WEBHOOK_TIMEOUT = 10.0

    @staticmethod
    def create_webhook(
        db: Session,
        organization_id: UUID,
        user_id: UUID,
        request: WebhookCreateRequest
    ) -> Webhook:
        """Create a new webhook."""
        secret = WebhookService.generate_secret()

        webhook = Webhook(
            organization_id=organization_id,
            name=request.name,
            url=request.url,
            events=[event.value for event in request.events],
            secret=secret,
            is_active=request.is_active,
            retry_count=request.retry_count,
            retry_delay_seconds=request.retry_delay_seconds,
            headers=request.headers or {},
            created_by_user_id=user_id
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def update_webhook(
        db: Session,
        webhook_id: UUID,
        request: WebhookUpdateRequest
    ) -> Webhook:
        """Update webhook configuration."""
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook:
            return None

        if request.name is not None:
            webhook.name = request.name
        if request.url is not None:
            webhook.url = request.url
        if request.events is not None:
            webhook.events = [event.value for event in request.events]
        if request.is_active is not None:
            webhook.is_active = request.is_active
        if request.retry_count is not None:
            webhook.retry_count = request.retry_count
        if request.retry_delay_seconds is not None:
            webhook.retry_delay_seconds = request.retry_delay_seconds
        if request.headers is not None:
            webhook.headers = request.headers

        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def get_webhook(db: Session, webhook_id: UUID) -> Optional[Webhook]:
        """Get webhook by ID."""
        return db.query(Webhook).filter(Webhook.id == webhook_id).first()

    @staticmethod
    def get_organization_webhooks(
        db: Session,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Webhook]:
        """Get all webhooks for organization."""
        return db.query(Webhook).filter(
            Webhook.organization_id == organization_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def delete_webhook(db: Session, webhook_id: UUID) -> bool:
        """Delete webhook."""
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if webhook:
            db.delete(webhook)
            db.commit()
            return True
        return False

    @staticmethod
    def get_webhook_deliveries(
        db: Session,
        webhook_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[int, List[WebhookDelivery]]:
        """Get delivery logs for webhook."""
        total = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).count()

        deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(desc(WebhookDelivery.created_at)).offset(skip).limit(limit).all()

        return total, deliveries

    @staticmethod
    async def trigger_webhook(
        db: Session,
        organization_id: UUID,
        event_type: WebhookEvent,
        payload: Dict[str, Any]
    ):
        """Trigger webhooks for an organization and event type."""
        webhooks = db.query(Webhook).filter(
            and_(
                Webhook.organization_id == organization_id,
                Webhook.is_active == True
            )
        ).all()

        for webhook in webhooks:
            if event_type.value in webhook.events:
                await WebhookService.queue_delivery(db, webhook, event_type, payload)

    @staticmethod
    async def queue_delivery(
        db: Session,
        webhook: Webhook,
        event_type: WebhookEvent,
        payload: Dict[str, Any]
    ):
        """Queue webhook delivery."""
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event_type=event_type,
            payload=payload,
            status=WebhookDeliveryStatus.PENDING
        )
        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        webhook.last_triggered_at = datetime.utcnow()
        db.commit()

        await WebhookService.send_webhook(db, delivery)

    @staticmethod
    async def send_webhook(db: Session, delivery: WebhookDelivery):
        """Send webhook delivery."""
        webhook = delivery.webhook
        payload = {
            "id": str(delivery.id),
            "timestamp": datetime.utcnow().isoformat(),
            "event": delivery.event_type.value,
            "organization_id": str(webhook.organization_id),
            "data": delivery.payload
        }

        headers = dict(webhook.headers or {})
        headers["X-Webhook-Event"] = delivery.event_type.value
        headers["X-Webhook-Signature"] = WebhookService.generate_signature(payload, webhook.secret)
        headers["Content-Type"] = "application/json"

        try:
            async with httpx.AsyncClient(timeout=WebhookService.WEBHOOK_TIMEOUT) as client:
                response = await client.post(webhook.url, json=payload, headers=headers)

                delivery.response_status = response.status_code
                delivery.response_body = response.text[:1000]

                if 200 <= response.status_code < 300:
                    delivery.status = WebhookDeliveryStatus.DELIVERED
                    delivery.delivered_at = datetime.utcnow()
                else:
                    raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            delivery.error_message = str(e)
            delivery.attempt_count += 1

            if delivery.attempt_count <= webhook.retry_count:
                delivery.status = WebhookDeliveryStatus.RETRYING
                delivery.next_retry_at = datetime.utcnow() + timedelta(
                    seconds=webhook.retry_delay_seconds
                )
            else:
                delivery.status = WebhookDeliveryStatus.FAILED
                webhook.status = WebhookStatus.FAILED

        db.commit()

    @staticmethod
    async def retry_failed_deliveries(db: Session):
        """Retry failed webhook deliveries."""
        now = datetime.utcnow()
        failed_deliveries = db.query(WebhookDelivery).filter(
            and_(
                WebhookDelivery.status == WebhookDeliveryStatus.RETRYING,
                WebhookDelivery.next_retry_at <= now
            )
        ).all()

        for delivery in failed_deliveries:
            await WebhookService.send_webhook(db, delivery)

    @staticmethod
    def generate_secret() -> str:
        """Generate webhook secret."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_signature(payload: Dict[str, Any], secret: str) -> str:
        """Generate HMAC signature for payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        expected_signature = WebhookService.generate_signature(json.loads(payload), secret)
        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    async def test_webhook(url: str, event_type: str, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Test webhook URL."""
        payload = {
            "id": "test-webhook",
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_type,
            "organization_id": "test-org",
            "data": {"test": True}
        }

        headers = custom_headers or {}
        headers["X-Webhook-Event"] = event_type
        headers["Content-Type"] = "application/json"

        start_time = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=WebhookService.WEBHOOK_TIMEOUT) as client:
                response = await client.post(url, json=payload, headers=headers)
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                return {
                    "success": 200 <= response.status_code < 300,
                    "status_code": response.status_code,
                    "response_time_ms": int(response_time),
                    "error": None
                }
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": int(response_time),
                "error": str(e)
            }
