# 2026-10-05-01 — Initial public release (Notion edition)

First commit of `grggls/jobbing-skills`. The earlier development history stays
in a private repository; this repository starts from one squashed commit with
no personal data.

## State at release

- Tracking lives in the user's Notion workspace, reached only through
  Claude's Notion connector (ADR-013). The `setup` skill creates a "Job
  Search" page with a "Job Tracker" database (board view), an "Interviews"
  database (relation + calendar view), and a "Comparisons" page.
- 14 generic skills in `.claude/skills/` (ASD-STE100), loadable as project
  skills or as the `jobbing` plugin (`.claude-plugin/`).
- `jobbing` CLI (Python 3.14): `init`, `home`, `example`, `notion`, `pdf`,
  `browse`, `scan`. `make check` passes (ruff, mypy --strict, pytest,
  coverage 97%).
- Local private data lives only in the git-ignored workspace (`CONTEXT.md`,
  `BOOKMARKS.md`, `.env`, `applications/`, `scan_results/`).

## Not yet verified

- **The Notion operations have not run against a real workspace.** At release
  the connector in the authoring session returned "API token is invalid". The
  `setup` schema (DDL), the board/calendar view `configure` strings, the
  property value formats, and the PDF upload (`notion-create-file-upload` +
  `curl`) are written from the connector's tool schemas, not from a run.
- `claude plugin marketplace add grggls/jobbing-skills` against the pushed
  repository.
- `install.sh` on a Mac without Homebrew (the Homebrew-install branch).

## What's next

> Read `CLAUDE.md` and this worklog. Make sure that the Notion connector is
> signed in (`/mcp`). Run the `setup` skill against a test Notion workspace
> and fix any skill text that does not match the connector's real behavior
> (database DDL, view DSL, property formats, file upload). Then run one full
> `analyze` → `apply` cycle with the example profile and confirm the company
> page, the board card, and the uploaded PDFs. Record each fix in a new
> worklog. Then test the plugin install from GitHub on a clean Claude Code
> profile.
