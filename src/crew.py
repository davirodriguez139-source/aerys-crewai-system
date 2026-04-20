from crewai import Crew, Process

from src.agents import (
    create_ads_agent,
    create_copy_agent,
    create_director_agent,
    create_research_agent,
)
from src.tasks import (
    create_ads_task,
    create_copy_task,
    create_director_review_task,
    create_research_task,
)


class AerysCrewSystem:
    """Factory/orchestrator for the AERYS multi-agent CrewAI workflow."""

    def __init__(self, campaign_goal: str):
        self.campaign_goal = campaign_goal

        self.director_agent = create_director_agent()
        self.research_agent = create_research_agent()
        self.copy_agent = create_copy_agent()
        self.ads_agent = create_ads_agent()

        self.research_task = create_research_task(
            research_agent=self.research_agent,
            campaign_goal=self.campaign_goal,
        )
        self.copy_task = create_copy_task(
            copy_agent=self.copy_agent,
            campaign_goal=self.campaign_goal,
            research_task=self.research_task,
        )
        self.ads_task = create_ads_task(
            ads_agent=self.ads_agent,
            campaign_goal=self.campaign_goal,
            copy_task=self.copy_task,
        )
        self.director_review_task = create_director_review_task(
            director_agent=self.director_agent,
            campaign_goal=self.campaign_goal,
            ads_task=self.ads_task,
        )

    def build_crew(self) -> Crew:
        """Create CrewAI sequential process for AERYS campaign generation."""
        return Crew(
            agents=[
                self.director_agent,
                self.research_agent,
                self.copy_agent,
                self.ads_agent,
            ],
            tasks=[
                self.research_task,
                self.copy_task,
                self.ads_task,
                self.director_review_task,
            ],
            process=Process.sequential,
            verbose=True,
        )

    def run(self):
        crew = self.build_crew()
        return crew.kickoff()
