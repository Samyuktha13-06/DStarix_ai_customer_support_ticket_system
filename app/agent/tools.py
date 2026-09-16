from pathlib import Path
import sys

# Add app/ directory to PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.tools import ALL_SUPPORT_TOOLS
from app.tools.rag_tools import search_knowledge_base


AGENT_TOOLS = [
    search_knowledge_base,
    *ALL_SUPPORT_TOOLS,
]