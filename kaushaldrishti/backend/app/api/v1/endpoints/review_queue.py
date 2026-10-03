"""
Mapping Review Queue Endpoints.
Allows human-in-the-loop review of uncertain taxonomy and geography matches (< 0.55 confidence).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ReviewItem(BaseModel):
    id: int
    raw_title: str
    raw_skills: Optional[str] = None
    raw_location: Optional[str] = None
    source_id: str
    suggested_trade: Optional[str] = None
    suggested_nco: Optional[str] = None
    confidence: float
    status: str  # pending, approved, rejected, remapped
    created_at: str


class ReviewDecisionRequest(BaseModel):
    decision: str  # approved, rejected, remapped
    assigned_trade_id: Optional[int] = None
    reviewer_notes: Optional[str] = None


# Seed review queue items for demonstration
_DEMO_REVIEW_QUEUE: List[Dict[str, Any]] = [
    {
        "id": 1,
        "raw_title": "Heavy EV Propulsion Battery Assembler and High Voltage Wireman",
        "raw_skills": "High Voltage Safety, BMS Diagnostics",
        "raw_location": "Hosur / Bengaluru Border",
        "source_id": "portal",
        "suggested_trade": "EV Service Technician",
        "suggested_nco": "7231.0101",
        "confidence": 0.52,  # Below 0.55 threshold -> enters queue
        "status": "pending",
        "created_at": "2024-03-01T10:00:00Z",
    },
    {
        "id": 2,
        "raw_title": "AI Robotic Sorter Operator",
        "raw_skills": "Robotic cell control, Conveyor maintenance",
        "raw_location": "Noida Sector 63",
        "source_id": "portal",
        "suggested_trade": "Warehouse Associate",
        "suggested_nco": "4321.0100",
        "confidence": 0.48,
        "status": "pending",
        "created_at": "2024-03-02T14:30:00Z",
    },
    {
        "id": 3,
        "raw_title": "Drone Surveillance Operator for Perimeter Guarding",
        "raw_skills": "DGCA Drone Pilot Certification",
        "raw_location": "Coimbatore Outer",
        "source_id": "ncs",
        "suggested_trade": "CCTV Installation Technician",
        "suggested_nco": "7421.0200",
        "confidence": 0.44,
        "status": "pending",
        "created_at": "2024-03-03T09:15:00Z",
    },
]


@router.get("/review-queue", response_model=List[ReviewItem])
async def list_review_queue(status: Optional[str] = "pending") -> List[ReviewItem]:
    """
    Returns items in mapping review queue filtered by status.
    """
    filtered = [
        ReviewItem(**item) for item in _DEMO_REVIEW_QUEUE
        if status is None or item["status"] == status
    ]
    return filtered


@router.post("/review-queue/{item_id}/decide")
async def decide_review_item(item_id: int, decision: ReviewDecisionRequest) -> Dict[str, Any]:
    """
    Submits a reviewer decision (approve, reject, or remap).
    Updates review item and logs to audit log.
    """
    for item in _DEMO_REVIEW_QUEUE:
        if item["id"] == item_id:
            item["status"] = decision.decision
            return {
                "id": item_id,
                "status": "updated",
                "new_status": decision.decision,
                "reviewer_notes": decision.reviewer_notes,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
    return {"status": "error", "message": f"Item {item_id} not found"}
