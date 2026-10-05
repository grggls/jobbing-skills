# Architecture Decision Records

## ADR-001: LangGraph for Agent Orchestration

**Status:** Abandoned

**Context:** The autonomous scan workflow was originally planned with LangGraph for multi-step orchestration. Options considered: plain Python functions, Celery task chains, custom state machine, LangGraph.

**Decision:** Originally accepted LangGraph, later abandoned. The Claude Code Skills approach (structured prompts invoking the `jobbing` CLI) proved sufficient for the interactive workflow without requiring a separate agent framework or API key.

**Rationale for abandoning:**
- Claude Code skills handle the interactive workflow without additional dependencies
- No separate Anthropic API key needed (skills use the Claude Code session)
- Simpler architecture with fewer moving parts
- The autonomous scanning use case didn't justify the dependency overhead

---

## ADR-002: Keep Notion as Primary Tracker

**Status:** Superseded by ADR-010

**Context:** Evaluated GitHub Projects, plain JSON, and custom webapp alternatives. Already have 49 companies tracked in Notion with rich page bodies (research, outreach, interview notes).

**Decision:** Keep Notion, add JsonFileTracker for testing.

**Rationale:**
- Existing data and workflow already in Notion
- Rich text body (markdown, databases, relations) valuable for interview prep
- Notion API sufficient for programmatic CRUD
- JSON fallback demonstrates the Protocol pattern without requiring Notion access

**Consequences:** Requires Notion API key. Not fully portable, but the TrackerBackend Protocol makes adding new backends straightforward.

---

## ADR-003: APScheduler over launchd

**Status:** Abandoned

**Context:** Previous system used macOS launchd plist for scheduling — hardcoded Python path, macOS-only, brittle. APScheduler was considered as a cross-platform replacement.

**Decision:** Originally accepted APScheduler, later abandoned. macOS launchd remains the scheduling mechanism for queue processing. The autonomous scanning daemon (`jobbing serve`) was never built.

**Rationale for abandoning:**
- Queue processing via launchd works reliably for the actual use case
- The `/scan` skill handles board scanning interactively, eliminating the need for a daemon
- Removes a runtime dependency

---

## ADR-004: Scoring Transparency and Tunability

**Status:** Accepted

**Context:** Initial scoring was too aggressive — Claude scored 30-35 on roles that were actually good fits because it penalized implied seniority mismatch (e.g., "Senior DevOps Engineer" titles for roles with leadership scope).

**Decision:** Implement full scoring transparency with editable criteria.

**Rationale:**
- `SCORING.md` is human-editable and version-tracked (now `.claude/skills/scoring/SKILL.md`)
- Every scoring decision preserved in `scan_results/` with full reasoning
- `ScoringResult` dataclass captures criteria_version, model, timestamp
- CLI provides `--review` (see filtered-out postings) and `--rescore` (re-evaluate with new criteria)
- Default threshold 60 (not 70) to avoid over-filtering

**Consequences:** More disk usage for scan logs. Adds complexity to the CLI. Worth it for trust and control.

---

## ADR-005: Autonomous Mode = Discovery Only

**Status:** Not Implemented (principle retained)

**Context:** Should the tool apply for jobs autonomously, or just help find and evaluate them?

**Decision:** Discovery and evaluation only. The tool never applies without explicit human approval. Originally planned as an autonomous daemon, this principle is now implemented through the interactive `/scan` and `/analyze` skills.

**Rationale:**

- Applying requires human judgment (CV tailoring, cover letter tone, timing)
- Mistakes in automated applications are hard to reverse
- The value is in reducing the search funnel, not automating the application
- Interactive Skills handle the full workflow with human-in-the-loop

**Consequences:** The user drives every step via Claude Code skills.

---

## ADR-006: src Layout Package Structure

**Status:** Accepted

**Context:** Python packages can use flat layout (`jobbing/`) or src layout (`src/jobbing/`).

**Decision:** Use src layout.

**Rationale:**
- Prevents accidental imports from the working directory
- Standard for modern Python packaging
- `pip install -e .` works correctly with src layout
- Consistent with professional Python projects

**Consequences:** Slightly deeper directory nesting. Minor inconvenience outweighed by correctness.

---

## ADR-007: TrackerBackend as Protocol (not ABC)

**Status:** Accepted

**Context:** Need a pluggable interface for tracker backends. Options: ABC, Protocol, duck typing.

**Decision:** Use `typing.Protocol` with `@runtime_checkable`.

**Rationale:**
- Structural subtyping — implementations don't need to inherit
- Runtime checking available via `isinstance()` if needed
- More Pythonic than ABC for this use case
- Demonstrates modern Python typing patterns

**Consequences:** Slightly less discoverable than ABC (no `raise NotImplementedError` on missing methods at class definition time). Trade-off is acceptable.

---

## ADR-008: ChatAnthropic as LLM Provider

**Status:** Abandoned

**Context:** LangChain's `ChatAnthropic` was planned as the LLM provider for the autonomous agent layer. Discovered that the Max subscription is separate from API console billing.

