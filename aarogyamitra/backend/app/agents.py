"""The six AarogyaMitra agents. Each has a distinct role and its own real tools."""
from crewai import Agent, LLM

from app.config import get_settings
from app.tools import (
    SchemeMatchTool,
    BillParserTool,
    CoverageRetrievalTool,
    HospitalFinderTool,
    DocumentGeneratorTool,
    TranslateTool,
)


def _llm() -> LLM:
    s = get_settings()
    return LLM(model=s.llm_model, api_key=s.openai_api_key, temperature=0.2)


def build_agents() -> dict:
    llm = _llm()

    eligibility_profiler = Agent(
        role="Eligibility Profiler",
        goal="Organise the user's income, state, family and card details into a clean eligibility profile.",
        backstory=(
            "A patient social worker who knows that the poorest families often don't "
            "know what to share. You never invent facts you weren't given."
        ),
        llm=llm,
        verbose=True,
    )

    scheme_matcher = Agent(
        role="Scheme Matcher",
        goal="Find every government scheme and subsidy the user actually qualifies for.",
        backstory="You know Indian public-health schemes and match people to their rightful benefits.",
        tools=[SchemeMatchTool()],
        llm=llm,
        verbose=True,
    )

    coverage_analyst = Agent(
        role="Coverage Analyst",
        goal="Decide, clause by clause, what the scheme will and won't pay on this bill.",
        backstory=(
            "A meticulous claims analyst. You never claim something is covered without "
            "retrieving the exact clause from the official scheme document."
        ),
        tools=[BillParserTool(), CoverageRetrievalTool()],
        llm=llm,
        verbose=True,
    )

    hospital_finder = Agent(
        role="Hospital Finder",
        goal="Point the user to nearby hospitals where the scheme's cashless treatment applies.",
        backstory="You help families reach a hospital that will honour their scheme without upfront payment.",
        tools=[HospitalFinderTool()],
        llm=llm,
        verbose=True,
    )

    document_agent = Agent(
        role="Document Agent",
        goal="Generate the exact document checklist and a ready-to-submit application draft.",
        backstory="You remove paperwork fear by preparing everything the applicant needs.",
        tools=[DocumentGeneratorTool()],
        llm=llm,
        verbose=True,
    )

    voice_guide = Agent(
        role="Multilingual Voice Guide",
        goal="Explain the whole plan in the user's own language, simply and warmly.",
        backstory="You make sure a person with no medical or legal knowledge understands their next steps.",
        tools=[TranslateTool()],
        llm=llm,
        verbose=True,
    )

    return {
        "eligibility_profiler": eligibility_profiler,
        "scheme_matcher": scheme_matcher,
        "coverage_analyst": coverage_analyst,
        "hospital_finder": hospital_finder,
        "document_agent": document_agent,
        "voice_guide": voice_guide,
    }
