import pytest

from app.tools.rag_tools import (
    search_knowledge_base,
)


@pytest.mark.integration
def test_rag_tool_finds_refund_policy():

    result = search_knowledge_base.invoke(
        {
            "query": "What is the refund policy?"
        }
    )

    assert result["success"] is True

    sources = [
        item["source"]
        for item in result["results"]
    ]

    assert "refund_policy.md" in sources