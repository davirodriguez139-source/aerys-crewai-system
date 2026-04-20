from typing import Any

from crewai import Task

from src.context_loader import load_obsidian_context


def _compose_task_context_block(full_context: str, brand_strategy: str) -> str:
    full_context = (full_context or "").strip()
    brand_strategy = (brand_strategy or "").strip()

    sections: list[str] = []

    if brand_strategy:
        sections.append(
            "Brand strategy and operations memory (Obsidian):\n"
            f"{brand_strategy}"
        )

    if full_context:
        sections.append(
            "Complete knowledge memory available for reference (Obsidian):\n"
            f"{full_context}"
        )

    if not sections:
        return "No Obsidian context was loaded. Work with caution and be explicit about assumptions."

    return "\n\n---\n\n".join(sections)


def create_research_task(
    research_agent,
    campaign_goal: str,
    context_data: dict[str, Any] | None = None,
) -> Task:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_task_context_block(
        full_context=context_data.get("full_context", ""),
        brand_strategy=context_data.get("brand_strategy", ""),
    )

    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Produce a market intelligence brief for the target niche. "
            "Cover: (1) customer pain points and desired outcomes, "
            "(2) top competitor patterns and weaknesses, "
            "(3) trend opportunities and positioning angles for AERYS, "
            "(4) practical messaging opportunities for direct-response marketing.\n\n"
            "Use the following dynamic brand memory and operational strategy:\n"
            f"{context_block}"
        ),
        expected_output=(
            "A structured markdown report with sections: Audience Pain Map, Competitor Analysis, "
            "Market Opportunities, and Actionable Messaging Insights. Must be specific, concise, "
            "and executable by copy/ads teams."
        ),
        agent=research_agent,
    )


def create_copy_task(
    copy_agent,
    campaign_goal: str,
    research_task: Task,
    context_data: dict[str, Any] | None = None,
) -> Task:
    context_data = context_data or load_obsidian_context()
    brand_strategy = (context_data.get("brand_strategy", "") or "").strip()

    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Using the research brief, produce conversion-first copy assets for AERYS. "
            "Include: (1) 10 high-impact headlines, (2) 5 value propositions, "
            "(3) 3 offer concepts with value stack, (4) product page hero section draft, "
            "(5) a short objection-handling block.\n\n"
            "Maintain strict alignment with this loaded brand strategy:\n"
            f"{brand_strategy}"
        ),
        expected_output=(
            "A markdown copy package ready for campaign execution, with clear subsections and "
            "market-appropriate tone. Copy must align with premium positioning and conversion intent."
        ),
        context=[research_task],
        agent=copy_agent,
    )


def create_ads_task(
    ads_agent,
    campaign_goal: str,
    copy_task: Task,
    context_data: dict[str, Any] | None = None,
) -> Task:
    context_data = context_data or load_obsidian_context()
    brand_strategy = (context_data.get("brand_strategy", "") or "").strip()

    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Convert the copy package into platform-ready ad scripts. "
            "Deliver: (1) 3 short-form video scripts with 0-3 second hooks, "
            "(2) 3 static ad concepts (visual + headline + CTA), "
            "(3) 3 UGC-style angles for testing, "
            "(4) suggested CTA variations.\n\n"
            "Respect the loaded strategy and operational standards:\n"
            f"{brand_strategy}"
        ),
        expected_output=(
            "A markdown ad production sheet with clear script formatting, testable hook variations, "
            "and direct-response CTAs suitable for paid social and short-form video channels."
        ),
        context=[copy_task],
        agent=ads_agent,
    )


def create_director_review_task(
    director_agent,
    campaign_goal: str,
    ads_task: Task,
    context_data: dict[str, Any] | None = None,
) -> Task:
    context_data = context_data or load_obsidian_context()
    context_block = _compose_task_context_block(
        full_context=context_data.get("full_context", ""),
        brand_strategy=context_data.get("brand_strategy", ""),
    )

    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Review all generated assets and provide a final approval package. "
            "Validate strategic alignment, differentiation quality, conversion strength, and execution readiness. "
            "If something is weak, explicitly flag it and provide improved replacements.\n\n"
            "Review against complete loaded memory and strategy:\n"
            f"{context_block}"
        ),
        expected_output=(
            "Final director-approved markdown output containing: Approval Summary, "
            "Final Recommended Assets, Risk Notes, and Launch Priorities."
        ),
        context=[ads_task],
        agent=director_agent,
    )


def create_tasks(
    campaign_goal: str,
    research_agent,
    copy_agent,
    ads_agent,
    director_agent,
    force_refresh_context: bool = False,
) -> dict[str, Task]:
    """Create all tasks using dynamic Obsidian context."""
    context_data = load_obsidian_context(force_refresh=force_refresh_context)

    research_task = create_research_task(
        research_agent=research_agent,
        campaign_goal=campaign_goal,
        context_data=context_data,
    )
    copy_task = create_copy_task(
        copy_agent=copy_agent,
        campaign_goal=campaign_goal,
        research_task=research_task,
        context_data=context_data,
    )
    ads_task = create_ads_task(
        ads_agent=ads_agent,
        campaign_goal=campaign_goal,
        copy_task=copy_task,
        context_data=context_data,
    )
    director_review_task = create_director_review_task(
        director_agent=director_agent,
        campaign_goal=campaign_goal,
        ads_task=ads_task,
        context_data=context_data,
    )

    return {
        "research": research_task,
        "copy": copy_task,
        "ads": ads_task,
        "director_review": director_review_task,
    }
