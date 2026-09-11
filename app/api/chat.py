# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

from app.services.rag_generation_service import (
    get_rag_generation_service,
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


class SourceReference(BaseModel):

    source: str | None = None
    chunk_id: int | None = None


class ChatResponse(BaseModel):

    answer: str
    sources: list[SourceReference]


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:

        service = get_rag_generation_service()

        result = service.generate_answer(
            query=request.message,
            top_k=4,
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
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
                "The customer-support service "
                "encountered an unexpected error."
            ),
        ) from exc