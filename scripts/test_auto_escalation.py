from langchain_core.messages import HumanMessage
import sys

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.agent.graph import build_agent_graph

#from app.database.database import SessionLocal
from app.services.order_service import get_order_service


def run_test(graph, thread_id, message):
    print("\n" + "=" * 80)
    print(f"THREAD: {thread_id}")
    print(f"USER: {message}")
    print("=" * 80)

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

    messages = result.get("messages", [])

    print("\nMESSAGE FLOW")
    print("-" * 80)

    for message in messages:
        print(f"\n[{message.type}]")

        if hasattr(message, "content"):
            print(message.content)

        if hasattr(message, "tool_calls") and message.tool_calls:
            print("Tool calls:")
            for tool_call in message.tool_calls:
                print(tool_call)

    print("\nFINAL RESPONSE")
    print("-" * 80)
    print(messages[-1].content)

    return result


def main():
    graph = build_agent_graph()

    # Test 1: explicit human escalation
    run_test(
        graph,
        "auto-escalation-human-request",
        "I want to speak with a human support representative about order 45824.",
    )


    #Test 2
    run_test(
    graph,
    "auto-escalation-payment-issue",
    "My payment was deducted but my order 45824 failed.",
)


if __name__ == "__main__":
    main()