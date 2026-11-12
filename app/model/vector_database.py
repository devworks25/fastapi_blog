from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore


class VectorDatabase(ABC):
    name: str

    @abstractmethod
    def connect(self, embeddings: Embeddings) -> VectorStore:
        raise NotImplementedError

    @abstractmethod
    def get_manifest_path(self) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_existing_ids(self, vector_store: VectorStore) -> list[str]:
        raise NotImplementedError

    def add_documents(
        self,
        vector_store: VectorStore,
        documents: list[Document],
        ids: list[str],
    ) -> None:
        vector_store.add_documents(documents, ids=ids)

    def delete_documents(self, vector_store: VectorStore, ids: list[str]) -> None:
        if ids:
            vector_store.delete(ids=ids)