import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.tools import ALL_SUPPORT_TOOLS
from app.tools.rag_tools import search_knowledge_base


# Keep create_support_ticket available at the application level,
# but let the agent use escalate_to_human() for ticket creation
# and human-support escalation.
AGENT_TOOLS = [
    search_knowledge_base,
    *[
        tool
        for tool in ALL_SUPPORT_TOOLS
        if tool.name != "create_support_ticket"
    ],
]