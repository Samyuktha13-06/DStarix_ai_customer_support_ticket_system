class AgentServiceError(Exception):
    """
    Base exception for controlled agent-service failures.
    """


class AgentLLMError(AgentServiceError):
    """
    Raised when the LLM/API cannot complete an agent request.
    """