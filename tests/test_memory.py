from langchain_core.messages import HumanMessage
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.agent.graph import build_agent_graph


def test_same_thread_preserves_conversation():
    graph = build_agent_graph()

    thread_id = "memory-test-same-thread"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result_1 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Where is my order 45821?"
                )
            ]
        },
        config=config,
    )

    assert "messages" in result_1
    assert len(result_1["messages"]) > 0

    result_2 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="When will it arrive?"
                )
            ]
        },
        config=config,
    )

    messages = result_2["messages"]

    # Previous conversation should still be present.
    assert len(messages) >= 4

    contents = [
        message.content
        for message in messages
        if hasattr(message, "content")
    ]

    assert any(
        "45821" in content
        for content in contents
        if isinstance(content, str)
    )


def test_different_threads_are_isolated():
    graph = build_agent_graph()

    thread_1 = "memory-isolation-001"
    thread_2 = "memory-isolation-002"

    config_1 = {
        "configurable": {
            "thread_id": thread_1
        }
    }

    config_2 = {
        "configurable": {
            "thread_id": thread_2
        }
    }

    # Conversation 1
    result_1 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="My order number is 45821."
                )
            ]
        },
        config=config_1,
    )

    # Conversation 2
    result_2 = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="My order number is 45825."
                )
            ]
        },
        config=config_2,
    )

    messages_1 = result_1["messages"]
    messages_2 = result_2["messages"]

    contents_1 = [
        message.content
        for message in messages_1
        if hasattr(message, "content")
    ]

    contents_2 = [
        message.content
        for message in messages_2
        if hasattr(message, "content")
    ]

    # Conversation 1 should contain its own order.
    assert any(
        "45821" in content
        for content in contents_1
        if isinstance(content, str)
    )

    # Conversation 2 should contain its own order.
    assert any(
        "45825" in content
        for content in contents_2
        if isinstance(content, str)
    )

    # Conversation 1 must not contain conversation 2's user message.
    assert not any(
        "45825" in content
        for content in contents_1
        if isinstance(content, str)
    )

    # Conversation 2 must not contain conversation 1's user message.
    assert not any(
        "45821" in content
        for content in contents_2
        if isinstance(content, str)
    )