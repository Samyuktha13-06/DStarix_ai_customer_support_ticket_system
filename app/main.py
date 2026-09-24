# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.core.logging_config import setup_logging
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.tickets import router as tickets_router
from app.api.escalation import router as escalation_router

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
app.include_router(health_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(tickets_router)
app.include_router(escalation_router)

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