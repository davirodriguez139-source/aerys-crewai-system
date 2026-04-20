from crewai import Crew, Process

from src.agents import create_agents
from src.context_loader import load_obsidian_context
from src.tasks import create_tasks


class AerysCrewSystem:
    """Factory/orchestrator for the AERYS multi-agent CrewAI workflow."""

    def __init__(self, campaign_goal: str):
        self.campaign_goal = campaign_goal

        # Force refresh once per crew instantiation to ensure latest Obsidian notes are used.
        self.context_data = load_obsidian_context(force_refresh=True)
        self._log_context_summary()

        agents = create_agents(force_refresh_context=False)
        self.director_agent = agents["director"]
        self.research_agent = agents["research"]
        self.copy_agent = agents["copy"]
        self.ads_agent = agents["ads"]

        tasks = create_tasks(
            campaign_goal=self.campaign_goal,
            research_agent=self.research_agent,
            copy_agent=self.copy_agent,
            ads_agent=self.ads_agent,
            director_agent=self.director_agent,
            force_refresh_context=False,
        )
        self.research_task = tasks["research"]
        self.copy_task = tasks["copy"]
        self.ads_task = tasks["ads"]
        self.director_review_task = tasks["director_review"]

    def _log_context_summary(self) -> None:
        """Print context diagnostics to verify dynamic memory loading."""
        loaded_files = self.context_data.get("loaded_files", [])
        errors = self.context_data.get("errors", [])
        context_sizes = self.context_data.get("context_sizes", {})
        sample_excerpt = (self.context_data.get("sample_excerpt", "") or "")[:200]

        print("\n[CONTEXT] Obsidian memory loaded successfully.")
        print(f"[CONTEXT] Files loaded: {len(loaded_files)}")
        for file_name in loaded_files:
            print(f"[CONTEXT] - {file_name}")

        print("[CONTEXT] Context sizes (characters):")
        for key, size in context_sizes.items():
            print(f"[CONTEXT] - {key}: {size}")

        if sample_excerpt:
            print(f"[CONTEXT] Sample excerpt: {sample_excerpt}...")

        if errors:
            print(f"[CONTEXT] Warnings/Errors: {len(errors)}")
            for error in errors:
                print(f"[CONTEXT] ! {error}")

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
