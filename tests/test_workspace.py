"""Tests for workspace setup: JOBBING_HOME, .env settings, init, home, example."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from jobbing.cli import _cmd_example, _cmd_home, _cmd_init
from jobbing.config import Config
from jobbing.models import CompanyData
from jobbing.scanner import parse_bookmarks


class TestJobbingHome:
    def test_env_var_sets_project_dir(self, tmp_path: Path) -> None:
        with patch.dict(os.environ, {"JOBBING_HOME": str(tmp_path)}):
            config = Config.load()
        assert config.project_dir == tmp_path

    def test_explicit_project_dir_wins_over_env(self, tmp_path: Path) -> None:
        other = tmp_path / "other"
        other.mkdir()
        with patch.dict(os.environ, {"JOBBING_HOME": str(tmp_path)}):
            config = Config.load(project_dir=other)
        assert config.project_dir == other

    def test_tilde_is_expanded(self) -> None:
        with patch.dict(os.environ, {"JOBBING_HOME": "~/jobsearch"}):
            config = Config.load()
        assert config.project_dir == Path.home() / "jobsearch"

    def test_home_command_prints_path(
        self, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _cmd_home(None, config)
        assert capsys.readouterr().out.strip() == str(config.project_dir)


class TestInit:
    def test_creates_workspace_files(self, tmp_path: Path) -> None:
        config = Config.load(project_dir=tmp_path)
        _cmd_init(None, config)

        assert config.context_path.is_file()
        assert config.bookmarks_path.is_file()
        assert config.applications_dir.is_dir()
        assert config.scan_results_dir.is_dir()

    def test_bookmarks_template_parses(self, tmp_path: Path) -> None:
        config = Config.load(project_dir=tmp_path)
        _cmd_init(None, config)
        assert len(parse_bookmarks(config.bookmarks_path)) > 0

    def test_never_overwrites_existing_files(self, tmp_path: Path) -> None:
        config = Config.load(project_dir=tmp_path)
        config.context_path.write_text("my real profile\n", encoding="utf-8")
        config.bookmarks_path.write_text("my boards\n", encoding="utf-8")

        _cmd_init(None, config)

        assert config.context_path.read_text(encoding="utf-8") == "my real profile\n"
        assert config.bookmarks_path.read_text(encoding="utf-8") == "my boards\n"

    def test_is_idempotent(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        config = Config.load(project_dir=tmp_path)
        _cmd_init(None, config)
        capsys.readouterr()
        _cmd_init(None, config)
        out = capsys.readouterr().out
        assert "created" not in out
        assert "exists" in out


class TestExample:
    def test_prints_valid_company_json(
        self, config: Config, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _cmd_example(None, config)
        out = capsys.readouterr().out
        json.loads(out)
        path = tmp_path / "example.json"
        path.write_text(out, encoding="utf-8")
        company = CompanyData.from_json_file(path)
        assert company.company_upper
        assert company.cv.jobs
        assert company.cl.paragraphs


class TestDotenvSettings:
    def test_settings_read_from_dotenv(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text(
            "SCORE_THRESHOLD=70\nFOLLOWUP_THRESHOLD_DAYS=9\nNOTION_TRACKER_URL=https://n/t\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load(project_dir=tmp_path)
        assert config.score_threshold == 70
        assert config.followup_threshold_days == 9
        assert config.notion_tracker_url == "https://n/t"

    def test_env_var_wins_over_dotenv(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text("SCORE_THRESHOLD=70\n")
        with patch.dict(os.environ, {"SCORE_THRESHOLD": "80"}, clear=True):
            config = Config.load(project_dir=tmp_path)
        assert config.score_threshold == 80
