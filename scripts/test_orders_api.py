from fastapi.testclient import TestClient
import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


def main():
    print("=" * 80)
    print("PHASE 9.9A - ORDERS API TEST")
    print("=" * 80)

    client = TestClient(app)

    # --------------------------------------------------------------
    # Existing order
    # --------------------------------------------------------------

    response = client.get("/orders/45821")

    print("\nTEST 1 - EXISTING ORDER")
    print("-" * 80)
    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    body = response.json()

    assert body["order_id"] == 45821
    assert body["customer_id"] == 1
    assert body["product"] == "NovaPhone X1"
    assert body["status"] == "Shipped"
    assert body["tracking_number"] == "NVC45821001"

    print("\nPASS: Existing order retrieved successfully.")
    print("PASS: Order data matches the seeded database.")

    # --------------------------------------------------------------
    # Non-existent order
    # --------------------------------------------------------------

    response = client.get("/orders/999999")

    print("\nTEST 2 - NON-EXISTENT ORDER")
    print("-" * 80)
    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "Order 999999 was not found."

    print("\nPASS: Missing order returned HTTP 404.")
    print("PASS: Safe error message returned.")

    # --------------------------------------------------------------
    # Invalid order ID
    # --------------------------------------------------------------

    response = client.get("/orders/0")

    print("\nTEST 3 - INVALID ORDER ID")
    print("-" * 80)
    print("HTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 400

    body = response.json()

    assert body["detail"] == "Order ID must be a positive integer."

    print("\nPASS: Invalid order ID returned HTTP 400.")
    print("PASS: Validation error returned safely.")

    print("\n" + "=" * 80)
    print("PHASE 9.9A ORDERS API TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()