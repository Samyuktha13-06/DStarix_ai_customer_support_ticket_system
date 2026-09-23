import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.agent_service import AgentService
from app.services.exceptions import AgentLLMError


class FailingGraph:

    def invoke(self, *args, **kwargs):
        raise RuntimeError(
            "Controlled test failure: Groq API unavailable."
        )


def main():

    service = AgentService.__new__(AgentService)

    # Replace the real graph with a controlled failing graph.
    service.graph = FailingGraph()

    try:

        service.chat(
            message="What is your refund policy?",
            thread_id="phase9-llm-failure-001",
        )

        raise AssertionError(
            "AgentService did not raise AgentLLMError."
        )

    except AgentLLMError as exc:

        expected_message = (
            "The AI support service is temporarily unavailable."
        )

        assert str(exc) == expected_message

        print("\n" + "=" * 80)
        print("PHASE 9.4 - LLM FAILURE TEST")
        print("=" * 80)

        print("\nPASS: LLM/graph failure was caught.")

        print("\nControlled exception:")
        print(
            "Controlled test failure: "
            "Groq API unavailable."
        )

        print("\nApplication-level exception:")
        print(str(exc))

        print("\nPASS: Internal provider error was not exposed.")

        print("\n" + "=" * 80)
        print("PHASE 9.4 RESULT: PASS")
        print("=" * 80)


if __name__ == "__main__":
    main()