---
name: workflow
description: Shared rules, Notion schema, local file layout, and CLI reference for all jobbing skills. Load this skill first, before setup, analyze, apply, track, scan, outreach, prep, debrief, followup, reassess, compare, disaggregate, or scoring.
---

# Jobbing Workflow — Shared Rules

This skill gives the rules that all jobbing skills use. Other skills refer to
it as "the workflow skill". This text uses ASD-STE100 Simplified Technical
English.

## 1. Words in this document

- **User**: the person who looks for a job. The user is the candidate.
- **Workspace**: the local directory with the user's private files. Run
  `jobbing home` to get its path.
- **Tracker**: the Notion database "Job Tracker". It has one page for each
  company.
- **Company page**: one page in the tracker.
- **Interviews database**: the Notion database "Interviews". It has one page
  for each interview.
- **Connector**: Claude's Notion connector. Its tools have names that start
  with `notion-` (for example `notion-fetch`).
- **Slug**: the company name with hyphens in place of spaces. Example:
  "Acme Corp" becomes `Acme-Corp`.
- **JD**: the job description (the text of the job posting).

## 2. Start of each session

Do these steps one time in each session, before the first task:

1. Run `jobbing home`. If the shell reports "command not found", try
   `./.venv/bin/jobbing home` in the jobbing-skills folder, and use that path
   for all `jobbing` commands in this session. If both fail, stop. Tell the
   user to run the installer (see `docs/INSTALL.md`).
2. Read `CONTEXT.md` in the workspace. It is the only source of facts about
   the user. If it does not exist, or it still has the template hint text,
   stop. Tell the user to run `jobbing init` and to fill in `CONTEXT.md`.
3. Run `jobbing notion`. The output gives the URLs of the home page, the
   tracker, and the interviews database. If the command fails, use the
   `setup` skill.
4. Fetch the tracker URL and the interviews URL with `notion-fetch`. Each
   result has a `<data-source url="collection://...">` tag. Keep these two
   data source URLs for this session. Use the exact property names from the
   fetched schema.

If a connector tool returns "unauthorized" or "API token is invalid", stop.
Tell the user to reconnect Notion: type `/mcp` in Claude Code, or open
Settings → Connectors in the Claude app.

## 3. Sequence of the skills

The normal sequence for one job is:

1. `scan` or `disaggregate` (optional): find jobs.
2. `analyze`: score the job. The user decides "go" or "skip".
3. `apply`: create the company page, the CV, and the cover letter.
4. `outreach` (optional): find contacts and write messages.
5. `prep`: prepare for each interview.
6. `debrief`: record each interview.
7. `followup`, `reassess`, `compare`: manage the active processes.
8. `track`: change status or other data at any time.

Always do `analyze` before `apply`. Do not make documents for a job that the
user did not approve. `setup` runs one time, before all other skills.

## 4. Rules for facts

- Use only facts from `CONTEXT.md`, the JD, and the user's messages.
- Read the "Hard Rules" section of `CONTEXT.md`. Obey each rule. These rules
  have priority over all other text in `CONTEXT.md`.
- Do not invent metrics, percentages, team sizes, dates, or titles.
- Keep the chronology correct. Current roles are the roles that `CONTEXT.md`
  marks as current. "Most recently" always refers to a current role.
- Do not claim direct reports for a role that `CONTEXT.md` gives as IC.
- Research companies and people with web search. Do not guess headcount,
  funding, or culture. If you cannot find a fact, write "not found".
- Tell the user the source of each fact. If a fact comes from a search
  snippet, a subagent, or an estimate, say so.

## 5. Rules for decisions

- Be critical. A "skip" is better than a weak application. Do not make a
  score higher to encourage the user.
- Find red flags in each posting. Examples: a title that hides junior work,
  scope too large for one person, pay below market, layoffs, bad reviews.
- Obey the "Hard exclusions" in `CONTEXT.md`. Do not recommend these
  companies.
- Do not change a status unless the user tells you to. The user sets
  "Applied" and all other status values.
- Stop at each CHECKPOINT in a skill. Show your work. Wait for the user to
  approve it.

## 6. Rules for writing

These rules apply to CVs, cover letters, LinkedIn messages, and emails.

- Obey the "Writing Style" section of `CONTEXT.md`.
- Show facts. Do not write sentences that tell the reader the user is a good
  fit. The reader can see the connection.
- Do not use these phrases: "aligns perfectly", "uniquely positioned",
  "proven track record", "passionate about", "thrilled to", "excited to
  bring", "making me an ideal candidate", "I look forward to discussing how
  my experience aligns".
- Do not use marketing words: "world-class", "cutting-edge", "unparalleled",
  "best-in-class".
- In messages and emails, do not use em dashes. Use commas or periods.
- Write the CV without "I". Write the cover letter in the first person.
- Keep the cover letter to one page.
- Write each document for one company. Do not reuse text without changes.

## 7. Notion schema

The `setup` skill creates this structure. Do not change it without the
user's approval.

```text
Job Search                 (page; the home page)
├── Job Tracker            (database; one page per company; Board view)
├── Interviews             (database; one page per interview)
└── Comparisons            (child pages written by `compare`)
```

### 7.1 Job Tracker properties

