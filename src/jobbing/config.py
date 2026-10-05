"""Configuration loading for the Jobbing package.

Configures the workspace path, scoring threshold, follow-up cadence, and the
Notion locations. Reads environment variables and the workspace .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_key_from_env(name: str) -> str | None:
    """Check environment variable."""
    return os.environ.get(name) or None


def _load_key_from_dotenv(name: str, env_path: Path) -> str | None:
    """Parse a key from a .env file."""
    if not env_path.is_file():
        return None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{name}="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return None


def default_workspace() -> Path:
    """Return the workspace directory.

    JOBBING_HOME wins. Otherwise use the repository root that holds this
    package (correct for an editable install from a git clone).
    """
    home = os.environ.get("JOBBING_HOME")
    if home:
        return Path(home).expanduser()
    return Path(__file__).resolve().parent.parent.parent


@dataclass
class Config:
    """Runtime configuration, loaded once.

    All paths are resolved relative to project_dir (the workspace).
    """

    project_dir: Path

    # Scoring
    score_threshold: int = 60

    # Follow-up cadence
    followup_threshold_days: int = 5

    # Notion locations, written by `jobbing notion --home/--tracker/--interviews`
    notion_home_url: str = ""
    notion_tracker_url: str = ""
    notion_interviews_url: str = ""

    @classmethod
    def load(cls, project_dir: Path | None = None) -> Config:
        """Load configuration from environment, .env, and defaults."""
        if project_dir is None:
            project_dir = default_workspace()

        env_path = project_dir / ".env"

        def setting(name: str, default: str = "") -> str:
            """Environment variable, then workspace .env, then default."""
            return _load_key_from_env(name) or _load_key_from_dotenv(name, env_path) or default

        return cls(
            project_dir=project_dir,
            score_threshold=int(setting("SCORE_THRESHOLD", "60")),
            followup_threshold_days=int(setting("FOLLOWUP_THRESHOLD_DAYS", "5")),
            notion_home_url=setting("NOTION_HOME_URL"),
            notion_tracker_url=setting("NOTION_TRACKER_URL"),
            notion_interviews_url=setting("NOTION_INTERVIEWS_URL"),
        )

    # --- Derived paths ---

    @property
    def applications_dir(self) -> Path:
        return self.project_dir / "applications"

    @property
    def scan_results_dir(self) -> Path:
        return self.project_dir / "scan_results"

    @property
    def bookmarks_path(self) -> Path:
        return self.project_dir / "BOOKMARKS.md"

    @property
    def context_path(self) -> Path:
        return self.project_dir / "CONTEXT.md"

    @property
    def env_path(self) -> Path:
        return self.project_dir / ".env"
