"""FastAPI backend for AarogyaMitra.

Endpoints:
  GET  /health          -> liveness check
  POST /analyze         -> run the 6-agent crew (JSON profile + optional bill file)
"""
import json
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.crew import run_aarogyamitra
from app.schemas import AnalyzeResponse

settings = get_settings()

app = FastAPI(title="AarogyaMitra API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    profile: str = Form(..., description="JSON string of UserProfile"),
    bill: Optional[UploadFile] = File(None),
) -> AnalyzeResponse:
    """Run the crew. `profile` is a JSON string; `bill` is an optional PDF upload."""
    profile_dict = json.loads(profile)

    bill_path = None
    if bill is not None:
        suffix = os.path.splitext(bill.filename or "bill.pdf")[1] or ".pdf"
        fd, bill_path = tempfile.mkstemp(prefix="bill_", suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(await bill.read())

    report = run_aarogyamitra(profile_dict, bill_path)

    # The crew returns rich text; the frontend renders `raw_report` and speaks
    # `voice_guidance`. (For production, have the voice_task emit structured JSON
    # and parse it here into the typed fields.)
    return AnalyzeResponse(
        voice_guidance=report,
        raw_report=report,
    )
