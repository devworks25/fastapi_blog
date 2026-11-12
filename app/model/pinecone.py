import hashlib
from pathlib import Path

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from .rag_ingestion import DATA_DIR
from .vector_database import VectorDatabase


INDEX_NAME = "fastapi-blog-knowledge"
NAMESPACE = ""


class PineconeDatabase(VectorDatabase):
    name = "Pinecone"

    def connect(self, embeddings: Embeddings) -> VectorStore:
        from langchain_pinecone import PineconeVectorStore

        return PineconeVectorStore(
            index_name=INDEX_NAME,
            namespace=NAMESPACE or None,
            embedding=embeddings,
        )

    def get_manifest_path(self) -> Path:
        store_key = hashlib.sha256(
            f"{INDEX_NAME}:{NAMESPACE}".encode()
        ).hexdigest()[:12]
        return DATA_DIR / ".rag_manifests" / f"pinecone_{store_key}.json"

    def get_existing_ids(self, vector_store: VectorStore) -> list[str]:
        return []