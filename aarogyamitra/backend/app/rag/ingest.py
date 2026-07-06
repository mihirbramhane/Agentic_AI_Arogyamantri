"""Build the RAG vector store from official scheme guideline PDFs.

Usage (from backend/):
    python -m app.rag.ingest

Place official scheme PDFs (PM-JAY, Aarogyasri, etc.) in data/scheme_docs/ first.
"""
import glob
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import get_settings


def build_store() -> None:
    s = get_settings()
    pdfs = glob.glob(os.path.join(s.scheme_docs_dir, "*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {s.scheme_docs_dir}. Add scheme guideline PDFs and re-run.")
        return

    docs = []
    for path in pdfs:
        print(f"Loading {path} ...")
        docs.extend(PyPDFLoader(path).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Embedding...")

    embeddings = OpenAIEmbeddings(model=s.embedding_model, api_key=s.openai_api_key)
    Chroma.from_documents(chunks, embeddings, persist_directory=s.chroma_dir)
    print(f"Vector store written to {s.chroma_dir}")


if __name__ == "__main__":
    build_store()
