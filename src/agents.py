import os
from typing import List

from crewai import Agent

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


def create_director_agent() -> Agent:
    return Agent(
        role="AERYS Growth Director",
        goal=(
            "Orchestrate the full marketing workflow and approve only outputs that can "
            "drive profitable growth, conversion, and brand strength in the USA sleep "
            "performance niche."
        ),
        backstory=(
            "You are the strategic brain of AERYS, a premium US biohacking brand selling "
            "Sleep Strips (mouth tape). You coordinate Research, Copy, and Ads specialists, "
            "enforce execution standards from the AERYS operating protocol, and reject generic "
            "deliverables. You prioritize clear market positioning, realistic performance, and profit."
        ),
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_research_agent() -> Agent:
    return Agent(
        role="AERYS Market Intelligence Researcher",
        goal=(
            "Uncover sharp, non-generic market insights about the US sleep strip category, "
            "including trends, competitor gaps, customer pains, and positioning opportunities."
        ),
        backstory=(
            "You are AERYS' competitive intelligence unit. You map competitor messaging, discover "
            "high-value audience pains (e.g., mouth breathing, poor sleep quality, low daytime energy), "
            "and identify profitable hooks for a premium biohacking audience. Your work is evidence-driven "
            "and practical for direct-response execution."
        ),
        llm=_build_llm(),
        tools=_optional_research_tools(),
        verbose=True,
        allow_delegation=False,
    )


def create_copy_agent() -> Agent:
    return Agent(
        role="AERYS Direct-Response Copywriter",
        goal=(
            "Transform validated research into high-converting messaging for US customers: "
            "headlines, offers, value stack, and product page-ready copy."
        ),
        backstory=(
            "You write persuasive conversion-first copy for AERYS. You combine direct-response "
            "frameworks, premium branding, social proof, and psychological triggers without sounding "
            "hyped or generic. You craft copy that moves a problem-aware audience toward immediate action."
        ),
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_ads_agent() -> Agent:
    return Agent(
        role="AERYS Performance Ads Creative Strategist",
        goal=(
            "Convert copy into platform-ready ad scripts with powerful 0-3 second hooks, "
            "clear structure, and strong conversion intent for US paid traffic."
        ),
        backstory=(
            "You build scroll-stopping ad creatives for AERYS. Your scripts are optimized for "
            "attention in the first 3 seconds, emotional resonance, and measurable response. "
            "You produce practical ad assets that can be recorded and launched quickly."
        ),
        llm=_build_llm(),
        verbose=True,
        allow_delegation=False,
    )
