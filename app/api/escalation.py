from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.tools.support_tools import escalate_to_human


router = APIRouter()


class EscalationRequest(BaseModel):
    customer_id: int | None = None
    reason: str
    order_id: int | None = None
    priority: str = "high"


@router.post("/escalate")
def escalate_api(request: EscalationRequest):

    result = escalate_to_human.invoke(
        {
            "customer_id": request.customer_id,
            "reason": request.reason,
            "order_id": request.order_id,
            "priority": request.priority,
        }
    )

    if not result.get("success"):
        error = result.get(
            "error",
            "Unable to escalate the issue at this time.",
        )

        if (
            "required for escalation" in error
            or "cannot be empty" in error
            or "Invalid priority" in error
        ):
            raise HTTPException(
                status_code=400,
                detail=error,
            )

        if "was not found" in error:
            raise HTTPException(
                status_code=404,
                detail=error,
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to escalate the issue at this time.",
        )

    return result