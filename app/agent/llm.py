from langchain_groq import ChatGroq
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.llm.groq_client import get_llm
from app.agent.tools import AGENT_TOOLS


def get_agent_llm() -> ChatGroq:
    llm = get_llm()

    return llm.bind_tools(
        AGENT_TOOLS
    )