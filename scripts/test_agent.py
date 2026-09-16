from langchain_core.messages import HumanMessage
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.agent.graph import build_agent_graph


def main() -> None:

    graph = build_agent_graph()

    queries = [
        "How long does standard delivery take?",
        "Where is order 45821?",
        "What is the payment status for order 45821?",
        "My payment was deducted but my order 45824 failed.",
        "what is the refund policy?",
        "I want to speak to a human agent"
    ]

    for query in queries:

        print("\n" + "=" * 80)
        print(f"USER: {query}")
        print("=" * 80)

        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=query
                    )
                ]
            }
        )

        messages = result["messages"]

        final_message = messages[-1]

        print("\nASSISTANT:")
        print(final_message.content)

        print("\nMESSAGE FLOW:")

        for message in messages:
            print(
                f"- {type(message).__name__}"
            )


if __name__ == "__main__":
    main()