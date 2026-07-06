"""Assemble the crew and run it."""
from crewai import Crew, Process

from app.agents import build_agents
from app.tasks import build_tasks


def run_aarogyamitra(profile: dict, bill_path: str | None = None) -> str:
    """Run the full 6-agent pipeline and return the final guidance text."""
    agents = build_agents()
    tasks = build_tasks(agents, profile, bill_path)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    return str(result)
