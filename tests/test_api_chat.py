from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_empty_chat_message_is_rejected():

    response = client.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_whitespace_chat_message_is_rejected():

    response = client.post(
        "/chat",
        json={"message": "   "},
    )

    assert response.status_code == 400


def test_chat_returns_answer():

    response = client.post(
        "/chat",
        json={
            "message": (
                "What is the refund policy?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0