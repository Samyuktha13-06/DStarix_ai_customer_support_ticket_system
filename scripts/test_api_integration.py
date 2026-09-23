from fastapi.testclient import TestClient
import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


def print_result(name: str, response):
    print(f"\n{name}")
    print("-" * 80)
    print(f"HTTP STATUS: {response.status_code}")
    print(f"RESPONSE: {response.json()}")


def test_health(client: TestClient):
    response = client.get("/health")

    print_result("TEST 1 - HEALTH CHECK", response)

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    print("PASS: Health endpoint is working.")


def test_readiness(client: TestClient):
    response = client.get("/ready")

    print_result("TEST 2 - READINESS CHECK", response)

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "available"

    print("PASS: Readiness endpoint and database are working.")


def test_knowledge_base_query(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "What is your refund policy?",
            "thread_id": "phase9-8-kb-001",
        },
    )

    print_result("TEST 3 - KNOWLEDGE BASE QUERY", response)

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert body["answer"].strip()

    assert "escalated" in body
    assert "ticket_id" in body

    # The answer should contain information related to the refund policy.
    answer = body["answer"].lower()

    assert (
        "refund" in answer
        or "7 calendar days" in answer
    )

    print("PASS: Knowledge-base query returned a valid grounded response.")


def test_order_query(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "What is the status of order 45821?",
            "thread_id": "phase9-8-order-001",
        },
    )

    print_result("TEST 4 - ORDER QUERY", response)

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert body["answer"].strip()

    answer = body["answer"].lower()

    # Order 45821 is seeded as Shipped.
    assert "45821" in answer
    assert "shipped" in answer

    print("PASS: Order query returned the expected order information.")


def test_explicit_human_escalation(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "I want to speak with a human support representative about order 45824.",
            "thread_id": "phase9-8-escalation-001",
        },
    )

    print_result("TEST 5 - HUMAN ESCALATION", response)

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert body["answer"].strip()

    assert body["escalated"] is True
    assert body["ticket_id"] is not None

    print("PASS: Explicit human request triggered escalation.")
    print(f"PASS: Ticket ID returned: {body['ticket_id']}")


def test_invalid_empty_message(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "",
            "thread_id": "phase9-8-invalid-001",
        },
    )

    print_result("TEST 6 - EMPTY MESSAGE", response)

    assert response.status_code == 422

    print("PASS: Empty message rejected with HTTP 422.")


def test_missing_thread_id(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "What is your refund policy?",
        },
    )

    print_result("TEST 7 - MISSING THREAD ID", response)

    assert response.status_code == 422

    print("PASS: Missing thread_id rejected with HTTP 422.")


def test_response_schema(client: TestClient):
    response = client.post(
        "/chat",
        json={
            "message": "What are your standard shipping times?",
            "thread_id": "phase9-8-schema-001",
        },
    )

    print_result("TEST 8 - RESPONSE SCHEMA", response)

    assert response.status_code == 200

    body = response.json()

    expected_fields = {
        "answer",
        "escalated",
        "ticket_id",
    }

    assert expected_fields.issubset(body.keys())

    assert isinstance(body["answer"], str)
    assert isinstance(body["escalated"], bool)

    if body["ticket_id"] is not None:
        assert isinstance(body["ticket_id"], int)

    print("PASS: Response conforms to the expected API schema.")


def main():
    print("=" * 80)
    print("PHASE 9.8 - API INTEGRATION TEST")
    print("=" * 80)

    client = TestClient(app)

    tests = [
        test_health,
        test_readiness,
        test_knowledge_base_query,
        test_order_query,
        test_explicit_human_escalation,
        test_invalid_empty_message,
        test_missing_thread_id,
        test_response_schema,
    ]

    passed = 0

    for test in tests:
        test(client)
        passed += 1

    print("\n" + "=" * 80)
    print(f"PHASE 9.8 API INTEGRATION TEST: PASS")
    print(f"Tests passed: {passed}/{len(tests)}")
    print("=" * 80)


if __name__ == "__main__":
    main()