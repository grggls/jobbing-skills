# Install Procedure

This document uses ASD-STE100 Simplified Technical English. A person or a
Claude agent can follow it.

## 1. Requirements

- macOS or Linux
- git
- Claude Code (`claude`)
- a Notion account (the free plan is sufficient)
- `uv` (recommended), or Python 3.14 or later

NOTE: macOS includes Python 3.9. That version is too old. If `uv` is not
installed, install it with `brew install uv`.

## 2. Install the CLI

1. Clone the repository:

```bash
git clone https://github.com/grggls/jobbing-skills.git ~/jobbing
```

2. Go to the directory:

```bash
cd ~/jobbing
```

3. Run the install script:

```bash
scripts/install.sh
```

The script does these steps:

- It creates `.venv/` with Python 3.14 and installs the `jobbing` package
  with the browser extra.
- It installs Chromium for Playwright (about 100 MB).
- It links `.venv/bin/jobbing` to `~/.local/bin/jobbing`.
- It runs `jobbing init`. This creates `CONTEXT.md`, `BOOKMARKS.md`,
  `applications/`, and `scan_results/`. It does not overwrite files that
  exist.
- It checks for Claude Code.

Options:

- `--no-browser`: do not install Playwright. `jobbing browse` and
  `jobbing scan fetch` will not operate. All other commands operate.
- `--dev`: also install the test and lint tools and the pre-commit hook.

## 3. Verify the CLI

1. Open a new terminal.
2. Run `jobbing home`. The output must be the repository path.
3. Run `jobbing --help`. The output must list `init`, `home`, `example`,
   `notion`, `pdf`, `scan`, and `browse`.
4. Run `jobbing browse https://example.com`. The output must be JSON with
   `"title": "Example Domain"`. If you used `--no-browser`, skip this step.

## 4. Connect Notion

The skills write to Notion through Claude's Notion connector. The repository
holds no Notion key.

1. In the Claude app, open Settings → Connectors. Connect Notion. Give it
   access to the workspace that you will use.
2. In Claude Code, type `/mcp`. Make sure that Notion shows as connected. If
   it shows "needs authentication", select it and sign in.

## 5. Set up the profile

1. Open `CONTEXT.md`. Fill in each section. Remove the hint text.
2. If the user gives a CV, use it to fill in `CONTEXT.md`. Then ask the user
   to correct it. Do not add facts that are not in the CV or in the user's
   messages.
3. Make sure that these sections are complete, because the skills use them:
   "Profile", "Career Timeline", "Target Roles", "Compensation", "CV Location
   Lines", "Scoring Preferences", "Cover Letter Plan", "Hard Rules",
   "Writing Style".
4. Open `BOOKMARKS.md`. Replace the example links with job boards for the
   user's field. Use one `## Category` heading for each group and one
   `- [Label](URL)` link on each line.

## 6. Create the Notion tracker

1. Start Claude Code in the repository directory: `claude`.
2. Say "set up my Notion tracker". Claude uses the `setup` skill.
3. The skill creates a "Job Search" page with:
   - a "Job Tracker" database with a "Board" view grouped by status
   - an "Interviews" database with a "Calendar" view
   - a "Comparisons" page
4. The skill runs `jobbing notion --home ... --tracker ... --interviews ...`.
   This writes the URLs to `.env`.
5. Run `jobbing notion`. The output must show three URLs.

## 7. Use it

1. Go to the repository directory.
2. Start Claude Code: `claude`.
3. Give Claude a job posting or a job URL.

## 8. Install as a plugin (optional)

Use this procedure only if the user wants the skills in other directories or
in the Claude desktop app.

1. Do the steps in sections 2 to 6. The plugin needs the `jobbing` CLI.
2. Add the marketplace and install the plugin:

```bash
claude plugin marketplace add grggls/jobbing-skills
claude plugin install jobbing@jobbing
```

3. Set `JOBBING_HOME` to the workspace (the directory with `CONTEXT.md`).
   Add this line to `~/.zshrc`:

```bash
export JOBBING_HOME="$HOME/jobbing"
```

The skill names then have the `jobbing:` prefix, for example
`/jobbing:analyze`.

CAUTION: Do not install the plugin if the user works only in the repository
directory. Claude Code then shows each skill two times.

## 9. Update

```bash
cd ~/jobbing
git pull
scripts/install.sh
```

The update does not change the files in the workspace or the data in Notion.

## 10. Troubleshooting

| Problem | Cause | Remedy |
|---------|-------|--------|
| `jobbing: command not found` | `~/.local/bin` is not on `PATH`. | Add `export PATH="$HOME/.local/bin:$PATH"` to `~/.zshrc`. Open a new terminal. |
| "Need Python 3.14+ or uv" | Only an old Python is installed. | Run `brew install uv`. Run the install script again. |
| "Playwright is not available" | The browser extra is not installed. | Run `scripts/install.sh` without `--no-browser`. |
| `jobbing browse` returns an empty page | The site needs more time to load. | Add `--wait-until networkidle` or `--wait-seconds 5`. |
| A Notion call returns "unauthorized" or "API token is invalid" | The Notion connector sign-in expired. | Type `/mcp` in Claude Code, or reconnect Notion in Settings → Connectors. |
| `jobbing notion` says "Notion is not set up" | The `setup` skill did not run, or `.env` is in a different workspace. | Run `jobbing home`. Ask Claude to set up the Notion tracker. |
| A skill says `CONTEXT.md` is missing | `jobbing init` did not run, or `JOBBING_HOME` points at a different directory. | Run `jobbing home`. Run `jobbing init`. |
| The Notion board has no columns | The board view was not created. | In Notion, open "Job Tracker", select "+ Add view" → "Board", group by "Status". |
