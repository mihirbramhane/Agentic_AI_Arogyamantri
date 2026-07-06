"""Scheme Matcher tool.

Queries a real scheme database (Supabase table `schemes`) filtered by state and
income, so eligibility is data-driven, not hallucinated. Falls back to the local
seed file data/schemes.json when Supabase is not configured (useful for local dev).
"""
import json
import os
from typing import Type, List, Dict, Any

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from app.config import get_settings

_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")


def _load_seed() -> List[Dict[str, Any]]:
    with open(os.path.abspath(_SEED_PATH), "r", encoding="utf-8") as f:
        return json.load(f)


def _query_supabase(state: str, income: int) -> List[Dict[str, Any]]:
    from supabase import create_client  # imported lazily so local dev works without it

    s = get_settings()
    client = create_client(s.supabase_url, s.supabase_service_key)
    # National schemes (state == "ALL") OR matching state, and income under the cap.
    resp = (
        client.table("schemes")
        .select("*")
        .lte("income_ceiling", 10_000_000)  # broad pull; fine-grained filter below
        .execute()
    )
    rows = resp.data or []
    return [r for r in rows if r.get("state") in ("ALL", state)]


class SchemeSearchInput(BaseModel):
    state: str = Field(..., description="User's state, e.g. 'Telangana'")
    annual_income: int = Field(..., description="Family annual income in INR")
    ration_card_type: str = Field("", description="e.g. 'White / BPL' or '' if none")


class SchemeMatchTool(BaseTool):
    name: str = "scheme_matcher"
    description: str = (
        "Find government health schemes and subsidies the user is eligible for, "
        "given their state, annual income and ration card. Returns a JSON list of "
        "schemes with authority, coverage amount and income ceiling."
    )
    args_schema: Type[BaseModel] = SchemeSearchInput

    def _run(self, state: str, annual_income: int, ration_card_type: str = "") -> str:
        s = get_settings()
        try:
            if s.supabase_url and s.supabase_service_key:
                rows = _query_supabase(state, annual_income)
            else:
                rows = [r for r in _load_seed() if r.get("state") in ("ALL", state)]
        except Exception as exc:  # never crash the crew on a data source hiccup
            rows = [r for r in _load_seed() if r.get("state") in ("ALL", state)]
            rows.append({"_note": f"Supabase unavailable, used seed data ({exc})."})

        eligible = []
        for r in rows:
            ceiling = r.get("income_ceiling")
            if ceiling is None or annual_income <= ceiling:
                eligible.append(r)
        return json.dumps(eligible, ensure_ascii=False)
