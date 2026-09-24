from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


client = TestClient(app)


def main():

    print("=" * 80)
    print("PHASE 9.9C - TICKETS API TEST")
    print("=" * 80)

    # --------------------------------------------------
    # TEST 1 - CREATE TICKET
    # --------------------------------------------------

    print("\nTEST 1 - CREATE SUPPORT TICKET")
    print("-" * 80)

    payload = {
        "customer_id": 1,
        "subject": "API ticket test",
        "description": "Testing ticket creation through the FastAPI endpoint.",
        "priority": "normal",
        "order_id": 45821,
    }

    response = client.post(
        "/tickets",
        json=payload,
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert "ticket_id" in data
    assert data["customer_id"] == 1
    assert data["order_id"] == 45821
    assert data["subject"] == "API ticket test"
    assert data["priority"] == "normal"
    assert data["status"] == "open"

    ticket_id = data["ticket_id"]

    print("PASS: Ticket created successfully.")
    print("PASS: Ticket data is correct.")

    # --------------------------------------------------
    # TEST 2 - GET TICKET
    # --------------------------------------------------

    print("\nTEST 2 - GET CREATED TICKET")
    print("-" * 80)

    response = client.get(
        f"/tickets/{ticket_id}"
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["ticket_id"] == ticket_id
    assert data["customer_id"] == 1
    assert data["order_id"] == 45821

    print("PASS: Created ticket retrieved successfully.")
    print("PASS: Ticket data matches.")

    # --------------------------------------------------
    # TEST 3 - NON-EXISTENT TICKET
    # --------------------------------------------------

    print("\nTEST 3 - NON-EXISTENT TICKET")
    print("-" * 80)

    response = client.get(
        "/tickets/999999"
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 404

    print("PASS: Missing ticket returned HTTP 404.")
    print("PASS: Safe error message returned.")

    # --------------------------------------------------
    # TEST 4 - INVALID TICKET ID
    # --------------------------------------------------

    print("\nTEST 4 - INVALID TICKET ID")
    print("-" * 80)

    response = client.get(
        "/tickets/0"
    )

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 400

    print("PASS: Invalid ticket ID returned HTTP 400.")
    print("PASS: Validation error returned safely.")

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("PHASE 9.9C TICKETS API TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()