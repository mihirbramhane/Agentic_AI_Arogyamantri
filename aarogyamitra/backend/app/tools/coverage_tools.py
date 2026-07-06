"""Coverage Analyzer tools (this is where RAG lives).

- BillParserTool: extracts text from an uploaded hospital bill/estimate PDF.
- CoverageRetrievalTool: retrieves the exact clauses from indexed scheme guideline
  PDFs that decide what is / isn't covered, using a Chroma vector store.

The vector store is built by app/rag/ingest.py from data/scheme_docs/*.pdf.
"""
import os
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from app.config import get_settings


# ----------------------------- Bill parsing -----------------------------------
class BillParseInput(BaseModel):
    pdf_path: str = Field(..., description="Local path to the uploaded bill/estimate PDF")


class BillParserTool(BaseTool):
    name: str = "bill_parser"
    description: str = (
        "Extract line items and totals as plain text from a hospital bill or "
        "cost-estimate PDF, so it can be checked against scheme coverage."
    )
    args_schema: Type[BaseModel] = BillParseInput

    def _run(self, pdf_path: str) -> str:
        from pypdf import PdfReader

        if not os.path.exists(pdf_path):
            return f"ERROR: file not found at {pdf_path}"
        reader = PdfReader(pdf_path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text.strip() or "No extractable text (bill may be a scanned image; OCR needed)."


# ------------------------- RAG over scheme docs -------------------------------
class CoverageQueryInput(BaseModel):
    query: str = Field(
        ...,
        description="What to look up, e.g. 'room rent cap and cardiac surgery coverage under Aarogyasri'",
    )
    scheme_name: str = Field("", description="Optional scheme name to focus the search")


class CoverageRetrievalTool(BaseTool):
    name: str = "coverage_retriever"
    description: str = (
        "Retrieve the exact clauses from official scheme guideline documents that "
        "determine coverage, caps and exclusions for a given procedure. Use this to "
        "back every coverage claim with a real citation from the scheme rules."
    )
    args_schema: Type[BaseModel] = CoverageQueryInput

    def _run(self, query: str, scheme_name: str = "") -> str:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings

        s = get_settings()
        if not os.path.isdir(s.chroma_dir):
            return (
                "Vector store not built yet. Run `python -m app.rag.ingest` after "
                "placing scheme PDFs in data/scheme_docs/."
            )
        embeddings = OpenAIEmbeddings(model=s.embedding_model, api_key=s.openai_api_key)
        store = Chroma(persist_directory=s.chroma_dir, embedding_function=embeddings)
        full_query = f"{scheme_name}: {query}" if scheme_name else query
        docs = store.similarity_search(full_query, k=4)
        if not docs:
            return "No matching clauses found in indexed scheme documents."
        out = []
        for d in docs:
            src = d.metadata.get("source", "scheme_doc")
            out.append(f"[{os.path.basename(src)}] {d.page_content.strip()}")
        return "\n\n".join(out)
