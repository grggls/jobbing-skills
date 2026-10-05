"""Tests for jobbing.cli — naming, pdf, scan, browse, notion, and dispatch."""

from __future__ import annotations

import argparse
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from jobbing.cli import (
    _build_parser,
    _cmd_browse,
    _cmd_example,
    _cmd_notion,
    _cmd_pdf,
    _cmd_scan,
    _find_company_dir,
    _normalize_company_name,
    _scan_bookmarks,
    _scan_fetch,
    _set_dotenv,
    main,
    slugify,
)
from jobbing.config import Config
from jobbing.scanner import Bookmark, FetchedBoard

_PATCH_PARSE_BOOKMARKS = "jobbing.scanner.parse_bookmarks"
_PATCH_FETCH_BOARDS = "jobbing.scanner.fetch_boards"
_PATCH_SAVE_FETCH = "jobbing.scanner.save_fetch_results"


def _pdf_args(company: str, **kw: object) -> argparse.Namespace:
    defaults: dict[str, object] = {"output_dir": None, "cv_only": False, "cl_only": False}
    defaults.update(kw)
    return argparse.Namespace(company=company, **defaults)


def _write_example_json(config: Config, slug: str) -> Path:
    company_dir = config.applications_dir / slug
    company_dir.mkdir(parents=True)
    path = company_dir / f"{slug}.json"
    out = io.StringIO()
    with redirect_stdout(out):
        _cmd_example(None, config)
    path.write_text(out.getvalue(), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------


class TestSlugify:
    @pytest.mark.parametrize(
        ("name", "slug"),
        [
            ("Acme Corp", "Acme-Corp"),
            ("Globex (Initrode)", "Globex-(Initrode)"),
            ("Doc Morris - Zur Rose Group", "Doc-Morris-Zur-Rose-Group"),
            ("A/B: Test", "A-B-Test"),
            ("4ACME2", "4ACME2"),
        ],
    )
    def test_slugify(self, name: str, slug: str) -> None:
        assert slugify(name) == slug

    def test_normalize_strips_parenthetical(self) -> None:
        assert _normalize_company_name("Initech (Anonymous Client)") == "initech"


class TestFindCompanyDir:
    def test_missing_applications_dir(self, tmp_path: Path) -> None:
        assert _find_company_dir("Acme", tmp_path / "nope") is None

    @pytest.mark.parametrize("query", ["Acme Corp", "acme corp", "Acme-Corp", "ACME CORP"])
    def test_matches_slug_variants(self, tmp_path: Path, query: str) -> None:
        (tmp_path / "Acme-Corp").mkdir()
        assert _find_company_dir(query, tmp_path) == tmp_path / "Acme-Corp"

    def test_matches_without_parenthetical(self, tmp_path: Path) -> None:
        (tmp_path / "Initech-(Anonymous-Client)").mkdir()
        found = _find_company_dir("Initech (Anonymous Client)", tmp_path)
        assert found == tmp_path / "Initech-(Anonymous-Client)"

    def test_ignores_files(self, tmp_path: Path) -> None:
        (tmp_path / "Acme").write_text("not a dir")
        assert _find_company_dir("Acme", tmp_path) is None


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------


class TestCmdPdf:
    def test_generates_real_pdfs(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        _write_example_json(config, "Acme-Corp")
        _cmd_pdf(_pdf_args("Acme Corp"), config)

        company_dir = config.applications_dir / "Acme-Corp"
        cv, cl = company_dir / "ACME-CORP-CV.pdf", company_dir / "ACME-CORP-CL.pdf"
        assert cv.read_bytes().startswith(b"%PDF")
        assert cl.read_bytes().startswith(b"%PDF")
        out = capsys.readouterr().out
        assert "ACME-CORP-CV.pdf" in out
        assert "ACME-CORP-CL.pdf" in out

    def test_cv_only(self, config: Config) -> None:
        _write_example_json(config, "Acme-Corp")
        _cmd_pdf(_pdf_args("Acme Corp", cv_only=True), config)
        names = sorted(p.name for p in (config.applications_dir / "Acme-Corp").glob("*.pdf"))
        assert names == ["ACME-CORP-CV.pdf"]

    def test_output_dir(self, config: Config, tmp_path: Path) -> None:
        _write_example_json(config, "Acme-Corp")
        out_dir = tmp_path / "out"
        _cmd_pdf(_pdf_args("Acme Corp", output_dir=str(out_dir)), config)
        assert (out_dir / "ACME-CORP-CV.pdf").is_file()

    def test_falls_back_to_any_json(self, config: Config) -> None:
        path = _write_example_json(config, "Acme-Corp")
        path.rename(path.with_name("other.json"))
        _cmd_pdf(_pdf_args("Acme Corp", cl_only=True), config)
        assert (config.applications_dir / "Acme-Corp" / "ACME-CORP-CL.pdf").is_file()

    def test_missing_company_exits(self, config: Config) -> None:
        with pytest.raises(SystemExit, match="1"):
            _cmd_pdf(_pdf_args("Nope"), config)

    def test_missing_json_exits(self, config: Config) -> None:
        (config.applications_dir / "Acme").mkdir(parents=True)
        with pytest.raises(SystemExit, match="1"):
            _cmd_pdf(_pdf_args("Acme"), config)


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


class TestCmdScan:
    def test_dispatches_bookmarks(self, config: Config) -> None:
        ns = argparse.Namespace(scan_command="bookmarks", categories=None)
        with patch("jobbing.cli._scan_bookmarks") as fn:
            _cmd_scan(ns, config)
        fn.assert_called_once_with(ns, config)

    def test_dispatches_fetch(self, config: Config) -> None:
        ns = argparse.Namespace(scan_command="fetch", categories=None, limit=None)
        with patch("jobbing.cli._scan_fetch") as fn:
            _cmd_scan(ns, config)
        fn.assert_called_once_with(ns, config)


class TestScanBookmarks:
    def test_lists_and_groups(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        bookmarks = [
            Bookmark(label="Board A", url="https://a.com", category="Climate"),
            Bookmark(label="Board B", url="https://b.com", category="Climate"),
            Bookmark(label="Board C", url="https://c.com", category="Startups"),
        ]
        with patch(_PATCH_PARSE_BOOKMARKS, return_value=bookmarks):
            _scan_bookmarks(argparse.Namespace(categories=None), config)
        out = capsys.readouterr().out
        assert "Bookmarks: 3 across 2 categories" in out
        assert "Climate (2)" in out
        assert "Board C" in out

    def test_filters_by_category(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        bookmarks = [
            Bookmark(label="Board A", url="https://a.com", category="Climate"),
            Bookmark(label="Board B", url="https://b.com", category="Startups"),
        ]
        with patch(_PATCH_PARSE_BOOKMARKS, return_value=bookmarks):
            _scan_bookmarks(argparse.Namespace(categories=["climate"]), config)
        out = capsys.readouterr().out
        assert "Board A" in out
        assert "Board B" not in out


class TestScanFetch:
    @staticmethod
    def _result(boards: list[MagicMock], fetched: int, failed: int) -> MagicMock:
        result = MagicMock()
        result.boards_fetched = fetched
        result.boards_requested = fetched + failed
        result.boards_failed = failed
        result.boards = boards
        return result

    def test_fetches_and_reports(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        bm = Bookmark(label="Board A", url="https://a.com", category="Cat")
        board = MagicMock(spec=FetchedBoard)
        board.bookmark, board.char_count, board.error = bm, 5000, ""
        with (
            patch("jobbing.browser._require_playwright"),
            patch(_PATCH_PARSE_BOOKMARKS, return_value=[bm]),
            patch(_PATCH_FETCH_BOARDS, return_value=self._result([board], 1, 0)),
            patch(_PATCH_SAVE_FETCH, return_value=Path("/tmp/r.json")),
        ):
            _scan_fetch(argparse.Namespace(categories=None, limit=None), config)
        out = capsys.readouterr().out
        assert "Fetched: 1/1" in out
        assert "5,000 chars" in out

    def test_failed_boards_shown(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        bm = Bookmark(label="Bad", url="https://bad.com", category="Cat")
        board = MagicMock(spec=FetchedBoard)
        board.bookmark, board.char_count, board.error = bm, 0, "Connection timeout"
        with (
            patch("jobbing.browser._require_playwright"),
            patch(_PATCH_PARSE_BOOKMARKS, return_value=[bm]),
            patch(_PATCH_FETCH_BOARDS, return_value=self._result([board], 0, 1)),
            patch(_PATCH_SAVE_FETCH, return_value=Path("/tmp/r.json")),
        ):
            _scan_fetch(argparse.Namespace(categories=None, limit=None), config)
        out = capsys.readouterr().out
        assert "Failed: 1" in out
        assert "FAILED: Connection timeout" in out

    def test_limit_applied(self, config: Config) -> None:
        bms = [Bookmark(label=f"B{i}", url=f"https://{i}.com", category="C") for i in range(10)]
        with (
            patch("jobbing.browser._require_playwright"),
            patch(_PATCH_PARSE_BOOKMARKS, return_value=bms),
            patch(_PATCH_FETCH_BOARDS, return_value=self._result([], 3, 0)) as fetch,
            patch(_PATCH_SAVE_FETCH, return_value=Path("/tmp/r.json")),
        ):
            _scan_fetch(argparse.Namespace(categories=None, limit=3), config)
        assert len(fetch.call_args[0][0]) == 3

    def test_no_matching_bookmarks(
        self, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with (
            patch("jobbing.browser._require_playwright"),
            patch(_PATCH_PARSE_BOOKMARKS, return_value=[]),
        ):
            _scan_fetch(argparse.Namespace(categories=["x"], limit=None), config)
        assert "No bookmarks match the filter." in capsys.readouterr().out

    def test_playwright_missing_exits(self, config: Config) -> None:
        with (
            patch("jobbing.browser._require_playwright", side_effect=RuntimeError("missing")),
            pytest.raises(SystemExit),
        ):
            _scan_fetch(argparse.Namespace(categories=None, limit=None), config)


# ---------------------------------------------------------------------------
# Browse
# ---------------------------------------------------------------------------


class TestCmdBrowse:
    @staticmethod
    def _args() -> argparse.Namespace:
        return argparse.Namespace(
            url="https://x.com", wait_until="domcontentloaded", wait_seconds=0.0
        )

    def test_prints_json(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        from jobbing.browser import BrowseResult

        result = BrowseResult(
            url="https://x.com",
            title="X",
            company="",
            description="",
            location="",
            raw_text="hello",
            char_count=5,
        )

        async def fake_fetch(*a: object, **k: object) -> BrowseResult:
            return result

        with (
            patch("jobbing.browser._require_playwright"),
            patch("jobbing.browser.fetch_page", side_effect=fake_fetch),
        ):
            _cmd_browse(self._args(), config)
        data = json.loads(capsys.readouterr().out)
        assert data["title"] == "X"
        assert "error" not in data

    def test_launch_failure_is_clean_error(
        self, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        async def boom(*a: object, **k: object) -> None:
            raise RuntimeError("Executable doesn't exist\nmore detail")

        with (
            patch("jobbing.browser._require_playwright"),
            patch("jobbing.browser.fetch_page", side_effect=boom),
            pytest.raises(SystemExit),
        ):
            _cmd_browse(self._args(), config)
        err = capsys.readouterr().err
        assert "Executable doesn't exist" in err
        assert "playwright install chromium" in err

    def test_playwright_missing_exits(self, config: Config) -> None:
        with (
            patch("jobbing.browser._require_playwright", side_effect=RuntimeError("missing")),
            pytest.raises(SystemExit),
        ):
            _cmd_browse(self._args(), config)


# ---------------------------------------------------------------------------
# Notion locations
# ---------------------------------------------------------------------------


class TestNotion:
    @staticmethod
    def _args(**kw: str) -> argparse.Namespace:
        values: dict[str, str | None] = {"home": None, "tracker": None, "interviews": None}
        values.update(kw)
        return argparse.Namespace(**values)

    def test_unset_exits_with_hint(
        self, config: Config, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit, match="1"):
            _cmd_notion(self._args(), config)
        assert "setup" in capsys.readouterr().err

    def test_saves_and_shows(self, config: Config, capsys: pytest.CaptureFixture[str]) -> None:
        _cmd_notion(
            self._args(home="https://n/h", tracker="https://n/t", interviews="https://n/i"),
            config,
        )
        shown = json.loads(capsys.readouterr().out)
        assert shown == {
            "home": "https://n/h",
            "tracker": "https://n/t",
            "interviews": "https://n/i",
        }
        reloaded = Config.load(project_dir=config.project_dir)
        assert reloaded.notion_tracker_url == "https://n/t"

    def test_set_dotenv_keeps_other_lines(self, tmp_path: Path) -> None:
        env = tmp_path / ".env"
        env.write_text("# comment\nSCORE_THRESHOLD=70\nNOTION_TRACKER_URL=old\n")
        _set_dotenv(env, {"NOTION_TRACKER_URL": "new", "NOTION_HOME_URL": "h"})
        assert env.read_text().splitlines() == [
            "# comment",
            "SCORE_THRESHOLD=70",
            "NOTION_TRACKER_URL=new",
            "NOTION_HOME_URL=h",
        ]


# ---------------------------------------------------------------------------
# Parser and dispatch
# ---------------------------------------------------------------------------


class TestParser:
    @pytest.mark.parametrize("removed", ["track", "get", "set"])
    def test_tracker_commands_removed(self, removed: str) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args([removed])

    def test_scan_existing_removed(self) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args(["scan", "existing"])


class TestMain:
    @pytest.mark.parametrize(
        ("argv", "handler"),
        [
            (["init"], "_cmd_init"),
            (["home"], "_cmd_home"),
            (["example"], "_cmd_example"),
            (["notion"], "_cmd_notion"),
            (["pdf", "Acme"], "_cmd_pdf"),
            (["scan", "bookmarks"], "_cmd_scan"),
            (["browse", "https://x.com"], "_cmd_browse"),
        ],
    )
    def test_dispatch(self, config: Config, argv: list[str], handler: str) -> None:
        mock = MagicMock()
        with (
            patch("sys.argv", ["jobbing", *argv]),
            patch("jobbing.cli.Config.load", return_value=config),
            patch.dict("jobbing.cli._COMMANDS", {argv[0]: mock}),
        ):
            main()
        mock.assert_called_once()

    def test_end_to_end_init_example_pdf(self, config: Config) -> None:
        with patch("jobbing.cli.Config.load", return_value=config):
            with patch("sys.argv", ["jobbing", "init"]):
                main()
            _write_example_json(config, "Acme-Corp")
            with patch("sys.argv", ["jobbing", "pdf", "Acme Corp"]):
                main()
        assert (config.applications_dir / "Acme-Corp" / "ACME-CORP-CV.pdf").is_file()
