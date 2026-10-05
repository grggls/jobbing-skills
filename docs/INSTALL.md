# Install Procedure

This document uses ASD-STE100 Simplified Technical English. A person or a
Claude agent can follow it.

## 1. Requirements

- macOS (Linux operates if Homebrew can install there)
- an Internet connection
- an administrator account on the computer (Homebrew needs it)
- the Claude app (https://claude.ai/download) or Claude Code
- a Notion account (the free plan is sufficient)

The user does not need git, Python, Homebrew, or shell configuration files.
The installer installs or creates all of them.

## 2. Install

1. Open Terminal.
2. Paste this command and press Return:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/grggls/jobbing-skills/main/install.sh)"
```

3. If the installer asks for a password, type the password of the computer
   account. The screen does not show the characters.
4. If macOS asks to install "command line developer tools", select
   "Install".

WARNING: Do not use `curl ... | bash`. Homebrew asks questions during its
install, and a pipe stops those questions from operating. Use the command in
step 2.

The installer does these steps:

1. It finds Homebrew. If Homebrew is not installed, it installs Homebrew.
2. It installs `git`, `python@3.14`, and `uv` with Homebrew.
3. It downloads jobbing-skills to `~/Documents/jobbing-skills`. If that
   folder is already a download, it updates it.
4. It creates `.venv/`, installs the `jobbing` package, and downloads a
   headless Chromium (about 100 MB).
5. It links `jobbing` to `~/.local/bin/jobbing`. It adds a marked block to
   `~/.zprofile` and `~/.zshrc` (and to `~/.bash_profile` and `~/.bashrc` if
   the login shell is bash). It creates a file if it does not exist. The
   block loads Homebrew and adds `~/.local/bin` to `PATH`. On a second run,
   it replaces the block. It does not add a second block.
6. It opens a new login shell to make sure that `jobbing` is found.
7. It runs `jobbing init`. This creates `CONTEXT.md`, `BOOKMARKS.md`,
   `applications/`, and `scan_results/`. It does not overwrite files that
   exist.

Options. Put them after the command, with `--` first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/grggls/jobbing-skills/main/install.sh)" -- --no-browser
```

- `--no-browser`: do not install Playwright. `jobbing browse` and
  `jobbing scan fetch` will not operate. All other commands operate.
- `--dev`: also install the test and lint tools and the pre-commit hook.

Environment variables:

- `JOBBING_DIR`: a different install folder.
- `JOBBING_REPO`: a different git URL (for tests).

From a clone, run `./install.sh` in the clone. The installer then uses that
folder and does not download a second copy.

## 3. Verify

1. Open a new Terminal window.
2. Run `jobbing home`. The output must be `~/Documents/jobbing-skills`
   (as a full path).
3. Run `jobbing browse https://example.com`. The output must be JSON with
   `"title": "Example Domain"`. If you used `--no-browser`, skip this step.

## 4. Connect Notion

The skills write to Notion through Claude's Notion connector. The repository
holds no Notion key.

1. In the Claude app, open Settings → Connectors. Connect Notion. Give it
   access to the workspace that you will use.
2. In Claude Code, type `/mcp`. Make sure that Notion shows as connected.

## 5. Open the folder in Claude

- Claude app: open the Code tab. Select the folder
  `~/Documents/jobbing-skills`.
- Terminal: `cd ~/Documents/jobbing-skills && claude`.

Claude then loads the skills in `.claude/skills/` and the instructions in
`CLAUDE.md`.

## 6. Set up the profile

1. Ask the user for their CV. Use it to fill in `CONTEXT.md`. Remove the hint
   text. Do not add facts that are not in the CV or in the user's messages.
2. Ask the user to read `CONTEXT.md` and correct it.
3. Make sure that these sections are complete, because the skills use them:
   "Profile", "Career Timeline", "Target Roles", "Compensation", "CV Location
   Lines", "Scoring Preferences", "Cover Letter Plan", "Hard Rules",
   "Writing Style".
4. Help the user replace the example links in `BOOKMARKS.md` with job boards
   for their field. Use one `## Category` heading for each group and one
   `- [Label](URL)` link on each line.

## 7. Create the Notion tracker

1. The user says "set up my Notion tracker". Use the `setup` skill.
2. The skill creates a "Job Search" page with:
   - a "Job Tracker" database with a "Board" view grouped by status
   - an "Interviews" database with a "Calendar" view
   - a "Comparisons" page
3. The skill runs `jobbing notion --home ... --tracker ... --interviews ...`.
   This writes the URLs to `.env`.
4. Run `jobbing notion`. The output must show three URLs.

## 8. Install as a plugin (optional, for developers)

1. Do the steps in sections 2 to 7. The plugin needs the `jobbing` CLI.
2. Add the marketplace and install the plugin:

```bash
claude plugin marketplace add grggls/jobbing-skills
claude plugin install jobbing@jobbing-skills
```

3. Set `JOBBING_HOME` to the workspace. Add this line to `~/.zshrc`:

```bash
export JOBBING_HOME="$HOME/Documents/jobbing-skills"
```

The skill names then have the `jobbing:` prefix, for example
`/jobbing:analyze`.

CAUTION: Do not install the plugin if the user works only in the
jobbing-skills folder. Claude then shows each skill two times.

## 9. Update

Run the install command from section 2 again. The update does not change
`CONTEXT.md`, `BOOKMARKS.md`, `applications/`, or the data in Notion.

## 10. Troubleshooting

| Problem | Cause | Remedy |
|---------|-------|--------|
| `jobbing: command not found` in a Terminal window that was open during the install | That window started before the install. | Open a new Terminal window. |
| `jobbing: command not found` in a new window | The shell is not zsh or bash, or a profile file overrides `PATH`. | Use the full path: `~/Documents/jobbing-skills/.venv/bin/jobbing`. |
| Homebrew install stops with a permission error | The account is not an administrator. | Use an administrator account, or ask an administrator to install Homebrew. |
| "exists and is not a jobbing-skills download" | `~/Documents/jobbing-skills` has other files. | Move that folder, or set `JOBBING_DIR` to a different folder. |
| "Playwright is not available" | The installer ran with `--no-browser`. | Run the install command again without `--no-browser`. |
| `jobbing browse` returns an empty page | The site needs more time to load. | Add `--wait-until networkidle` or `--wait-seconds 5`. |
| A Notion call returns "unauthorized" or "API token is invalid" | The Notion connector sign-in expired. | Reconnect Notion in Settings → Connectors, or type `/mcp` in Claude Code. |
| `jobbing notion` says "Notion is not set up" | The `setup` skill did not run, or `.env` is in a different workspace. | Run `jobbing home`. Ask Claude to set up the Notion tracker. |
| The Notion board has no columns | The board view was not created. | In Notion, open "Job Tracker", select "+ Add view" → "Board", group by "Status". |