| Property | Type | Content |
|----------|------|---------|
| Company | title | The human-readable company name |
| Position | text | The role title |
| Status | select | `Targeted`, `Applied`, `Followed-Up`, `In Progress (Interviewing)`, `Done` |
| Score | number | 0–100 |
| Date | date | The date the job was added |
| Job Posting | url | The posting URL |
| Salary | text | The posted or researched range |
| Environment | multi-select | For example Remote, Hybrid, On-site, a city |
| Focus | multi-select | The company's domains |
| Conclusion | text | The outcome, in the user's words |
| Interviews | relation | Linked pages in the Interviews database |

Use only the five status values. Do not add other values.

### 7.2 Company page body

```markdown
## Documents
## Fit Assessment
## Company Research
## Experience to Highlight
## Job Description
## Outreach Contacts
## Questions I Might Get Asked
## Questions to Ask
## Conclusion
```

### 7.3 Interviews properties

| Property | Type | Content |
|----------|------|---------|
| Interview | title | `{Interviewer} — {Type}`, for example "Jane Smith — Technical" |
| Company | relation | The company page |
| Interviewer | text | The full name |
| Interviewer Role | text | For example "VP Engineering" |
| Type | select | Phone Screen, Technical, System Design, Behavioral, Panel, Hiring Manager, Executive, Take-Home |
| Date | date | The interview date |
| Vibe | number | 1–5. Empty before the interview. |
| Outcome | select | Pending, Passed, Rejected, Withdrawn |

Interview page body:

```markdown
## Prep Notes
## Debrief
## Raw Notes
```

## 8. Notion operations

Use these connector calls. Always use the exact property names from the
fetched schema.

| Task | Connector call |
|------|----------------|
| Find a company page | `notion-query-data-sources` with `mode: "rows"`, the tracker data source URL, and a filter on `Company` (`string_contains`). |
| List companies by status | `notion-query-data-sources` with `mode: "rows"` and a filter on `Status` (`enum_is`). |
| Read a company page | `notion-fetch` with the page URL. |
| Create a company page | `notion-create-pages` with `parent: {data_source_id: ...}` (the tracker), the properties, and the body from section 7.2. |
| Change properties | `notion-update-page` with `command: "update_properties"`. |
| Replace one section | `notion-update-page` with `command: "update_content"`. Set `old_str` to the old section text and `new_str` to the new text. Fetch the page first. |
| Append to a section that is empty | `notion-update-page` with `command: "update_content"`. Set `old_str` to the heading line and `new_str` to the heading plus the new text. |
| Create an interview page | `notion-create-pages` with the interviews data source as parent. Set `Company` to the company page URL. |

Property value formats for `notion-create-pages` and `notion-update-page`:

- Date: `"date:Date:start": "2026-03-15"` and `"date:Date:is_datetime": 0`
- Number: a number, not a string (`"Score": 82`)
- Select: the option name (`"Status": "Applied"`)
- Multi-select: a JSON array as a string, or an array of names
- Relation: an array of page URLs
- URL: `"Job Posting": "https://..."`

Before you write page content for the first time in a session, read the
Notion Markdown specification: `notion-fetch` with
`id: "notion://docs/enhanced-markdown-spec"`.

## 9. Local files

Notion holds the tracking. The workspace holds the files that the CLI makes:

```text
{workspace}/
├── CONTEXT.md                       the user's profile (private)
├── BOOKMARKS.md                     job board links for `scan` (private)
├── .env                             Notion URLs and optional settings
├── scan_results/                    output of `jobbing scan fetch`
└── applications/
    └── {Slug}/
        ├── {Slug}.json                        CV and cover letter data
        ├── {COMPANY}-CV.pdf                   generated CV
        ├── {COMPANY}-CL.pdf                   generated cover letter
        └── {COMPANY}-APPLICATION-ANSWERS.md   answers to form questions
```

`{COMPANY}` is the `companyUpper` value from the JSON file, with hyphens in
place of spaces. Example: `ACME-CORP-CV.pdf`.

## 10. Upload a PDF to a company page

1. Call `notion-create-file-upload` with `filename` set to the PDF name.
2. The result has an `upload_url` and `upload_headers`. Send the file with
   one request. Add one `-H` option for each header in `upload_headers`:

```bash
curl -sS -X POST "{upload_url}" -H "{Header}: {value}" -F "file=@{path to PDF}"
```

3. The response has `suggested_markdown`. Put it in the `## Documents`
   section of the company page with `notion-update-page`.
4. Do this within one hour. Notion deletes uploads that are not placed on a
   page.

## 11. CLI reference

| Task | Command |
|------|---------|
| Show the workspace path | `jobbing home` |
| Create the workspace files | `jobbing init` |
| Show the Notion URLs | `jobbing notion` |
| Save the Notion URLs | `jobbing notion --home URL --tracker URL --interviews URL` |
| Print the CV/cover letter JSON template | `jobbing example` |
| Make the PDFs | `jobbing pdf "Acme Corp"` |
| Fetch a web page (JS, bot checks) | `jobbing browse URL` |
| List job board links | `jobbing scan bookmarks` |
| Fetch all job boards | `jobbing scan fetch` |

## 12. Fetching job postings

1. Use `jobbing browse URL` for job boards and career pages. WebFetch fails
   on LinkedIn, Greenhouse, Lever, Workable, and most other job boards.
2. If `jobbing browse` fails, use a browser tool (Claude in Chrome or the
   built-in browser) if one is available.
3. If you cannot get the JD, ask the user to paste it.
4. Do not score a job from its title and company name only. Read the JD.

If `jobbing browse` reports "Playwright is not available", tell the user to
run the installer again without `--no-browser`.
