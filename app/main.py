# pyrefly: ignore [missing-import]
from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.logging_config import setup_logging

setup_logging()


app = FastAPI(
    title="NovaCart AI Customer Support",
    description=(
        "AI-powered customer support system using "
        "RAG and Groq."
    ),
    version="0.1.0",
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "NovaCart AI Customer Support API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }