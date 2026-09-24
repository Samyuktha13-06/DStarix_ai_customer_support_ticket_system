from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


client = TestClient(app)


def main():

    print("=" * 80)
    print("PHASE 9.9D - ESCALATION API TEST")
    print("=" * 80)

    # --------------------------------------------------
    # TEST 1 - ESCALATE USING ORDER ID
    # --------------------------------------------------

    print("\nTEST 1 - ESCALATE USING ORDER ID")
    print("-" * 80)

    payload = {
        "order_id": 45821,
        "reason": "Customer requested human support.",
        "priority": "high",
    }

    response = client.post(
        "/escalate",
        json=payload,
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["escalated"] is True
    assert "ticket_id" in data
    assert data["order_id"] == 45821
    assert data["priority"] == "high"

    ticket_id = data["ticket_id"]

    print("PASS: Escalation succeeded.")
    print("PASS: Support ticket was created.")
    print(f"PASS: Ticket ID: {ticket_id}")

    # --------------------------------------------------
    # TEST 2 - MISSING REASON
    # --------------------------------------------------

    print("\nTEST 2 - MISSING ESCALATION REASON")
    print("-" * 80)

    payload = {
        "order_id": 45821,
        "reason": "",
        "priority": "high",
    }

    response = client.post(
        "/escalate",
        json=payload,
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 400

    print("PASS: Empty escalation reason returned HTTP 400.")
    print("PASS: Validation error returned safely.")

    # --------------------------------------------------
    # TEST 3 - INVALID ORDER
    # --------------------------------------------------

    print("\nTEST 3 - NON-EXISTENT ORDER")
    print("-" * 80)

    payload = {
        "order_id": 999999,
        "reason": "Customer needs human assistance.",
        "priority": "high",
    }

    response = client.post(
        "/escalate",
        json=payload,
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 404

    print("PASS: Missing order returned HTTP 404.")
    print("PASS: Safe error message returned.")

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("PHASE 9.9D ESCALATION API TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()