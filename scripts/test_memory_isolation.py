from langchain_core.messages import HumanMessage
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.agent.graph import build_agent_graph


def send_message(graph, thread_id, message):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        },
        config=config,
    )

    return result["messages"][-1].content


def main():
    graph = build_agent_graph()

    # -----------------------------
    # Conversation 1
    # -----------------------------
    thread_1 = "customer-001"

    print("\n" + "=" * 70)
    print("CONVERSATION 1")
    print("=" * 70)

    response = send_message(
        graph,
        thread_1,
        "Where is my order 45821?"
    )

    print("\nUser:")
    print("Where is my order 45821?")

    print("\nAgent:")
    print(response)

    response = send_message(
        graph,
        thread_1,
        "When will it arrive?"
    )

    print("\nUser:")
    print("When will it arrive?")

    print("\nAgent:")
    print(response)

    # -----------------------------
    # Conversation 2
    # -----------------------------
    thread_2 = "customer-002"

    print("\n" + "=" * 70)
    print("CONVERSATION 2")
    print("=" * 70)

    response = send_message(
        graph,
        thread_2,
        "Where is my order 45825?"
    )

    print("\nUser:")
    print("Where is my order 45825?")

    print("\nAgent:")
    print(response)

    response = send_message(
        graph,
        thread_2,
        "When will it arrive?"
    )

    print("\nUser:")
    print("When will it arrive?")

    print("\nAgent:")
    print(response)


if __name__ == "__main__":
    main()