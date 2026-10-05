# 2026-10-05-02 — One-step installer

## Why

The first install on a non-developer's Mac failed at PATH setup: the user
had no `~/.zshrc` or `~/.zprofile` and could not add `~/.local/bin` to PATH.

## What changed

- `install.sh` at the repo root replaces `scripts/install.sh`. It runs with
  `/bin/bash -c "$(curl -fsSL .../install.sh)"`, installs Homebrew (if
  missing), `git`, `python@3.14`, `uv`, clones to
  `~/Documents/jobbing-skills`, installs the CLI and Chromium, writes a marked
  PATH block to `~/.zprofile` and `~/.zshrc` (creating them), checks a fresh
  login shell, and runs `jobbing init`. Re-running updates in place.
- Fix: `.gitignore` ignored `src/jobbing/templates/CONTEXT.md` and
  `BOOKMARKS.md`, so `jobbing init` crashed on every fresh clone (the CI
  `tests` job on main showed it). Patterns are now anchored to the root.
- README rewritten for non-developers (Claude app Code tab, Documents
  folder). Marketplace renamed to `jobbing-skills`
  (`claude plugin install jobbing@jobbing-skills`).
- The workflow skill falls back to `./.venv/bin/jobbing` if `jobbing` is not
  on PATH.

## Proof

- Vacuum test: empty `$HOME` (no rc files, no `Documents`), `env -i` with
  `PATH=/usr/bin:/bin:/usr/sbin:/sbin` (Homebrew present on disk but not on
  PATH), script piped as a string. Exit 0. A new interactive login zsh and a
  non-interactive login zsh both resolve `jobbing` and `brew`;
  `jobbing browse https://example.com` and `jobbing pdf` work. A second run
  exits 0, keeps one PATH block per file, and does not overwrite user files.

## CI

- All workflows run on `macos-latest`. `ci.yml` (lint, format, mypy, tests)
  moved off Linux.
- `install.yml` runs `scripts/ci/test-install.sh` (the vacuum test above,
  automated) on every PR and push. `install-fresh-homebrew` removes Homebrew
  first; it runs weekly, on demand, and on PRs labeled `fresh-homebrew`.
- `install.sh` no longer fails when the clone is not on a branch (CI checks
  out PRs detached); it skips the update with a warning.

## Not verified

- The Notion skills against a live workspace (see worklog -01).

## What's next

Same as worklog -01: verify the Notion `setup` skill and one full
`analyze` → `apply` cycle against a real Notion workspace.
