"""Tasks executed sequentially; each task's output feeds the next agent's context."""
from crewai import Task


def build_tasks(agents: dict, profile: dict, bill_path: str | None) -> list:
    profile_str = ", ".join(f"{k}={v}" for k, v in profile.items())
    bill_line = f"An uploaded bill PDF is at: {bill_path}" if bill_path else "No bill uploaded."

    profile_task = Task(
        description=(
            f"Build a clean eligibility profile from this input: {profile_str}. "
            "List state, annual income, family size, ration card status and ailment. "
            "Do not assume missing values — mark them as unknown."
        ),
        expected_output="A concise structured eligibility profile.",
        agent=agents["eligibility_profiler"],
    )

    scheme_task = Task(
        description=(
            "Using the scheme_matcher tool with the user's state, income and ration "
            "card, list every scheme they qualify for. For each: name, authority, "
            "coverage amount, and one line on why they are eligible."
        ),
        expected_output="A list of eligible schemes with coverage and eligibility reasons.",
        agent=agents["scheme_matcher"],
        context=[profile_task],
    )

    coverage_task = Task(
        description=(
            f"{bill_line} If a bill exists, parse it with bill_parser. Then, for the "
            "top matched scheme and the user's ailment, use coverage_retriever to pull "
            "the exact clauses on coverage, caps and exclusions. Summarise what will be "
            "paid, what won't, and cite the clause for each claim."
        ),
        expected_output="A coverage summary grounded in retrieved scheme clauses.",
        agent=agents["coverage_analyst"],
        context=[profile_task, scheme_task],
    )

    hospital_task = Task(
        description=(
            "Use hospital_finder to list nearby hospitals where the top matched scheme's "
            "cashless treatment likely applies, based on the user's state/location and ailment."
        ),
        expected_output="A short list of nearby hospitals with a verify-empanelment note.",
        agent=agents["hospital_finder"],
        context=[profile_task, scheme_task],
    )

    document_task = Task(
        description=(
            "Use document_generator for the top matched scheme to produce the document "
            "checklist and a pre-filled application draft. Add any scheme-specific "
            "documents you found in the coverage clauses."
        ),
        expected_output="A document checklist and the path to the generated application draft.",
        agent=agents["document_agent"],
        context=[scheme_task, coverage_task],
    )

    voice_task = Task(
        description=(
            "Write a short, warm, plain-language summary for the user: which scheme to "
            "use, roughly how much it covers, which hospital to go to, and which papers "
            "to carry. Then use the translator tool to render it in the user's language "
            "(language code in the profile). End with a gentle reminder to confirm "
            "details at the hospital / official portal."
        ),
        expected_output="Final guidance in the user's language, ready to be read aloud.",
        agent=agents["voice_guide"],
        context=[scheme_task, coverage_task, hospital_task, document_task],
    )

    return [profile_task, scheme_task, coverage_task, hospital_task, document_task, voice_task]
