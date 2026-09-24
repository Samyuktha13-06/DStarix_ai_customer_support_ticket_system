import json
import logging
import re
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.database.models import Conversation, Message, Customer
from app.services.agent_service import get_agent_service
from app.services.exceptions import AgentLLMError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    thread_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    customer_id: int | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty or contain only whitespace.")
        return value

    @field_validator("thread_id")
    @classmethod
    def validate_thread_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Thread ID cannot be empty or contain only whitespace.")
        return value


class ChatResponse(BaseModel):
    answer: str
    escalated: bool = False
    ticket_id: int | None = None
    order: dict | None = None
    payment: dict | None = None
    tools_used: list[dict] = []
    customer: dict | None = None


def _detect_category(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["order", "track", "delivery", "shipping", "shipped", "package"]):
        return "Orders"
    if any(k in lower for k in ["pay", "payment", "card", "charge", "refund", "receipt"]):
        return "Payments"
    if any(k in lower for k in ["return", "exchange", "cancel", "policy"]):
        return "Returns & Refunds"
    if any(k in lower for k in ["account", "login", "password", "email", "profile"]):
        return "Account"
    if any(k in lower for k in ["human", "agent", "escalate", "representative", "speak"]):
        return "Support Escalation"
    return "General Support"


def _generate_title(text: str) -> str:
    cleaned = re.sub(r'[\r\n]+', ' ', text).strip()
    if len(cleaned) <= 45:
        return cleaned
    return cleaned[:42] + "..."


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    logger.info(
        "Chat endpoint called | thread_id=%s | customer_id=%s | message_preview=%s",
        request.thread_id,
        request.customer_id,
        request.message[:80],
    )

    # 1. Conversation Persistence: store user message
    detected_cat = _detect_category(request.message)
    user_msg_id = None
    customer_info = None

    try:
        with SessionLocal() as db:
            conv = db.query(Conversation).filter(Conversation.id == request.thread_id).first()
            if not conv:
                conv = Conversation(
                    id=request.thread_id,
                    title=_generate_title(request.message),
                    customer_id=request.customer_id,
                    category=detected_cat,
                    status="active",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(conv)
                db.flush()
                logger.info("Created new persistent conversation | id=%s", request.thread_id)
            else:
                conv.updated_at = datetime.utcnow()
                if conv.title in ["New Support Conversation", "New Chat", "Support Conversation"]:
                    conv.title = _generate_title(request.message)
                if request.customer_id and not conv.customer_id:
                    conv.customer_id = request.customer_id
                if not conv.category:
                    conv.category = detected_cat

            user_msg = Message(
                conversation_id=request.thread_id,
                sender="user",
                content=request.message,
                created_at=datetime.utcnow(),
            )
            db.add(user_msg)
            db.commit()
            user_msg_id = user_msg.id
            logger.info("Persisted user message | id=%s | thread_id=%s", user_msg_id, request.thread_id)
    except Exception as exc:
        logger.warning("Could not persist user message in DB: %s", exc)

    # 2. Agent Execution
    try:
        service = get_agent_service()

        result = service.chat(
            message=request.message,
            thread_id=request.thread_id,
        )

        answer = result["answer"]
        escalated = result["escalated"]
        ticket_id = result["ticket_id"]
        order = result.get("order")
        payment = result.get("payment")
        tools_used = result.get("tools_used", [])

        # 3. Capture structured customer info if available
        try:
            with SessionLocal() as db:
                target_cust_id = None
                if order and order.get("customer_id"):
                    target_cust_id = order["customer_id"]
                elif request.customer_id:
                    target_cust_id = request.customer_id

                if target_cust_id:
                    cust = db.query(Customer).filter(Customer.id == target_cust_id).first()
                    if cust:
                        customer_info = {
                            "id": cust.id,
                            "name": cust.name,
                            "email": cust.email,
                        }
                        # Update conversation customer_id if not set
                        conv = db.query(Conversation).filter(Conversation.id == request.thread_id).first()
                        if conv and not conv.customer_id:
                            conv.customer_id = cust.id
                            db.commit()

                # Persist assistant message with rich metadata
                meta_payload = {
                    "escalated": escalated,
                    "ticket_id": ticket_id,
                    "order": order,
                    "payment": payment,
                    "tools_used": tools_used,
                }

                asst_msg = Message(
                    conversation_id=request.thread_id,
                    sender="assistant",
                    content=answer,
                    meta_info=json.dumps(meta_payload),
                    created_at=datetime.utcnow(),
                )
                db.add(asst_msg)

                # Update conversation metadata and order_id
                conv = db.query(Conversation).filter(Conversation.id == request.thread_id).first()
                if conv:
                    conv.updated_at = datetime.utcnow()
                    if order and order.get("order_id"):
                        conv.order_id = order["order_id"]
                    if escalated:
                        conv.status = "escalated"
                    db.commit()

                logger.info(
                    "Persisted assistant message | thread_id=%s | order_id=%s | tools_count=%d",
                    request.thread_id,
                    order.get("order_id") if order else None,
                    len(tools_used),
                )
        except Exception as exc:
            logger.warning("Could not persist assistant message in DB: %s", exc)

        return ChatResponse(
            answer=answer,
            escalated=escalated,
            ticket_id=ticket_id,
            order=order,
            payment=payment,
            tools_used=tools_used,
            customer=customer_info,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except AgentLLMError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "An unexpected error occurred in the chat endpoint."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The customer-support agent "
                "encountered an unexpected error."
            ),
        ) from exc