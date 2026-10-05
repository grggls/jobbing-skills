"""Unified CLI entry point for the Jobbing package.

The CLI does the local, deterministic work. Tracking lives in Notion and is
done by the skills through Claude's Notion connector.

    jobbing init                     # create CONTEXT.md, BOOKMARKS.md, applications/
    jobbing home                     # print the workspace path
    jobbing example                  # print the CV/cover-letter JSON template
    jobbing notion [--home URL] [--tracker URL] [--interviews URL]
    jobbing pdf <company> [--cv-only] [--cl-only] [--output-dir path]
    jobbing browse <url> [--wait-until ...] [--wait-seconds N]
    jobbing scan bookmarks [--categories CAT1 CAT2]
    jobbing scan fetch [--categories CAT1 CAT2] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from importlib import resources
from pathlib import Path
from typing import Any

from jobbing.config import Config

# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    """Convert a company name to a filesystem-safe slug with hyphens.

    "Acme Corp" → "Acme-Corp"
    "Globex (Initrode)" → "Globex-(Initrode)"
    "Doc Morris - Zur Rose Group" → "Doc-Morris-Zur-Rose-Group"
    """
    safe = name.replace("/", "-").replace("\\", "-").replace(":", "-").strip()
    safe = safe.replace(" ", "-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe


def _normalize_company_name(s: str) -> str:
    """Strip parenthetical suffixes for fuzzy directory matching.

    e.g. "Initech (Anonymous Client)" → "initech"
    """
    return re.sub(r"\s*\([^)]*\)\s*$", "", s).strip().lower()


def _find_company_dir(company_input: str, applications_dir: Path) -> Path | None:
    """Find the per-company directory under applications/.

    Tries exact slug match, then case-insensitive match, then normalized
    (parentheticals stripped) match.
    """
    if not applications_dir.is_dir():
        return None

    input_slug = slugify(company_input)
    input_lower = input_slug.lower()
    input_normalized = _normalize_company_name(company_input)

    for d in applications_dir.iterdir():
        if not d.is_dir():
            continue
        dir_lower = d.name.lower()
        if (
            d.name == input_slug
            or dir_lower == input_lower
            or dir_lower.replace("-", " ") == input_lower.replace("-", " ")
            or _normalize_company_name(d.name) == input_normalized
        ):
            return d
    return None


# ---------------------------------------------------------------------------
# PDF subcommand
# ---------------------------------------------------------------------------


def _cmd_pdf(args: argparse.Namespace, config: Config) -> None:
    """Generate CV and/or cover letter PDFs from applications/{Slug}/{Slug}.json."""
    from jobbing.models import CompanyData
    from jobbing.pdf import PDFGenerator

    company_dir = _find_company_dir(args.company, config.applications_dir)
    if company_dir is None:
        print(
            f"Error: No company directory found for '{args.company}' in {config.applications_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    json_file = company_dir / f"{slugify(args.company)}.json"
    if not json_file.exists():
        json_candidates = sorted(company_dir.glob("*.json"))
        if not json_candidates:
            print(f"Error: No JSON file found in {company_dir}", file=sys.stderr)
            sys.exit(1)
        json_file = json_candidates[0]

    company_data = CompanyData.from_json_file(json_file)
    output_dir = Path(args.output_dir) if args.output_dir else company_dir

    paths = PDFGenerator().generate(
        company_data,
        output_dir,
        cv_only=args.cv_only,
        cl_only=args.cl_only,
    )

    for path in paths:
        size = path.stat().st_size
        print(f"{path}: {size:,} bytes ({size / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Browse subcommand
# ---------------------------------------------------------------------------


def _cmd_browse(args: argparse.Namespace, _config: Config) -> None:
    """Fetch a URL via headless Playwright+stealth and print structured JSON."""
    import asyncio

    from jobbing.browser import _require_playwright, fetch_page

    try:
        _require_playwright()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = asyncio.run(
            fetch_page(
                args.url,
                wait_until=args.wait_until,
                extra_wait_s=args.wait_seconds,
            )
        )
    except Exception as e:  # browser launch failures (e.g. Chromium not downloaded)
        first_line = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
        print(
            f"Error: browser failed to start: {first_line}\n"
            "If Chromium is missing, run: playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    output: dict[str, Any] = {
        "url": result.url,
        "title": result.title,
        "company": result.company,
        "description": result.description,
        "location": result.location,
        "raw_text": result.raw_text,
        "char_count": result.char_count,
    }
    if result.error:
        output["error"] = result.error

    print(json.dumps(output, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Scan subcommands
# ---------------------------------------------------------------------------


def _cmd_scan(args: argparse.Namespace, config: Config) -> None:
    """Fetch job boards or list bookmarks for Claude to process."""
    if args.scan_command == "bookmarks":
        _scan_bookmarks(args, config)
    else:
        _scan_fetch(args, config)


def _scan_bookmarks(args: argparse.Namespace, config: Config) -> None:
    """List parsed bookmarks from BOOKMARKS.md."""
    from jobbing.scanner import Bookmark, parse_bookmarks

    bookmarks = parse_bookmarks(config.bookmarks_path)

    if args.categories:
        cat_lower = [c.lower() for c in args.categories]
        bookmarks = [b for b in bookmarks if b.category.lower() in cat_lower]

    by_cat: dict[str, list[Bookmark]] = {}
    for b in bookmarks:
        by_cat.setdefault(b.category, []).append(b)

    print(f"Bookmarks: {len(bookmarks)} across {len(by_cat)} categories\n")
    for cat, bms in by_cat.items():
        print(f"## {cat} ({len(bms)})")
        for b in bms:
            print(f"  - {b.label}")
        print()


def _scan_fetch(args: argparse.Namespace, config: Config) -> None:
    """Fetch board pages and save content for Claude to process."""
    from jobbing.browser import _require_playwright
    from jobbing.scanner import fetch_boards, parse_bookmarks, save_fetch_results

    try:
        _require_playwright()
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    bookmarks = parse_bookmarks(config.bookmarks_path)
    if args.categories:
        cat_lower = [c.lower() for c in args.categories]
        bookmarks = [b for b in bookmarks if b.category.lower() in cat_lower]
    if args.limit:
        bookmarks = bookmarks[: args.limit]

    if not bookmarks:
        print("No bookmarks match the filter.")
        return

    print(f"Fetching {len(bookmarks)} boards...")
    result = fetch_boards(bookmarks)
    filepath = save_fetch_results(result, config.scan_results_dir)

    print(f"\nFetch complete: {filepath}")
    print(f"  Fetched: {result.boards_fetched}/{result.boards_requested}")
    if result.boards_failed:
        print(f"  Failed: {result.boards_failed}")
    for fb in result.boards:
        status = f"{fb.char_count:,} chars" if not fb.error else f"FAILED: {fb.error}"
        print(f"  {fb.bookmark.label}: {status}")


# ---------------------------------------------------------------------------
# Workspace subcommands
# ---------------------------------------------------------------------------

# Template file in the package -> destination relative to the workspace.
_INIT_FILES: list[tuple[str, str]] = [
    ("CONTEXT.md", "CONTEXT.md"),
    ("BOOKMARKS.md", "BOOKMARKS.md"),
]

# CLI flag -> .env key for `jobbing notion`.
_NOTION_KEYS: dict[str, str] = {
    "home": "NOTION_HOME_URL",
    "tracker": "NOTION_TRACKER_URL",
    "interviews": "NOTION_INTERVIEWS_URL",
}


def _template_text(name: str) -> str:
    return resources.files("jobbing").joinpath("templates", name).read_text(encoding="utf-8")


def _cmd_init(args: argparse.Namespace | None, config: Config) -> None:
    """Create the workspace files. Never overwrite a file that exists."""
    root = config.project_dir
    for template, rel in _INIT_FILES:
        dest = root / rel
        if dest.exists():
            print(f"exists   {dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(_template_text(template), encoding="utf-8")
        print(f"created  {dest}")
    for d in (config.applications_dir, config.scan_results_dir):
        if d.is_dir():
            print(f"exists   {d}/")
        else:
            d.mkdir(parents=True)
            print(f"created  {d}/")
    print(f"\nWorkspace: {root}")


def _cmd_home(args: argparse.Namespace | None, config: Config) -> None:
    """Print the workspace path."""
    print(config.project_dir)


def _cmd_example(args: argparse.Namespace | None, config: Config) -> None:
    """Print the example CV/cover-letter JSON (the schema template)."""
    print(_template_text("example_company.json"), end="")


def _set_dotenv(env_path: Path, updates: dict[str, str]) -> None:
    """Set KEY=value lines in a .env file. Keep all other lines unchanged."""
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.is_file() else []
    remaining = dict(updates)
    out: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in remaining:
            out.append(f"{key}={remaining.pop(key)}")
        else:
            out.append(line)
    out.extend(f"{k}={v}" for k, v in remaining.items())
    env_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _cmd_notion(args: argparse.Namespace, config: Config) -> None:
    """Show the saved Notion locations, or save new ones to the workspace .env."""
    updates = {
        env_key: getattr(args, flag)
        for flag, env_key in _NOTION_KEYS.items()
        if getattr(args, flag, None)
    }
    if updates:
        _set_dotenv(config.env_path, updates)
        config = Config.load(project_dir=config.project_dir)

    shown = {
        "home": config.notion_home_url,
        "tracker": config.notion_tracker_url,
        "interviews": config.notion_interviews_url,
    }
    print(json.dumps(shown, indent=2))
    if not all(shown.values()):
        print(
            "Notion is not set up. Ask Claude to run the 'setup' skill.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobbing", description="AI-assisted job search.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- workspace ---
    subparsers.add_parser("init", help="Create CONTEXT.md, BOOKMARKS.md and folders")
    subparsers.add_parser("home", help="Print the workspace path")
    subparsers.add_parser("example", help="Print the CV/cover-letter JSON template")

    p_notion = subparsers.add_parser("notion", help="Show or save the Notion locations")
    p_notion.add_argument("--home", help="URL of the 'Job Search' parent page")
    p_notion.add_argument("--tracker", help="URL of the 'Job Tracker' database")
    p_notion.add_argument("--interviews", help="URL of the 'Interviews' database")

    # --- pdf ---
    p_pdf = subparsers.add_parser("pdf", help="Generate PDF documents")
    p_pdf.add_argument("company", help="Company name")
    p_pdf.add_argument("--output-dir", help="Output directory")
    p_pdf.add_argument("--cv-only", action="store_true", help="CV only")
    p_pdf.add_argument("--cl-only", action="store_true", help="Cover letter only")

    # --- scan ---
    p_scan = subparsers.add_parser("scan", help="Job board scanning utilities")
    scan_subs = p_scan.add_subparsers(dest="scan_command", required=True)
    p_scan_bm = scan_subs.add_parser("bookmarks", help="List parsed bookmarks")
    p_scan_bm.add_argument("--categories", nargs="+", help="Filter to categories")
    p_scan_fetch = scan_subs.add_parser("fetch", help="Fetch board pages")
    p_scan_fetch.add_argument("--categories", nargs="+", help="Filter to categories")
    p_scan_fetch.add_argument("--limit", type=int, help="Max boards to fetch")

    # --- browse ---
    p_browse = subparsers.add_parser("browse", help="Fetch a URL via headless browser")
    p_browse.add_argument("url", help="URL to fetch")
    p_browse.add_argument(
        "--wait-until",
        default="domcontentloaded",
        choices=["domcontentloaded", "networkidle", "load", "commit"],
        help="Playwright wait strategy (default: domcontentloaded)",
    )
    p_browse.add_argument(
        "--wait-seconds",
        type=float,
        default=2.0,
        help="Extra seconds to wait after page load (default: 2.0)",
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_COMMANDS = {
    "init": _cmd_init,
    "home": _cmd_home,
    "example": _cmd_example,
    "notion": _cmd_notion,
    "pdf": _cmd_pdf,
    "scan": _cmd_scan,
    "browse": _cmd_browse,
}


def main() -> None:
    args = _build_parser().parse_args()
    _COMMANDS[args.command](args, Config.load())


if __name__ == "__main__":
    main()
