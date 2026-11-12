import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings

from .rag_ingestion import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    NoRagDataError,
    get_document_fingerprint,
    load_and_chunk_documents,
)
from .chroma import ChromaDatabase
from .vector_database import VectorDatabase


def get_database() -> VectorDatabase:
    return ChromaDatabase()


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    database = get_database()
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    index_manifest = {
        "provider": database.name,
        "corpus": get_document_fingerprint(),
        "embedding_model": embedding_model,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }
    manifest_path = database.get_manifest_path()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    vector_store = database.connect(OpenAIEmbeddings(model=embedding_model))

    try:
        saved_manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        saved_manifest = None

    if saved_manifest and all(
        saved_manifest.get(key) == value for key, value in index_manifest.items()
    ):
        return vector_store

    chunks = load_and_chunk_documents()
    existing_ids = saved_manifest.get("chunk_ids", []) if saved_manifest else []
    if not existing_ids:
        existing_ids = database.get_existing_ids(vector_store)

    chunk_ids = [
        hashlib.sha256(
            f"{chunk.metadata.get('source')}:{chunk.metadata.get('page')}:{index}:{chunk.page_content}".encode()
        ).hexdigest()
        for index, chunk in enumerate(chunks)
    ]
    database.delete_documents(vector_store, existing_ids)
    database.add_documents(vector_store, chunks, chunk_ids)
    manifest_path.write_text(json.dumps({**index_manifest, "chunk_ids": chunk_ids}, indent=2))
    return vector_store


def get_retriever():
    return get_vector_store().as_retriever(search_kwargs={"k": 4})


def retrieve_documents(query: str) -> list[Document]:
    documents = get_retriever().invoke(query)
    if not documents:
        raise NoRagDataError("No RAG data is available to answer this question.")
    return documents


def format_documents(documents: list[Document]) -> str:
    excerpts = []
    for document in documents:
        source = Path(document.metadata.get("source", "unknown")).name
        page = document.metadata.get("page")
        page_label = f", page {page + 1}" if isinstance(page, int) else ""
        excerpts.append(f"Source: {source}{page_label}\n{document.page_content}")
    return "\n\n".join(excerpts)


@tool
def search_faq(query: str) -> str:
    """Search the FAQ and policy documents for company-specific information."""
    return format_documents(retrieve_documents(query))


def main() -> None:
    database = get_database()
    get_vector_store()
    manifest = json.loads(database.get_manifest_path().read_text())
    chunk_count = len(manifest.get("chunk_ids", []))
    print(f"RAG ingestion complete: {chunk_count} chunks stored in {database.name}.")


if __name__ == "__main__":
    main()