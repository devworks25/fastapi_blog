from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from .rag_ingestion import DATA_DIR
from .vector_database import VectorDatabase


CHROMA_DIR = DATA_DIR / "chroma_db"
COLLECTION_NAME = "faq_documents"


class ChromaDatabase(VectorDatabase):
    name = "Chroma"

    def connect(self, embeddings: Embeddings) -> VectorStore:
        return Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
        )

    def get_manifest_path(self) -> Path:
        return CHROMA_DIR / "index_manifest.json"

    def get_existing_ids(self, vector_store: VectorStore) -> list[str]:
        return vector_store.get(include=["metadatas"])["ids"]