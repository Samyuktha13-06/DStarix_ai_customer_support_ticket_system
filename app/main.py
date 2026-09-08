# pyrefly: ignore [missing-import]
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging_config import setup_logging


settings = get_settings()

setup_logging(settings.log_level)


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered customer support and "
        "ticket automation system"
    ),
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Customer Support System is running",
        "environment": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }