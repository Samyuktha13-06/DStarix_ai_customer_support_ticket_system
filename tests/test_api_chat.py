from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_empty_message():
    response = client.post(
        "/chat",
        json={
            "thread_id": "test-empty-message",
            "message": "",
        },
    )

    assert response.status_code == 422


def test_whitespace_message():
    response = client.post(
        "/chat",
        json={
            "thread_id": "test-whitespace-message",
            "message": "   ",
        },
    )

    # Pydantic accepts whitespace because it has length,
    # but AgentService rejects it.
    assert response.status_code == 400


def test_missing_thread_id():
    response = client.post(
        "/chat",
        json={
            "message": "Where is my order 45821?",
        },
    )

    assert response.status_code == 422


def test_empty_thread_id():
    response = client.post(
        "/chat",
        json={
            "thread_id": "",
            "message": "Where is my order 45821?",
        },
    )

    assert response.status_code == 422


def test_basic_chat():
    """
    Test a normal customer-support question.

    A normal question should return:
    - an answer
    - escalated = False
    - ticket_id = None
    """

    response = client.post(
        "/chat",
        json={
            "thread_id": "test-basic-chat",
            "message": "How long does standard delivery take?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0

    assert "escalated" in data
    assert data["escalated"] is False

    assert "ticket_id" in data
    assert data["ticket_id"] is None


def test_conversation_follow_up():
    """
    Test that conversation memory works across
    multiple requests using the same thread_id.
    """

    thread_id = "test-follow-up-45821"

    # First message establishes the order context.
    response_1 = client.post(
        "/chat",
        json={
            "thread_id": thread_id,
            "message": "Where is my order 45821?",
        },
    )

    assert response_1.status_code == 200

    data_1 = response_1.json()

    assert "answer" in data_1
    assert isinstance(data_1["answer"], str)
    assert len(data_1["answer"]) > 0

    assert data_1["escalated"] is False
    assert data_1["ticket_id"] is None

    # Second message refers to the previous order indirectly.
    response_2 = client.post(
        "/chat",
        json={
            "thread_id": thread_id,
            "message": "When will it arrive?",
        },
    )

    assert response_2.status_code == 200

    data_2 = response_2.json()

    assert "answer" in data_2
    assert isinstance(data_2["answer"], str)
    assert len(data_2["answer"]) > 0

    assert data_2["escalated"] is False
    assert data_2["ticket_id"] is None


def test_conversation_memory_isolation():
    """
    Test that different thread IDs maintain separate
    conversation histories.
    """

    thread_1 = "test-isolation-customer-001"
    thread_2 = "test-isolation-customer-002"

    # Conversation 1 establishes order 45821.
    response_1 = client.post(
        "/chat",
        json={
            "thread_id": thread_1,
            "message": "Where is my order 45821?",
        },
    )

    assert response_1.status_code == 200

    # Conversation 2 establishes order 45825.
    response_2 = client.post(
        "/chat",
        json={
            "thread_id": thread_2,
            "message": "Where is my order 45825?",
        },
    )

    assert response_2.status_code == 200

    # Follow-up in conversation 1.
    response_3 = client.post(
        "/chat",
        json={
            "thread_id": thread_1,
            "message": "When will it arrive?",
        },
    )

    assert response_3.status_code == 200

    # Follow-up in conversation 2.
    response_4 = client.post(
        "/chat",
        json={
            "thread_id": thread_2,
            "message": "When will it arrive?",
        },
    )

    assert response_4.status_code == 200

    answer_1 = response_3.json()["answer"]
    answer_2 = response_4.json()["answer"]

    assert isinstance(answer_1, str)
    assert isinstance(answer_2, str)

    assert len(answer_1) > 0
    assert len(answer_2) > 0

    assert response_3.json()["escalated"] is False
    assert response_4.json()["escalated"] is False

    assert response_3.json()["ticket_id"] is None
    assert response_4.json()["ticket_id"] is None


def test_new_conversation_has_no_previous_context():
    """
    A new thread should not inherit context from
    an existing conversation.
    """

    old_thread = "test-old-conversation"
    new_thread = "test-new-conversation"

    # Establish order context in the first conversation.
    response_1 = client.post(
        "/chat",
        json={
            "thread_id": old_thread,
            "message": "My order number is 45821. Where is it?",
        },
    )

    assert response_1.status_code == 200

    # Start a completely new conversation without an order ID.
    response_2 = client.post(
        "/chat",
        json={
            "thread_id": new_thread,
            "message": "When will it arrive?",
        },
    )

    assert response_2.status_code == 200

    answer = response_2.json()["answer"]

    assert isinstance(answer, str)
    assert len(answer) > 0

    # The new conversation should not inherit the old order.
    assert "45821" not in answer

    assert response_2.json()["escalated"] is False
    assert response_2.json()["ticket_id"] is None


def test_chat_escalation_returns_ticket_id():
    """
    Test that an automatically escalated issue returns
    both escalation status and the generated ticket ID.
    """

    response = client.post(
        "/chat",
        json={
            "thread_id": "test-api-escalation-45824",
            "message": (
                "I want to speak with a human support "
                "representative about order 45824."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0

    assert "escalated" in data
    assert data["escalated"] is True

    assert "ticket_id" in data
    assert data["ticket_id"] is not None
    assert isinstance(data["ticket_id"], int)


def test_payment_order_issue_escalates():
    """
    Test the important payment/order inconsistency scenario.

    Order 45824 is Failed while its payment is Captured.
    The agent should escalate the issue.
    """

    response = client.post(
        "/chat",
        json={
            "thread_id": "test-api-payment-escalation-45824",
            "message": (
                "My payment was deducted but "
                "my order 45824 failed."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0

    assert data["escalated"] is True

    assert data["ticket_id"] is not None
    assert isinstance(data["ticket_id"], int)


def test_chat_response_structure():
    """
    Verify that every successful /chat response contains
    the complete Phase 8.4 response structure.
    """

    response = client.post(
        "/chat",
        json={
            "thread_id": "test-response-structure",
            "message": "What is your cancellation policy?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "answer",
        "escalated",
        "ticket_id",
    }

    assert isinstance(data["answer"], str)
    assert isinstance(data["escalated"], bool)

    if data["escalated"]:
        assert data["ticket_id"] is not None
        assert isinstance(data["ticket_id"], int)
    else:
        assert data["ticket_id"] is None