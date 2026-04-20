import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

UPLOADS_PATH = Path("/home/ubuntu/Uploads")

_AGENT_FILENAMES = {
    "AGENTE - DIRETOR.md": "director_context",
    "AGENTE - PESQUISA.md": "research_context",
    "AGENTE - COPY.md": "copy_context",
    "AGENTE - ADS.md": "ads_context",
}

_cache: dict[str, Any] | None = None


def _safe_read_text(file_path: Path) -> tuple[str | None, str | None]:
    """Read file text safely. Returns (content, error_message)."""
    try:
        return file_path.read_text(encoding="utf-8"), None
    except Exception as exc:  # pragma: no cover - defensive guard
        return None, f"{file_path.name}: {exc}"


def _combine_sections(sections: list[tuple[str, str]]) -> str:
    if not sections:
        return ""

    combined_parts: list[str] = []
    for name, content in sections:
        combined_parts.append(f"# {name}\n\n{content.strip()}")

    return "\n\n---\n\n".join(combined_parts).strip()


def _categorize_file(file_name: str) -> str:
    upper_name = file_name.upper()

    if upper_name.startswith("AGENTE -"):
        return "agent"
    if "ESTRATÉGIA" in upper_name or upper_name.startswith("MAPA"):
        return "strategy"
    if (
        upper_name.startswith("CORE")
        or upper_name.startswith("MANUAL")
        or "SOP" in upper_name
    ):
        return "core"

    return "general"


def load_obsidian_context(force_refresh: bool = False) -> dict[str, Any]:
    """Load AERYS memory from Obsidian markdown files in /home/ubuntu/Uploads.

    Caching behavior:
    - Default returns cached data if available.
    - Use force_refresh=True to reload from disk (recommended once per crew run).
    """
    global _cache

    if _cache is not None and not force_refresh:
        LOGGER.info(
            "[ContextLoader] Using cached Obsidian context (files=%s).",
            _cache.get("file_count", 0),
        )
        return _cache

    agent_context_map = {
        "director_context": "",
        "research_context": "",
        "copy_context": "",
        "ads_context": "",
    }

    strategy_sections: list[tuple[str, str]] = []
    core_sections: list[tuple[str, str]] = []
    general_sections: list[tuple[str, str]] = []
    all_sections: list[tuple[str, str]] = []

    loaded_files: list[str] = []
    errors: list[str] = []

    if not UPLOADS_PATH.exists():
        error_message = f"Uploads directory not found: {UPLOADS_PATH}"
        LOGGER.warning("[ContextLoader] %s", error_message)
        _cache = {
            "director_context": "",
            "research_context": "",
            "copy_context": "",
            "ads_context": "",
            "brand_strategy": "",
            "full_context": "",
            "loaded_files": loaded_files,
            "errors": [error_message],
            "file_count": 0,
            "context_sizes": {},
            "sample_excerpt": "",
        }
        return _cache

    markdown_files = sorted(UPLOADS_PATH.glob("*.md"), key=lambda p: p.name.lower())

    for markdown_file in markdown_files:
        content, read_error = _safe_read_text(markdown_file)

        if read_error:
            LOGGER.error("[ContextLoader] Failed to read %s", read_error)
            errors.append(read_error)
            continue

        assert content is not None

        normalized_content = content.strip()
        if not normalized_content:
            warning = f"{markdown_file.name}: file is empty"
            LOGGER.warning("[ContextLoader] %s", warning)
            errors.append(warning)
            continue

        loaded_files.append(markdown_file.name)
        all_sections.append((markdown_file.name, normalized_content))

        agent_key = _AGENT_FILENAMES.get(markdown_file.name)
        if agent_key:
            agent_context_map[agent_key] = normalized_content
            continue

        category = _categorize_file(markdown_file.name)
        if category == "strategy":
            strategy_sections.append((markdown_file.name, normalized_content))
        elif category == "core":
            core_sections.append((markdown_file.name, normalized_content))
        else:
            general_sections.append((markdown_file.name, normalized_content))

    brand_strategy_sections = strategy_sections + core_sections + general_sections
    brand_strategy = _combine_sections(brand_strategy_sections)
    full_context = _combine_sections(all_sections)

    context_data: dict[str, Any] = {
        **agent_context_map,
        "brand_strategy": brand_strategy,
        "full_context": full_context,
        "loaded_files": loaded_files,
        "errors": errors,
        "file_count": len(loaded_files),
        "context_sizes": {
            "director_context": len(agent_context_map["director_context"]),
            "research_context": len(agent_context_map["research_context"]),
            "copy_context": len(agent_context_map["copy_context"]),
            "ads_context": len(agent_context_map["ads_context"]),
            "brand_strategy": len(brand_strategy),
            "full_context": len(full_context),
        },
        "sample_excerpt": full_context[:300],
    }

    LOGGER.info(
        "[ContextLoader] Obsidian context loaded: files=%s | sizes=%s",
        context_data["file_count"],
        context_data["context_sizes"],
    )
    if errors:
        LOGGER.warning("[ContextLoader] Load completed with %s warning/error entries.", len(errors))

    _cache = context_data
    return context_data
