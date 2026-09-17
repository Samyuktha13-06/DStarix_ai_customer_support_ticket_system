from langchain_core.messages import HumanMessage
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.agent.graph import build_agent_graph


def main():
    graph = build_agent_graph()

    thread_id = "memory-test-001"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\n===== MESSAGE 1 =====")

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

    print(result_1["messages"][-1].content)

    print("\n===== MESSAGE 2 =====")

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

    print(result_2["messages"][-1].content)


if __name__ == "__main__":
    main()