"""Document Agent tool.

Generates the required-document checklist for a scheme application and a
pre-filled application draft (as structured text) the user can print/submit.
Writes the draft to /tmp so it can be served/downloaded by the frontend.
"""
import json
import os
import tempfile
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Base documents most Indian health-scheme applications need. Scheme-specific
# extras are appended by the agent from the retrieved guidelines.
_BASE_DOCS = [
    "Aadhaar card (applicant and beneficiary)",
    "Ration card (BPL/White card if applicable)",
    "Income / caste certificate as required by the scheme",
    "Recent passport-size photographs",
    "Hospital admission slip or doctor's referral",
    "Original hospital bill / cost estimate",
]


class DocGenInput(BaseModel):
    scheme_name: str = Field(..., description="Scheme the user is applying to")
    applicant_name: str = Field("", description="Applicant name if known")
    extra_docs: str = Field("", description="Comma-separated scheme-specific documents")


class DocumentGeneratorTool(BaseTool):
    name: str = "document_generator"
    description: str = (
        "Produce the required-document checklist and a pre-filled application draft "
        "for a given health scheme. Returns JSON with 'checklist' and 'draft_path'."
    )
    args_schema: Type[BaseModel] = DocGenInput

    def _run(self, scheme_name: str, applicant_name: str = "", extra_docs: str = "") -> str:
        checklist = list(_BASE_DOCS)
        if extra_docs:
            checklist.extend(d.strip() for d in extra_docs.split(",") if d.strip())

        draft = (
            f"APPLICATION DRAFT — {scheme_name}\n"
            f"Applicant: {applicant_name or '<fill name>'}\n\n"
            "I am applying for cashless / subsidised treatment under the above "
            "scheme. My documents are attached as per the checklist. Please process "
            "my eligibility for the treatment noted in the enclosed hospital estimate.\n\n"
            "Signature: ____________    Date: ____________\n"
        )
        fd, path = tempfile.mkstemp(prefix="application_", suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(draft)

        return json.dumps({"checklist": checklist, "draft_path": path}, ensure_ascii=False)
