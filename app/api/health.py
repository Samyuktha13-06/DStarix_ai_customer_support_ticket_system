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
    Liveness check.

    Confirms that the FastAPI application is running.
    """
    return {
        "status": "healthy"
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
        }

    except Exception:
        return {
            "status": "not_ready",
            "database": "unavailable",
        }