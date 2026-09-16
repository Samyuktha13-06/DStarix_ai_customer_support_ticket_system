from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.services.agent_service import (
    get_agent_service,
)


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


class ChatResponse(BaseModel):

    answer: str


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:

        service = get_agent_service()

        result = service.chat(
            message=request.message
        )

        return ChatResponse(
            answer=result["answer"]
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
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