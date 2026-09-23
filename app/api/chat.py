from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.agent_service import get_agent_service
from app.services.exceptions import AgentLLMError

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


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:
        service = get_agent_service()

        result = service.chat(
            message=request.message,
            thread_id=request.thread_id,
        )

        return ChatResponse(
            answer=result["answer"],
            escalated=result["escalated"],
            ticket_id=result["ticket_id"],
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

        raise HTTPException(
            status_code=500,
            detail=(
                "The customer-support agent "
                "encountered an unexpected error."
            ),
        ) from exc