**Decision:** Abandoned. Claude Code skills provide the LLM interaction layer without requiring a separate API key or LangChain dependency.

**Rationale:**

- Claude Code sessions handle all workflow phases effectively
- No separate API billing needed
- Skills-first approach proved sufficient — the agent layer was unnecessary
- Fewer dependencies, simpler architecture

---

## ADR-009: Claude Code Skills as Primary Workflow Interface

**Status:** Accepted

**Context:** The workflow has distinct phases (analyze, apply, outreach, track) that benefit from structured prompts. Options: free-form prompts with CLAUDE.md instructions, CLI-only workflow, Claude Code project skills.

**Decision:** Create project-level Claude Code skills in `.claude/skills/` for each workflow phase.

**Rationale:**
- Skills are discoverable as slash commands in Claude Code sessions
- Each skill encodes domain-specific instructions, reducing prompt engineering per session
- Skills reference shared context (CONTEXT.md, and since ADR-011 the `workflow` skill) without duplicating content
- Works in both Claude Code CLI and Cowork environments
- Skills + CLI provide two complementary interfaces: conversational and programmatic

**Consequences:** Skills are Claude Code-specific. Users of other AI coding tools would rely on CLAUDE.md and WORKFLOW.md directly. Skills need updating when workflow changes.

---

## ADR-010: Obsidian Markdown Replaces Notion

**Status:** Superseded by ADR-013

**Context:** The Notion backend needed an API key, a write queue, and a launchd agent. Writes failed silently when the agent stopped. Claude could not read Notion pages without an extra API call.

**Decision:** Store all tracker data as Markdown files in an Obsidian vault: one hub file per company, one file per interview, and one kanban board file. Delete the Notion backend, the queue, and the sync script.

**Consequences:**
- No API keys, no network, no background process.
- Claude reads and edits the data with normal file tools, and with `jobbing get` / `jobbing set`.
- The board and the hubs can disagree. `jobbing track validate` and `jobbing track sync` repair this.

---

## ADR-011: Private Workspace, Shareable Repository, Installable Skills

**Status:** Accepted (2026-10-05)

**Context:** The repository held one person's CV, board, and personal rules inside the skills. A second user could not use it without editing every skill.

**Decision:**
- All personal local data lives in the workspace: `CONTEXT.md`, `BOOKMARKS.md`, `applications/`, `scan_results/` (originally `kanban/`; see ADR-013). Git ignores all of it. `jobbing init` creates it from templates in the package.
- The skills are generic. Personal rules ("Hard Rules", "Scoring Preferences", "Cover Letter Plan", "CV Location Lines") are sections of `CONTEXT.md`.
- The shared rules are in the `workflow` skill, not in `CLAUDE.md` or `WORKFLOW.md`. Plugin installs do not load `CLAUDE.md`, so each skill loads the `workflow` skill.
- The repository is also a Claude Code plugin marketplace (`.claude-plugin/`). The plugin points at `.claude/skills/`, so one copy of the skills serves both modes.
- `JOBBING_HOME` selects the workspace. The default is the repository root.

**Consequences:** A clone-and-run user and a plugin user get the same skills. Agent docs use ASD-STE100 Simplified Technical English.

---

## ADR-012: Playwright Is an Optional Extra

**Status:** Accepted

**Context:** Playwright needs compiled extensions and a Chromium download. Some sandboxes (Cowork) cannot run it.

**Decision:** Install it with `pip install -e ".[browser]"`. `jobbing browse` and `jobbing scan fetch` fail with a clear message when it is missing. All other commands work without it.

---

## ADR-013: Notion Through Claude's Connector

**Status:** Accepted (2026-10-05). Supersedes ADR-010.

**Context:** The Obsidian tracker (ADR-010) worked, but most users already use Notion and find a Markdown vault too technical. The first Notion backend (ADR-002) failed for a different reason: it called the Notion API from Python with a stored key, a write queue, and a launchd agent, and writes failed silently when the agent stopped.

**Decision:** Track applications in the user's Notion workspace, and reach Notion only through Claude's Notion connector (MCP), from the skills.
- The `setup` skill creates a "Job Search" page with a "Job Tracker" database (board view grouped by Status), an "Interviews" database (two-way relation to companies, calendar view), and a "Comparisons" page.
- The workspace `.env` stores the three URLs (`jobbing notion`).
- The CLI keeps only local work: `init`, `home`, `example`, `notion`, `pdf`, `browse`, `scan`. The tracker commands (`track`, `get`, `set`, `scan existing`) and the Obsidian/JSON tracker backends are deleted.
- Final PDFs are uploaded to the company page with the connector's file upload tool.

**Consequences:**
- No API key in the repository and no background process. Authentication is the connector's OAuth sign-in, which the user manages in Claude.
- The Notion operations are skill instructions, not tested code. They are verified by running `setup` and one full application against a real workspace.
- The skills depend on the connector's tool names (`notion-fetch`, `notion-create-pages`, `notion-update-page`, `notion-query-data-sources`, `notion-create-database`, `notion-create-view`, `notion-create-file-upload`).
- Free Notion plans limit SQL queries, so the skills use the connector's `rows` query mode.

