import os
from typing import Any, Dict, List

from crewai import Agent

from src.context_loader import load_obsidian_context

try:
    from crewai import LLM
except Exception:  # pragma: no cover - compatibility fallback for CrewAI versions without LLM class
    LLM = None

try:
    from crewai_tools import SerperDevTool
except Exception:  # pragma: no cover - optional dependency in some environments
    SerperDevTool = None


CLAUDE_MODEL = os.getenv("ANTHROPIC_MODEL", "anthropic/claude-sonnet-4-6")


def _build_llm():
    """Build a Claude LLM config compatible with multiple CrewAI versions."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if LLM is not None:
        return LLM(model=CLAUDE_MODEL, api_key=anthropic_key, temperature=0.35)

    # Fallback for older CrewAI versions that accept model string directly.
    return CLAUDE_MODEL


def _optional_research_tools() -> List:
    """Prepare tools for future web research. Activated when SERPER_API_KEY is available."""
    if not os.getenv("SERPER_API_KEY") or SerperDevTool is None:
        return []

    return [SerperDevTool()]


def _compose_context_block(agent_context: str, brand_strategy: str) -> str:
    agent_context = (agent_context or "").strip()
    brand_strategy = (brand_strategy or "").strip()

    sections: list[str] = []

    if agent_context:
        sections.append(
            "Agent-specific operational memory loaded from Obsidian:\n"
            f"{agent_context}"
        )

    if brand_strategy:
        sections.append(
            "Shared brand strategy and operating memory loaded from Obsidian:\n"
            f"{brand_strategy}"
        )

    if not sections:
        return (
            "No Obsidian context was found. Operate cautiously and request clarification "
            "whenever strategic details are missing."
        )

    return "\n\n---\n\n".join(sections)


def create_director_agent(context_data: Dict[str, Any] | None = None) -> Agent:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_context_block(
        context_data.get("director_context", ""),
        context_data.get("brand_strategy", ""),
    )

    return Agent(
        role="AERYS Growth Director",
        goal=(
            "Coordinate the full workflow, enforce quality standards, and approve only outputs "
            "that are consistent with the loaded AERYS memory and campaign objective."
        ),
        backstory=context_block,
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_research_agent(context_data: Dict[str, Any] | None = None) -> Agent:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_context_block(
        context_data.get("research_context", ""),
        context_data.get("brand_strategy", ""),
    )

    return Agent(
        role="AERYS Market Intelligence Researcher",
        goal=(
            "Generate specific, evidence-driven insights aligned with the loaded brand memory, "
            "highlighting market opportunities, competitor gaps, and actionable positioning angles."
        ),
        backstory=context_block,
        llm=_build_llm(),
        tools=_optional_research_tools(),
        verbose=True,
        allow_delegation=False,
    )


def create_copy_agent(context_data: Dict[str, Any] | None = None) -> Agent:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_context_block(
        context_data.get("copy_context", ""),
        context_data.get("brand_strategy", ""),
    )

    return Agent(
        role="AERYS Direct-Response Copywriter",
        goal=(
            "Transform validated insights into conversion-focused messaging that follows the loaded "
            "AERYS voice, strategic principles, and execution standards."
        ),
        backstory=context_block,
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_ads_agent(context_data: Dict[str, Any] | None = None) -> Agent:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_context_block(
        context_data.get("ads_context", ""),
        context_data.get("brand_strategy", ""),
    )

    return Agent(
        role="AERYS Performance Ads Creative Strategist",
        goal=(
            "Convert strategy and copy into platform-ready ad assets with strong hooks, clear "
            "structure, and conversion intent aligned to the loaded brand memory."
        ),
        backstory=context_block,
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_agents(force_refresh_context: bool = False) -> dict[str, Agent]:
    """Create all agents using the latest Obsidian context.

    Set force_refresh_context=True once per crew run to guarantee fresh context from disk.
    """
    context_data = load_obsidian_context(force_refresh=force_refresh_context)

    return {
        "director": create_director_agent(context_data=context_data),
        "research": create_research_agent(context_data=context_data),
        "copy": create_copy_agent(context_data=context_data),
        "ads": create_ads_agent(context_data=context_data),
    }
