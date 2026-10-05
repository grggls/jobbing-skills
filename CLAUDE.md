# jobbing-skills — Instructions for Claude

This file uses ASD-STE100 Simplified Technical English.

## 1. What this repository is

jobbing-skills helps one person find and apply for jobs. Claude scores job postings,
writes a tailored CV and cover letter for each job, prepares the user for
interviews, and tracks each application in the user's Notion workspace.

- `README.md`: the human introduction.
- `docs/INSTALL.md`: the install procedure. Use it when the user asks you to
  install or set up jobbing-skills.
- `docs/ARCHITECTURE.md`: how the parts work together.
- `docs/DECISIONS.md`: the reasons for the design.

## 2. Two types of task

### 2.1 Job search tasks

Examples: "analyze this job", "help me apply", "prep me for my interview",
"set up my Notion tracker".

1. Load the `workflow` skill. It has the shared rules, the Notion schema and
   operations, the local file layout, and the CLI reference.
2. Load the skill for the task (`setup`, `analyze`, `apply`, `track`, `scan`,
   `outreach`, `prep`, `debrief`, `followup`, `reassess`, `compare`,
   `disaggregate`).
3. Read `CONTEXT.md`. It is the only source of facts about the user.

The user's local data is private. Do not commit it. Git ignores it. The
tracking data is in the user's Notion workspace.

### 2.2 Development tasks

Examples: "fix this bug", "add a CLI flag".

1. Make a feature branch. Do not commit to `main`.
2. Write a test that fails. Then change the code.
3. Run `make check`. All checks must pass before you commit.
4. Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`).
5. If a change affects a skill or a document, update it in the same branch.
6. Do not add Notion API calls to the CLI. Notion access goes through the
   Notion connector in the skills (ADR-013).

## 3. Rules for all tasks

- Do not invent facts. If you do not know, say "not found" or "I could not
  verify this".
- Tell the user the source of each fact.
- Do not apologize. State the error, the fix, and what you will do next time.
- Be short. Give results, not narration.
- Put text that the user will copy (emails, messages) in the chat, not in a
  file.

## 4. Commands

```bash
jobbing home          # workspace path
jobbing init          # create CONTEXT.md, BOOKMARKS.md, applications/
jobbing notion        # show the saved Notion URLs
jobbing --help        # all commands
make check            # lint, format check, type check, tests
```

The full CLI reference is section 11 of `.claude/skills/workflow/SKILL.md`.

## 5. Repository layout

```text
.claude/skills/        the skills (one directory each)
.claude-plugin/        plugin and marketplace manifests
src/jobbing/           the CLI package
src/jobbing/templates/ files for `jobbing init` and `jobbing example`
tests/                 pytest suite
docs/                  install, architecture, decisions, worklog
install.sh             one-step installer (Homebrew, Python, uv, CLI, PATH)
```

Workspace files (`CONTEXT.md`, `BOOKMARKS.md`, `.env`, `applications/`,
`scan_results/`) are in the repository root by default. Git ignores them.
The installer puts the repository in `~/Documents/jobbing-skills`.
