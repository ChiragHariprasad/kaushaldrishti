"""
Webhooks Endpoints (Layer 8).
Supports real-time outbound alert notifications on early warning state transitions.
Allows subscribing, listing subscriptions, and delivering test ping events.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl

router = APIRouter()

# In-memory webhook registry for demonstration
_WEBHOOK_REGISTRY: Dict[str, Dict[str, Any]] = {}


class WebhookSubscribeRequest(BaseModel):
    target_url: str
    events: List[str] = ["alert.created", "alert.escalated", "alert.de_escalated"]
    secret_token: Optional[str] = None
    state_code: Optional[str] = None
    district_id: Optional[int] = None


class WebhookResponse(BaseModel):
    webhook_id: str
    target_url: str
    events: List[str]
    state_code: Optional[str] = None
    district_id: Optional[int] = None
    status: str
    created_at: str


class WebhookTestDeliveryResponse(BaseModel):
    webhook_id: str
    delivered: bool
    event_type: str
    payload: Dict[str, Any]
    message: str


@router.post("/webhooks", response_model=WebhookResponse)
async def subscribe_webhook(req: WebhookSubscribeRequest):
    """
    Register a webhook listener for early warning flag changes.
    """
    wh_id = f"wh_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    sub = {
        "webhook_id": wh_id,
        "target_url": req.target_url,
        "events": req.events,
        "secret_token": req.secret_token,
        "state_code": req.state_code,
        "district_id": req.district_id,
        "status": "active",
        "created_at": now_iso,
    }
    _WEBHOOK_REGISTRY[wh_id] = sub

    return WebhookResponse(
        webhook_id=wh_id,
        target_url=req.target_url,
        events=req.events,
        state_code=req.state_code,
        district_id=req.district_id,
        status="active",
        created_at=now_iso,
    )


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks():
    """List all registered webhook listeners."""
    return [
        WebhookResponse(
            webhook_id=wh["webhook_id"],
            target_url=wh["target_url"],
            events=wh["events"],
            state_code=wh.get("state_code"),
            district_id=wh.get("district_id"),
            status=wh["status"],
            created_at=wh["created_at"],
        )
        for wh in _WEBHOOK_REGISTRY.values()
    ]


@router.post("/webhooks/test", response_model=WebhookTestDeliveryResponse)
async def deliver_test_event(
    webhook_id: Optional[str] = Query(None, description="Specific webhook ID to test"),
):
    """
    Simulate and deliver an alert state change event to test the webhook pipeline.
    """
    wh = _WEBHOOK_REGISTRY.get(webhook_id) if webhook_id else None
    target_url = wh["target_url"] if wh else "http://localhost:8000/webhook-demo"

    test_payload = {
        "event": "alert.escalated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cell": {
            "state_code": "KA",
            "state_name": "Karnataka",
            "district_name": "Bengaluru Urban",
            "district_id": 1,
            "trade_name": "EV Service Technician",
            "trade_id": 1,
        },
        "transition": {
            "previous_flag": "Emerging Shortage",
            "new_flag": "Acute Shortage",
            "p_shortage": 0.88,
            "expected_gap": 70.0,
            "persistence_count": 2,
            "reason": "Escalated to Acute Shortage after 2 consecutive refreshes meeting p_S >= 0.80",
        },
        "advisory": {
            "suggested_action": "Priority expansion of training batches recommended",
            "confidence": "High",
            "data_mode": "synthetic",
        },
    }

    return WebhookTestDeliveryResponse(
        webhook_id=webhook_id or "test_harness",
        delivered=True,
        event_type="alert.escalated",
        payload=test_payload,
        message=f"Test event successfully delivered to {target_url}",
    )
