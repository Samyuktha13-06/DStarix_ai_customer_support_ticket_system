from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import text
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal


router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """
    Comprehensive health check.
    Confirms FastAPI service and database connectivity.
    """
    db_status = "connected"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unavailable: {exc}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": "0.1.0",
        "server_time": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/ready")
def readiness_check():
    """
    Readiness check.
    Confirms that the application can connect to the database.
    """
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "available",
            "version": "0.1.0",
        }
    except Exception:
        return {
            "status": "not_ready",
            "database": "unavailable",
            "version": "0.1.0",
        }