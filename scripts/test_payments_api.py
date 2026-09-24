import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from app.main import app
from fastapi.testclient import TestClient

from app.main import app


def main():
    print("=" * 80)
    print("PHASE 9.9B - PAYMENTS API TEST")
    print("=" * 80)

    client = TestClient(app)

    # --------------------------------------------------------------
    # Test 1: Existing payment
    # --------------------------------------------------------------

    response = client.get("/payments/45824")

    print("\nTEST 1 - EXISTING PAYMENT")
    print("-" * 80)

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    body = response.json()

    assert body["payment_id"] == 4
    assert body["order_id"] == 45824
    assert body["amount"] == 12999.0
    assert body["status"] == "Captured"
    assert "payment_date" in body

    print("\nPASS: Payment retrieved successfully.")
    print("PASS: Payment data matches the seeded database.")

    # --------------------------------------------------------------
    # Test 2: Non-existent payment/order
    # --------------------------------------------------------------

    response = client.get("/payments/999999")

    print("\nTEST 2 - NON-EXISTENT PAYMENT")
    print("-" * 80)

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == (
        "No payment record was found for order 999999."
    )

    print("\nPASS: Missing payment returned HTTP 404.")
    print("PASS: Safe error message returned.")

    # --------------------------------------------------------------
    # Test 3: Invalid order ID
    # --------------------------------------------------------------

    response = client.get("/payments/0")

    print("\nTEST 3 - INVALID ORDER ID")
    print("-" * 80)

    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 400

    body = response.json()

    assert body["detail"] == (
        "Order ID must be a positive integer."
    )

    print("\nPASS: Invalid order ID returned HTTP 400.")
    print("PASS: Validation error returned safely.")

    print("\n" + "=" * 80)
    print("PHASE 9.9B PAYMENTS API TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()