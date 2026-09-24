import json
import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.database import get_db
from app.database.models import Conversation, Message, Customer

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


class ConversationCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(default="New Support Conversation", max_length=255)
    customer_id: int | None = None
    category: str | None = None


class MessageOut(BaseModel):
    id: int
    sender: str
    content: str
    created_at: str
    meta: dict[str, Any] | None = None


class ConversationSummary(BaseModel):
    id: str
    title: str
    customer_id: int | None = None
    customer_name: str | None = None
    category: str | None = None
    status: str
    order_id: int | None = None
    message_count: int
    last_message: str | None = None
    created_at: str
    updated_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    customer_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    category: str | None = None
    status: str
    order_id: int | None = None
    created_at: str
    updated_at: str
    messages: list[MessageOut]


class FeedbackRequest(BaseModel):
    message_id: int | None = None
    feedback: str = Field(..., pattern="^(like|dislike|clear)$")


@router.get("", response_model=list[ConversationSummary])
def list_conversations(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List past conversations ordered by most recently updated.
    """
    conversations = (
        db.query(Conversation)
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
        .all()
    )

    results = []
    for conv in conversations:
        last_msg = conv.messages[-1].content if conv.messages else None
        cust_name = conv.customer.name if conv.customer else None
        results.append(
            ConversationSummary(
                id=conv.id,
                title=conv.title or "Support Conversation",
                customer_id=conv.customer_id,
                customer_name=cust_name,
                category=conv.category,
                status=conv.status,
                order_id=conv.order_id,
                message_count=len(conv.messages),
                last_message=last_msg[:80] + "..." if last_msg and len(last_msg) > 80 else last_msg,
                created_at=conv.created_at.isoformat() if conv.created_at else "",
                updated_at=conv.updated_at.isoformat() if conv.updated_at else "",
            )
        )
    return results


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full conversation and messages.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_out = []
    for m in conv.messages:
        meta_dict = None
        if m.meta_info:
            try:
                meta_dict = json.loads(m.meta_info)
            except Exception:
                meta_dict = None

        messages_out.append(
            MessageOut(
                id=m.id,
                sender=m.sender,
                content=m.content,
                created_at=m.created_at.isoformat() if m.created_at else "",
                meta=meta_dict,
            )
        )

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        customer_id=conv.customer_id,
        customer_name=conv.customer.name if conv.customer else None,
        customer_email=conv.customer.email if conv.customer else None,
        category=conv.category,
        status=conv.status,
        order_id=conv.order_id,
        created_at=conv.created_at.isoformat() if conv.created_at else "",
        updated_at=conv.updated_at.isoformat() if conv.updated_at else "",
        messages=messages_out,
    )


@router.post("", response_model=ConversationSummary)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new conversation or return existing one.
    """
    existing = db.query(Conversation).filter(Conversation.id == payload.id).first()
    if existing:
        return ConversationSummary(
            id=existing.id,
            title=existing.title,
            customer_id=existing.customer_id,
            customer_name=existing.customer.name if existing.customer else None,
            category=existing.category,
            status=existing.status,
            order_id=existing.order_id,
            message_count=len(existing.messages),
            created_at=existing.created_at.isoformat() if existing.created_at else "",
            updated_at=existing.updated_at.isoformat() if existing.updated_at else "",
        )

    new_conv = Conversation(
        id=payload.id,
        title=payload.title,
        customer_id=payload.customer_id,
        category=payload.category,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return ConversationSummary(
        id=new_conv.id,
        title=new_conv.title,
        customer_id=new_conv.customer_id,
        customer_name=None,
        category=new_conv.category,
        status=new_conv.status,
        order_id=None,
        message_count=0,
        last_message=None,
        created_at=new_conv.created_at.isoformat(),
        updated_at=new_conv.updated_at.isoformat(),
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a conversation and all its messages.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conv)
    db.commit()
    logger.info("Deleted conversation %s", conversation_id)
    return {"message": "Conversation deleted successfully", "id": conversation_id}


@router.post("/{conversation_id}/feedback")
def submit_feedback(
    conversation_id: str,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """
    Record user feedback (like/dislike) for a message or conversation.
    """
    if payload.message_id:
        msg = (
            db.query(Message)
            .filter(Message.id == payload.message_id, Message.conversation_id == conversation_id)
            .first()
        )
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found")

        meta = {}
        if msg.meta_info:
            try:
                meta = json.loads(msg.meta_info)
            except Exception:
                meta = {}
        meta["feedback"] = payload.feedback if payload.feedback != "clear" else None
        msg.meta_info = json.dumps(meta)
        db.commit()
        return {"status": "ok", "message_id": payload.message_id, "feedback": meta["feedback"]}

    return {"status": "ok", "feedback": payload.feedback}
