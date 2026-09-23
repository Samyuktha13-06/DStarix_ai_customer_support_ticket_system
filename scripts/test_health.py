from fastapi.testclient import TestClient
import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


def main():
    print("=" * 80)
    print("PHASE 9.7 - HEALTH AND READINESS TEST")
    print("=" * 80)

    client = TestClient(app)

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    health_response = client.get("/health")

    print("\nHEALTH STATUS:")
    print(health_response.status_code)

    print("\nHEALTH RESPONSE:")
    print(health_response.json())

    assert health_response.status_code == 200

    health_body = health_response.json()

    assert health_body["status"] == "healthy"

    print("\nPASS: /health returned HTTP 200.")
    print("PASS: Application reported healthy status.")

    # ------------------------------------------------------------------
    # Readiness check
    # ------------------------------------------------------------------

    ready_response = client.get("/ready")

    print("\nREADINESS STATUS:")
    print(ready_response.status_code)

    print("\nREADINESS RESPONSE:")
    print(ready_response.json())

    assert ready_response.status_code == 200

    ready_body = ready_response.json()

    assert ready_body["status"] == "ready"
    assert ready_body["database"] == "available"

    print("\nPASS: /ready returned HTTP 200.")
    print("PASS: Database connection is available.")

    print("\n" + "=" * 80)
    print("PHASE 9.7 HEALTH TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()