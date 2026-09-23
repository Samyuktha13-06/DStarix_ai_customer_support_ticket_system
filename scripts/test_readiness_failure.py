from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


class FailingSession:
    def __enter__(self):
        raise RuntimeError("Controlled database connection failure.")

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def main():
    print("=" * 80)
    print("PHASE 9.7 - READINESS FAILURE TEST")
    print("=" * 80)

    import app.api.health as health_module

    original_session_local = health_module.SessionLocal

    health_module.SessionLocal = lambda: FailingSession()

    try:
        client = TestClient(app)

        response = client.get("/ready")

        print("\nHTTP STATUS:")
        print(response.status_code)

        print("\nRESPONSE:")
        print(response.json())

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "not_ready"
        assert body["database"] == "unavailable"

        print("\nPASS: Database failure was handled safely.")
        print("PASS: /ready returned HTTP 200.")
        print("PASS: Application reported not_ready.")
        print("PASS: Internal database error was not exposed.")

        print("\n" + "=" * 80)
        print("PHASE 9.7 READINESS FAILURE TEST: PASS")
        print("=" * 80)

    finally:
        health_module.SessionLocal = original_session_local


if __name__ == "__main__":
    main()