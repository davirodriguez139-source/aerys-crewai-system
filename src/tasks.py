from crewai import Task


AERYS_CONTEXT = """
Brand: AERYS (premium biohacking brand in the USA)
Core product: Sleep Strips (mouth tape for sleep optimization)
Strategic intent: Win through stronger differentiation, sharper hooks, better creatives,
and conversion-focused execution against shopping-feed competitors.
Quality rule: Avoid generic outputs. Every deliverable must be specific and actionable.
Language rule: Final outputs must be written in English for the USA market.
""".strip()


def create_research_task(research_agent, campaign_goal: str) -> Task:
    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Produce a market intelligence brief for the US sleep strips niche. "
            "Cover: (1) customer pain points and desired outcomes, "
            "(2) top competitor patterns and weaknesses, "
            "(3) trend opportunities and positioning angles for AERYS, "
            "(4) practical messaging opportunities for direct-response marketing.\n\n"
            f"Use this context:\n{AERYS_CONTEXT}"
        ),
        expected_output=(
            "A structured markdown report with sections: Audience Pain Map, Competitor Analysis, "
            "Market Opportunities, and Actionable Messaging Insights. Must be specific, concise, "
            "and executable by copy/ads teams."
        ),
        agent=research_agent,
    )


def create_copy_task(copy_agent, campaign_goal: str, research_task: Task) -> Task:
    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Using the research brief, produce conversion-first copy assets for AERYS Sleep Strips. "
            "Include: (1) 10 high-impact headlines, (2) 5 value propositions, "
            "(3) 3 offer concepts with value stack, (4) product page hero section draft, "
            "(5) a short objection-handling block."
        ),
        expected_output=(
            "A markdown copy package ready for campaign execution, with clear subsections and "
            "US-market tone. Copy must align with premium biohacking positioning and conversion intent."
        ),
        context=[research_task],
        agent=copy_agent,
    )


def create_ads_task(ads_agent, campaign_goal: str, copy_task: Task) -> Task:
    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Convert the copy package into platform-ready ad scripts. "
            "Deliver: (1) 3 short-form video scripts with 0-3 second hooks, "
            "(2) 3 static ad concepts (visual + headline + CTA), "
            "(3) 3 UGC-style angles for testing, "
            "(4) suggested CTA variations."
        ),
        expected_output=(
            "A markdown ad production sheet with clear script formatting, testable hook variations, "
            "and direct-response CTAs suitable for paid social and short-form video channels."
        ),
        context=[copy_task],
        agent=ads_agent,
    )


def create_director_review_task(director_agent, campaign_goal: str, ads_task: Task) -> Task:
    return Task(
        description=(
            f"Campaign goal: {campaign_goal}\n\n"
            "Review all generated assets and provide final approval package. "
            "Validate strategic alignment, differentiation quality, conversion strength, and execution readiness. "
            "If something is weak, explicitly flag it and provide improved replacements."
        ),
        expected_output=(
            "Final director-approved markdown output containing: Approval Summary, "
            "Final Recommended Assets, Risk Notes, and Launch Priorities."
        ),
        context=[ads_task],
        agent=director_agent,
    )
