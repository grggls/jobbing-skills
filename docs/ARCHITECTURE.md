# Architecture

This document uses ASD-STE100 Simplified Technical English.

## 1. Overview

jobbing-skills has four parts:

1. **Skills** (`.claude/skills/`): Markdown instructions for Claude. They
   contain the judgment: scoring, writing, interview prep, and the Notion
   operations.
2. **CLI** (`src/jobbing/`, command `jobbing`): a Python program for the
   local, deterministic work. It makes PDFs, fetches web pages, and stores
   the Notion URLs.
3. **Notion**: the user's tracker. One database for companies (with a board
   view), one database for interviews.
4. **Workspace**: the user's private local files (profile, bookmarks, CV
   data, PDFs).

Claude reads the skills, runs the CLI, edits local files, and reads and
writes Notion through Claude's Notion connector. The repository has no API
key, no server, and no database.

```text
 user ──▶ Claude Code ──loads──▶ skills (.claude/skills/*/SKILL.md)
                │
                ├──Notion connector──▶ Notion: Job Search
                │                        ├── Job Tracker (Board view)
                │                        ├── Interviews (Calendar view)
                │                        └── Comparisons
                │
                ├──runs──▶ jobbing CLI ──writes──▶ workspace/applications/{Slug}/*.pdf
                │                       ──fetches─▶ job boards (Playwright)
                │
                └──reads/edits──▶ workspace/CONTEXT.md, BOOKMARKS.md, *.json

 user ──▶ Notion app ──shows──▶ the board, company pages, interviews
```

## 2. Workspace

`jobbing home` prints the workspace path. The path is:

1. the value of `JOBBING_HOME`, if it is set
2. otherwise, the repository root (for an editable install from a clone).
   The installer clones to `~/Documents/jobbing-skills`, so that folder is
   the default workspace.

`jobbing init` creates the workspace files from templates in
`src/jobbing/templates/`. It does not overwrite files. Git ignores all
workspace data. The layout is in section 9 of the `workflow` skill.

The workspace `.env` file holds three Notion URLs (home page, tracker,
interviews). `jobbing notion` reads and writes them.

## 3. Notion

The `setup` skill creates the Notion structure one time. The schema is in
section 7 of the `workflow` skill. The key points:

- **Job Tracker**: one page per company. `Status` is a select with five
  values. The "Board" view groups by `Status`.
- **Interviews**: one page per interview. A two-way relation links each
  interview to its company.
- Each company page has fixed `##` sections (Fit Assessment, Company
  Research, and so on). Skills replace one section at a time.
- Final PDFs are uploaded to the company page through the connector's file
  upload tool (`notion-create-file-upload` plus one `curl` POST).

The CLI does not call Notion. Only Claude does, through the connector.

## 4. Package structure

```text
src/jobbing/
├── __main__.py        python -m jobbing
├── cli.py             all subcommands (argparse); slugify; company dir lookup
├── config.py          Config: workspace path, .env values, Notion URLs
├── models.py          dataclasses: CompanyData, CVData, CLData, Job, Education
├── pdf.py             CV and cover letter PDFs (reportlab)
├── browser.py         page fetch (Playwright + stealth, optional extra)
├── scanner.py         BOOKMARKS.md parser, board fetch
└── templates/         files for `jobbing init` and `jobbing example`
```

## 5. Skills

| Skill | Purpose |
|-------|---------|
| `workflow` | Shared rules, Notion schema and operations, local layout, CLI reference. Every other skill loads it first. |
| `setup` | Creates the Notion pages and databases one time. |
| `scoring` | The 0–100 formula. Preferences come from `CONTEXT.md`. |
| `analyze` | Score one job. Draft "Experience to Highlight". |
| `apply` | Company page, tailored JSON, PDFs, upload, ATS check. |
| `track` | Status and data changes; board summary; data checks. |
| `scan` | Fetch boards from `BOOKMARKS.md` and score the jobs. |
| `disaggregate` | Find the real companies behind aggregator listings. |
| `outreach` | LinkedIn contacts and connection messages. |
| `prep` | Interview preparation; creates the interview page. |
| `debrief` | Structured notes after an interview. |
| `followup` | Stale interview processes (read-only). |
| `reassess` | New score after interviews. |
| `compare` | Weighted comparison of active jobs; writes a Comparisons page. |

The skills contain no personal data. Personal rules are sections of
`CONTEXT.md` ("Hard Rules", "Scoring Preferences", "Cover Letter Plan",
"CV Location Lines", "Writing Style").

## 6. Distribution

- **Clone mode**: clone the repository and open Claude Code in it. Claude
  Code loads `.claude/skills/` as project skills and reads `CLAUDE.md`.
- **Plugin mode**: `.claude-plugin/marketplace.json` makes the repository a
  plugin marketplace. `.claude-plugin/plugin.json` points at
  `.claude/skills/`. Skills then have the `jobbing:` prefix. The CLI must
  still be installed, and `JOBBING_HOME` must point at the workspace.

Decisions and their reasons are in `DECISIONS.md` (ADR-011 to ADR-013 for
the current design).

## 7. Quality checks

```bash
make check    # ruff lint, ruff format --check, mypy --strict, pytest
```

All CI runs on macOS runners (no Linux). Two workflows:

- `ci.yml`: the `make check` steps on Python 3.14, on each push and pull
  request to `main`. The test coverage floor is 80%.
- `install.yml`: `scripts/ci/test-install.sh` runs the real `install.sh` in
  an empty home folder with Homebrew off `PATH`, then checks fresh login
  shells, `jobbing browse`, `jobbing pdf`, and a second run. The
  `install-fresh-homebrew` job removes Homebrew first. It runs weekly, on
  demand, and on pull requests with the `fresh-homebrew` label. The tests do not call Notion. The
Notion operations are in the skills, so a person or an agent verifies them by
running `setup` and one `analyze` → `apply` cycle against a real workspace.
