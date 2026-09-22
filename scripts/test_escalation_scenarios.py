import json

from langchain_core.messages import HumanMessage
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.agent.graph import build_agent_graph


def extract_tool_results(messages):
    """
    Extract structured results returned by tools.
    """

    results = []

    for message in messages:

        if getattr(message, "type", None) != "tool":
            continue

        content = getattr(message, "content", None)

        if not content:
            continue

        try:
            if isinstance(content, str):
                data = json.loads(content)
            elif isinstance(content, dict):
                data = content
            else:
                continue

        except (json.JSONDecodeError, TypeError):
            continue

        results.append(data)

    return results


def extract_tool_calls(messages):
    """
    Extract tool calls made by the AI.
    """

    tool_calls = []

    for message in messages:

        calls = getattr(message, "tool_calls", None)

        if not calls:
            continue

        for call in calls:
            tool_calls.append(call)

    return tool_calls


def run_scenario(graph, name, thread_id, user_message):

    print("\n")
    print("=" * 90)
    print(f"SCENARIO: {name}")
    print("=" * 90)

    print(f"\nUSER:")
    print(user_message)

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=user_message
                )
            ]
        },
        config=config,
    )

    messages = result.get("messages", [])

    if not messages:
        raise RuntimeError(
            "Agent returned no messages."
        )

    tool_calls = extract_tool_calls(messages)
    tool_results = extract_tool_results(messages)

    print("\nTOOL CALLS:")
    if tool_calls:
        for call in tool_calls:
            print(
                f"- {call.get('name')} "
                f"{call.get('args')}"
            )
    else:
        print("- No tools called.")

    print("\nTOOL RESULTS:")
    if tool_results:
        for tool_result in tool_results:
            print(tool_result)
    else:
        print("- No tool results.")

    print("\nFINAL RESPONSE:")
    print(messages[-1].content)

    return {
        "messages": messages,
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "answer": messages[-1].content,
    }


def find_escalation_result(tool_results):

    for result in tool_results:

        if (
            isinstance(result, dict)
            and result.get("escalated") is True
        ):
            return result

    return None


def main():

    graph = build_agent_graph()

    # ==========================================================
    # 1. Explicit human escalation
    # ==========================================================

    result_1 = run_scenario(
        graph=graph,
        name="Explicit Human Request",
        thread_id="phase85-human-request",
        user_message=(
            "I want to speak with a human support "
            "representative about order 45824."
        ),
    )

    escalation_1 = find_escalation_result(
        result_1["tool_results"]
    )

    assert escalation_1 is not None, (
        "Explicit human request did not produce "
        "a successful escalation."
    )

    assert escalation_1["ticket_id"] is not None

    print("\nPASS: Explicit human escalation")


    # ==========================================================
    # 2. Payment/order inconsistency
    # ==========================================================

    result_2 = run_scenario(
        graph=graph,
        name="Payment Deducted but Order Failed",
        thread_id="phase85-payment-mismatch",
        user_message=(
            "My payment was deducted but "
            "my order 45824 failed."
        ),
    )

    escalation_2 = find_escalation_result(
        result_2["tool_results"]
    )

    assert escalation_2 is not None, (
        "Payment/order inconsistency was not escalated."
    )

    assert escalation_2["ticket_id"] is not None

    print("\nPASS: Payment/order inconsistency escalation")


    # ==========================================================
    # 3. Policy exception
    # ==========================================================

    result_3 = run_scenario(
        graph=graph,
        name="Refund Policy Exception",
        thread_id="phase85-policy-exception",
        user_message=(
            "My order 45823 arrived outside the refund period, "
            "but the product is defective. "
            "I want an exception to the refund policy."
        ),
    )

    escalation_3 = find_escalation_result(
        result_3["tool_results"]
    )

    assert escalation_3 is not None, (
        "Policy exception was not escalated."
    )

    assert escalation_3["ticket_id"] is not None

    print("\nPASS: Policy exception escalation")


    # ==========================================================
    # 4. Normal knowledge-base question
    # ==========================================================

    result_4 = run_scenario(
        graph=graph,
        name="Normal Refund Policy Question",
        thread_id="phase85-normal-policy",
        user_message=(
            "What is your refund policy?"
        ),
    )

    escalation_4 = find_escalation_result(
        result_4["tool_results"]
    )

    assert escalation_4 is None, (
        "Normal policy question incorrectly "
        "created an escalation."
    )

    print("\nPASS: Normal policy question did not escalate")


    # ==========================================================
    # 5. Normal order query
    # ==========================================================

    result_5 = run_scenario(
        graph=graph,
        name="Normal Order Status",
        thread_id="phase85-normal-order",
        user_message=(
            "Where is my order 45821?"
        ),
    )

    escalation_5 = find_escalation_result(
        result_5["tool_results"]
    )

    assert escalation_5 is None, (
        "Normal order query incorrectly "
        "created an escalation."
    )

    print("\nPASS: Normal order query did not escalate")


    # ==========================================================
    # 6. Invalid order
    # ==========================================================

    result_6 = run_scenario(
        graph=graph,
        name="Invalid Order ID",
        thread_id="phase85-invalid-order",
        user_message=(
            "Where is my order 99999?"
        ),
    )

    print("\nPASS: Invalid order handled without crash")


    # ==========================================================
    # Final summary
    # ==========================================================

    print("\n")
    print("=" * 90)
    print("PHASE 8.5 ESCALATION TEST SUMMARY")
    print("=" * 90)

    print("1. Explicit human request       : PASS")
    print("2. Payment/order inconsistency  : PASS")
    print("3. Policy exception             : PASS")
    print("4. Normal policy question       : PASS")
    print("5. Normal order query           : PASS")
    print("6. Invalid order                : PASS")

    print("\nAll Phase 8.5 scenarios passed.")


if __name__ == "__main__":
    main()