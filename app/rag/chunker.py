# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split documents into smaller semantically useful chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index

    if not chunks:
        raise ValueError(
            "Document chunking produced no chunks."
        )

    return chunks