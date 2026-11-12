import hashlib
from pathlib import Path

import xlrd
from docx2txt import process as extract_docx_text
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openpyxl import load_workbook
from pptx import Presentation


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
SUPPORTED_EXTENSIONS = {
    ".csv",
    ".docx",
    ".html",
    ".json",
    ".log",
    ".md",
    ".pdf",
    ".pptx",
    ".rst",
    ".txt",
    ".xls",
    ".xlsx",
}


class NoRagDataError(RuntimeError):
    pass


def load_documents() -> list[Document]:
    files = sorted(
        path
        for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        supported_types = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise NoRagDataError(
            f"No supported RAG documents found in app/data. Supported types: {supported_types}."
        )

    documents = []
    for path in files:
        try:
            documents.extend(_load_file(path))
        except Exception as exc:
            raise NoRagDataError(f"Could not read {path.name}: {exc}") from exc

    if not documents:
        raise NoRagDataError("No readable content found in the documents in app/data.")
    return documents


def _load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix == ".docx":
        text = extract_docx_text(str(path))
        return [Document(page_content=text, metadata={"source": str(path)})] if text.strip() else []
    if suffix in {".txt", ".md", ".rst", ".log", ".json", ".html"}:
        return TextLoader(str(path), encoding="utf-8").load()
    if suffix == ".csv":
        return CSVLoader(str(path), encoding="utf-8").load()
    if suffix == ".xlsx":
        return _load_xlsx(path)
    if suffix == ".xls":
        return _load_xls(path)
    if suffix == ".pptx":
        return _load_pptx(path)
    return []


def _load_xlsx(path: Path) -> list[Document]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    documents = []
    for sheet in workbook.worksheets:
        rows = [
            " | ".join(str(value) for value in row if value is not None)
            for row in sheet.iter_rows(values_only=True)
        ]
        text = "\n".join(row for row in rows if row.strip())
        if text:
            documents.append(Document(page_content=text, metadata={"source": str(path), "sheet": sheet.title}))
    workbook.close()
    return documents


def _load_xls(path: Path) -> list[Document]:
    workbook = xlrd.open_workbook(str(path), on_demand=True)
    documents = []
    for sheet in workbook.sheets():
        rows = [
            " | ".join(str(value) for value in sheet.row_values(index) if value != "")
            for index in range(sheet.nrows)
        ]
        text = "\n".join(row for row in rows if row.strip())
        if text:
            documents.append(Document(page_content=text, metadata={"source": str(path), "sheet": sheet.name}))
    workbook.release_resources()
    return documents


def _load_pptx(path: Path) -> list[Document]:
    presentation = Presentation(str(path))
    documents = []
    for index, slide in enumerate(presentation.slides, start=1):
        text = "\n".join(
            shape.text.strip()
            for shape in slide.shapes
            if getattr(shape, "has_text_frame", False) and shape.text.strip()
        )
        if text:
            documents.append(Document(page_content=text, metadata={"source": str(path), "page": index - 1}))
    return documents


def load_and_chunk_documents() -> list[Document]:
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    ).split_documents(load_documents())
    if not chunks:
        raise NoRagDataError("No readable text found in the documents in app/data.")
    return chunks


def get_document_fingerprint() -> str:
    files = sorted(
        path
        for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        raise NoRagDataError("No supported RAG documents found in the app/data folder.")

    fingerprint = hashlib.sha256()
    for path in files:
        fingerprint.update(path.name.encode())
        fingerprint.update(path.read_bytes())
    return fingerprint.hexdigest()