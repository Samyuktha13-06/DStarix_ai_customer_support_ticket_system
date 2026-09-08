import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.llm import get_llm


def main() -> None:
    llm = get_llm()

    response = llm.invoke(
        "You are a customer support assistant. "
        "Reply with one short sentence confirming that you are ready."
    )

    print(response.content)


if __name__ == "__main__":
    main()