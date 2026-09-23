import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.test_rag_failure_graph import build_test_rag_graph
from scripts.test_rag_failure_tool import (
    controlled_rag_no_results_tool,
    controlled_rag_retrieval_failure_tool,
)


def run_test(
    test_name: str,
    test_tool,
    expected_error: str,
):
    graph = build_test_rag_graph(test_tool)

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "What is NovaCart's policy "
                        "for a completely hypothetical "
                        "product scenario?"
                    ),
                }
            ]
        }
    )

    messages = result["messages"]

    tool_calls = []

    for message in messages:
        if getattr(message, "tool_calls", None):
            tool_calls.extend(message.tool_calls)

    assert tool_calls, (
        f"No tool call generated for {test_name}."
    )

    assert len(tool_calls) == 1, (
        f"Expected exactly one tool call for {test_name}, "
        f"got {len(tool_calls)}."
    )

    assert tool_calls[0]["name"] == test_tool.name, (
        f"Unexpected tool called: "
        f"{tool_calls[0]['name']}"
    )

    tool_messages = [
        message
        for message in messages
        if getattr(message, "type", None) == "tool"
    ]

    assert tool_messages, (
        f"No tool result returned for {test_name}."
    )

    tool_result = json.loads(
        tool_messages[0].content
    )

    assert tool_result["success"] is False

    assert tool_result["error"] == expected_error

    final_message = messages[-1]

    assert getattr(
        final_message,
        "type",
        None,
    ) == "ai"

    final_response = final_message.content

    assert final_response.strip()

    response_lower = final_response.lower()

    forbidden_claims = [
        "you are eligible",
        "you are entitled",
        "novacart allows",
        "novacart policy states",
    ]

    for claim in forbidden_claims:
        assert claim not in response_lower, (
            f"Potential hallucinated policy claim: {claim}"
        )

    print(f"\nPASS: {test_name}")
    print("\nTool called:")
    print(tool_calls[0]["name"])

    print("\nTool result:")
    print(json.dumps(tool_result, indent=2))

    print("\nFinal response:")
    print(final_response)


def main():
    print("\n" + "=" * 80)
    print("PHASE 9.3 - RAG FAILURE HANDLING")
    print("=" * 80)

    print("\nTEST 1: No relevant KB results")

    run_test(
        test_name="No relevant KB results",
        test_tool=controlled_rag_no_results_tool,
        expected_error=(
            "No relevant information was found "
            "in the NovaCart knowledge base."
        ),
    )

    print("\n" + "-" * 80)

    print("\nTEST 2: Retrieval system failure")

    run_test(
        test_name="Retrieval system failure",
        test_tool=controlled_rag_retrieval_failure_tool,
        expected_error=(
            "The knowledge base could not be "
            "searched at this time."
        ),
    )

    print("\n" + "=" * 80)
    print("PHASE 9.3 RESULT: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()