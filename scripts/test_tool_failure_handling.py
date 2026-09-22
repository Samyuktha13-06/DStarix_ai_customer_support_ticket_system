
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.test_failure_graph import build_test_graph


def main():
    graph = build_test_graph()

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Where is my order 45821?",
                }
            ]
        }
    )

    messages = result["messages"]

    print("\n" + "=" * 80)
    print("PHASE 9.2 - CONTROLLED TOOL FAILURE TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. Verify the controlled failure tool was called
    # ---------------------------------------------------------

    tool_calls = []

    for message in messages:
        if getattr(message, "tool_calls", None):
            tool_calls.extend(message.tool_calls)

    assert tool_calls, "No tool call was generated."

    assert any(
        call["name"] == "controlled_failure_tool"
        for call in tool_calls
    ), "controlled_failure_tool was not called."

    print("\nPASS: Controlled failure tool was called.")

    # ---------------------------------------------------------
    # 2. Verify the tool returned success=False
    # ---------------------------------------------------------

    tool_messages = [
        message
        for message in messages
        if getattr(message, "type", None) == "tool"
    ]

    assert tool_messages, "No tool result was returned."

    tool_result = tool_messages[0].content

    assert '"success": false' in tool_result.lower()

    print("PASS: Tool returned success=false.")

    # ---------------------------------------------------------
    # 3. Verify the agent produced a final response
    # ---------------------------------------------------------

    final_message = messages[-1]

    assert getattr(final_message, "type", None) == "ai"

    final_response = final_message.content

    assert final_response.strip()

    print("PASS: Agent produced a final response.")

    # ---------------------------------------------------------
    # 4. Verify the response does not fabricate order status
    # ---------------------------------------------------------

    forbidden_claims = [
        "has been shipped",
        "has been delivered",
        "was delivered",
        "is currently shipped",
        "will arrive",
    ]

    response_lower = final_response.lower()

    for claim in forbidden_claims:
        assert claim not in response_lower, (
            f"Potentially fabricated order status found: {claim}"
        )

    print("PASS: No fabricated order status detected.")

    # ---------------------------------------------------------
    # 5. Verify no second tool was called after failure
    # ---------------------------------------------------------

    tool_call_names = [
        call["name"]
        for call in tool_calls
    ]

    assert tool_call_names == [
        "controlled_failure_tool"
    ], (
        "Unexpected additional tool calls detected: "
        f"{tool_call_names}"
    )

    print("PASS: Agent did not retry with another tool.")

    # ---------------------------------------------------------
    # 6. Display final response
    # ---------------------------------------------------------

    print("\nFINAL RESPONSE:")
    print(final_response)

    print("\n" + "=" * 80)
    print("PHASE 9.2 RESULT: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()