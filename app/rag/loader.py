from pathlib import Path

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document


KNOWLEDGE_BASE_DIR = Path("knowledge_base")


def load_markdown_documents() -> list[Document]:
    """
    Load all Markdown files from the NovaCart knowledge base.

    Each file becomes a LangChain Document with source metadata.
    """

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: "
            f"{KNOWLEDGE_BASE_DIR}"
        )

    documents: list[Document] = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        try:
            content = file_path.read_text(
                encoding="utf-8"
            )

            if not content.strip():
                continue

            document = Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "file_type": "markdown",
                },
            )

            documents.append(document)

        except OSError as exc:
            raise RuntimeError(
                f"Failed to read knowledge-base file "
                f"{file_path}: {exc}"
            ) from exc

    if not documents:
        raise ValueError(
            "No Markdown documents were found "
            "in the knowledge base."
        )

    return documents