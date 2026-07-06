# AarogyaMitra 🏥

**AI agents that help low-income Indians access the free/subsidised hospital
treatment they're legally entitled to** under schemes like Ayushman Bharat
(PM-JAY) and state programs (e.g. Telangana's Aarogyasri).

Many eligible patients avoid treatment or fall into debt simply because they
don't know they qualify or can't navigate the process. AarogyaMitra closes that
gap: upload a bill/estimate, answer a few questions, and a team of agents finds
your schemes, checks coverage clause-by-clause, points you to a cashless
hospital, prepares your paperwork, and explains everything in your language by
voice.

## The 6 agents (each calls a real tool)

| Agent | Job | Real tool |
|---|---|---|
| Eligibility Profiler | Structures the user's details | (intake / reasoning) |
| Scheme Matcher | Finds schemes the user qualifies for | **Supabase DB query** |
| Coverage Analyst | Decides what's covered, clause by clause | **PDF parse + RAG (Chroma)** |
| Hospital Finder | Locates nearby cashless hospitals | **Google Places API** |
| Document Agent | Builds checklist + pre-filled form | **File generation** |
| Voice Guide | Explains it in the user's language | **LLM translate → Web Speech** |

**RAG:** official scheme guideline PDFs + hospital lists + the user's policy are
indexed in a Chroma vector store; agents retrieve exact clauses to justify every
coverage decision.

## Architecture

```
Next.js (Vercel)  ──►  /api/analyze (auth via Supabase)  ──►  FastAPI + CrewAI (Render)
       ▲                                                              │
       └────────────── voice guidance (Web Speech API) ◄──────────────┘
```

## Backend setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
# add official scheme PDFs to data/scheme_docs/ then build the RAG store:
python -m app.rag.ingest
uvicorn app.main:app --reload --port 8000
```

## Frontend wiring (into your existing Next.js app)

1. Copy `frontend/app/api/analyze/route.ts` and `frontend/lib/aarogyamitra.ts`
   into your app.
2. Add `AGENT_BACKEND_URL=http://localhost:8000` to `.env.local`.
3. Call `analyze(profile, billFile)` from a form, then `speak(result.voice_guidance, profile.language)`.

## Deploy

- **Backend:** Render / Railway — start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend:** Vercel (your existing project); set `AGENT_BACKEND_URL` to the Render URL.

## Supabase tables

```sql
create table schemes (
  id bigint generated always as identity primary key,
  name text, state text, authority text,
  coverage_amount text, income_ceiling int, notes text, verify_url text
);
-- seed from backend/data/schemes.json (replace with OFFICIAL figures)
```

## ⚠️ Safety note

`data/schemes.json` is **illustrative seed data**. Replace all eligibility
figures with current official numbers before real use. AarogyaMitra gives
**informational** guidance only — users must confirm eligibility and coverage
with the official portal or hospital.

---

## Project Summary (≤200 words, for submission)

**AarogyaMitra** helps low-income Indians access free/subsidised hospital
treatment they're legally entitled to under schemes like Ayushman Bharat
(PM-JAY) and state programs (e.g. Telangana's Aarogyasri). Many eligible
patients avoid treatment or fall into debt because they're unaware or can't
navigate the process. Users: patients and families, especially rural/low-income.

**Agents (6):** (1) Eligibility Profiler collects income/state/family details;
(2) Scheme Matcher queries a Supabase scheme database to find applicable schemes;
(3) Coverage Analyst parses the hospital bill and, using RAG over scheme
documents, identifies covered items clause-by-clause; (4) Hospital Finder locates
nearby empanelled cashless hospitals via the Google Places API; (5) Document
Agent generates the required-document checklist and pre-fills application forms;
(6) Multilingual Voice Guide explains each step in the user's language via speech.

**RAG:** Knowledge source = official scheme guideline PDFs, hospital lists and
the user's policy, indexed in a Chroma vector store; agents retrieve exact
clauses to decide eligibility and coverage.

**Why multiple agents:** eligibility varies by state/scheme, hospital data is
live, and forms must be generated and tracked — a single prompt can't call these
real tools (DB, maps, file, PDF).
