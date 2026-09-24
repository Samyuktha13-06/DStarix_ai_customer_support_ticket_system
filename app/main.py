from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.logging_config import setup_logging
from app.database.database import Base, engine, SessionLocal
import app.database.models  # Ensure all models are registered

from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.tickets import router as tickets_router
from app.api.escalation import router as escalation_router
from app.api.conversations import router as conversations_router

setup_logging()

# Auto-create tables for conversation persistence and tickets
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NovaCart AI Customer Support",
    description=(
        "AI-powered customer support system using "
        "RAG and Groq."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(tickets_router)
app.include_router(escalation_router)
app.include_router(conversations_router)


@app.get("/")
def root():
    return {
        "message": "NovaCart AI Customer Support API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    db_status = "connected"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {e}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": "0.1.0",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }