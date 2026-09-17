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
    # but AgentService should reject it.
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
    response = client.post(
        "/chat",
        json={
            "thread_id": "test-basic-chat",
            "message": "Where is my order 45821?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_conversation_follow_up():
    """
    Test that the agent remembers context within
    the same conversation thread.
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
    assert len(data_1["answer"]) > 0

    # Second message does not mention the order ID.
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
    assert len(data_2["answer"]) > 0


def test_conversation_memory_isolation():
    """
    Test that two different thread IDs maintain
    separate conversation histories.
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


def test_new_conversation_has_no_previous_context():
    """
    A new thread should not inherit context from another thread.
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

    # The new conversation should not inherit order 45821.
    assert "45821" not in answer