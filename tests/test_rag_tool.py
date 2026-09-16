from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from app.tools.rag_tools import (
    search_knowledge_base,
)


def test_rag_tool_rejects_empty_query():

    result = search_knowledge_base.invoke(
        {
            "query": ""
        }
    )

    assert result["success"] is False


def test_rag_tool_rejects_whitespace_query():

    result = search_knowledge_base.invoke(
        {
            "query": "   "
        }
    )

    assert result["success"] is False