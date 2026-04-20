from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_PATH = DB_DIR / "campaigns.db"


@contextmanager
def get_connection() -> sqlite3.Connection:
    """Yield a SQLite connection configured for safer concurrent access."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """Initialize required tables on first run."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                date TEXT,
                status TEXT NOT NULL,
                file_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def create_campaign(goal: str, status: str = "running") -> int:
    """Create a campaign execution record and return its id."""
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO campaigns (goal, date, status, file_path, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (goal, None, status, None, now),
        )
        return int(cursor.lastrowid)


def update_campaign_status(
    campaign_id: int,
    status: str,
    file_path: str | None = None,
    date: str | None = None,
) -> None:
    """Update status (and optional metadata) for an existing campaign."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE campaigns
            SET status = ?,
                file_path = COALESCE(?, file_path),
                date = COALESCE(?, date)
            WHERE id = ?
            """,
            (status, file_path, date, campaign_id),
        )


def get_all_campaigns() -> list[dict[str, Any]]:
    """Return all campaign rows ordered by most recent first."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, goal, date, status, file_path, created_at
            FROM campaigns
            ORDER BY datetime(created_at) DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_campaign_by_id(campaign_id: int) -> dict[str, Any] | None:
    """Return a single campaign dict by id, if it exists."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, goal, date, status, file_path, created_at
            FROM campaigns
            WHERE id = ?
            """,
            (campaign_id,),
        ).fetchone()
    return dict(row) if row else None


# Initialize DB when module is imported.
init_database()
