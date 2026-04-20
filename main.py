import re
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from src.crew import AerysCrewSystem


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"


def slugify(text: str, max_length: int = 60) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", cleaned)
    slug = slug.strip("-")
    return (slug[:max_length] or "campaign").strip("-")


def save_output(campaign_goal: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{date.today().isoformat()}_{slugify(campaign_goal)}.md"
    output_path = OUTPUT_DIR / filename

    final_doc = f"# AERYS Campaign Output\n\n"
    final_doc += f"- **Campaign Goal:** {campaign_goal}\n"
    final_doc += f"- **Generated On:** {date.today().isoformat()}\n\n"
    final_doc += "---\n\n"
    final_doc += str(content)

    output_path.write_text(final_doc, encoding="utf-8")
    return output_path


def validate_env() -> None:
    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is missing. Copy .env.example to .env and set your key."
        )


def main() -> int:
    print("=" * 72)
    print("AERYS CrewAI System - US Sleep Strips Campaign Engine")
    print("=" * 72)

    load_dotenv(PROJECT_ROOT / ".env")

    try:
        validate_env()
    except Exception as exc:
        print(f"[ERROR] Environment setup issue: {exc}")
        return 1

    campaign_goal = input(
        "\nEnter your campaign goal (example: 'Create ad for jawline angle'):\n> "
    ).strip()

    if not campaign_goal:
        print("[ERROR] Campaign goal cannot be empty.")
        return 1

    try:
        print("\n[1/4] Initializing AERYS agents...")
        system = AerysCrewSystem(campaign_goal=campaign_goal)

        print("[2/4] Running sequential workflow: Research -> Copy -> Ads -> Director Review...")
        result = system.run()

        print("[3/4] Saving final output...")
        output_path = save_output(campaign_goal=campaign_goal, content=str(result))

        print("[4/4] Completed successfully.")
        print(f"\n✅ Final output saved to: {output_path}")
        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Execution interrupted by user.")
        return 130
    except Exception as exc:
        print(f"\n[ERROR] Workflow failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
