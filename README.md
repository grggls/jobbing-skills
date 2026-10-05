# Jobbing

Run your job search with Claude. Paste a job posting and Claude tells you
honestly whether it's worth applying, writes a CV and cover letter tailored to
that job, preps you for each interview, and keeps everything on a board in
your Notion.

No API keys, no servers. Your profile and the generated PDFs stay on your
machine; your applications and interview notes live in your own Notion
workspace, which Claude reaches through its Notion connector.

## What it does

| You say | Claude does |
|---|---|
| "Analyze this job: <paste or URL>" | Scores the fit 0–100, lists green and red flags, researches the company, and drafts the experience to lead with. You decide go or skip. |
| "Go" | Adds the company to your Notion board, proposes a tailoring plan, then writes the CV and cover letter PDFs once you approve it and attaches them to the Notion page. |
| "Find contacts at Acme" | Finds the hiring manager, recruiter, and peers, and drafts a LinkedIn note for each. |
| "Scan my job boards" | Fetches the boards in `BOOKMARKS.md` and shows only the postings that fit. |
| "I have an interview with Jane at Acme on Thursday" | Researches Jane, writes likely questions, talking points, and questions to ask, and files it under Interviews in Notion. |
| "Debrief Acme: …" | Turns your rambling notes into a structured record. |
| "Any stale conversations?" / "Compare Acme and Beta" | Follow-up reminders and side-by-side offer comparisons. |

Claude checks every claim against your profile and won't invent numbers. It
also stops for your approval before writing a CV or changing anything on your
board.

## Setup (about 15 minutes)

You need:

- a Mac or Linux machine with git
- [Claude Code](https://claude.com/claude-code)
- a Notion account (the free plan works)

```bash
git clone https://github.com/grggls/jobbing-skills.git ~/jobbing
cd ~/jobbing
scripts/install.sh
```

The script installs the `jobbing` command and a headless browser for reading
job boards, then creates your private files. It's safe to run again. Details
and troubleshooting are in [docs/INSTALL.md](docs/INSTALL.md).

Then:

1. **Connect Notion to Claude.** In the Claude app go to Settings →
   Connectors → Notion and allow access. In Claude Code you can also type
   `/mcp`.
2. **Fill in `CONTEXT.md`.** This is your profile and the single most
   important file: Claude only knows what's in it. The easy way is to start
   `claude` in the folder, paste your CV, and say "fill in CONTEXT.md from
   this". Then read it and fix what's wrong. Use the **Hard Rules** section
   for anything Claude must never get wrong ("I've never managed people",
   "my side project has no revenue").
3. **Edit `BOOKMARKS.md`** with job boards and searches for your field.
4. **Say "set up my Notion tracker".** Claude creates a *Job Search* page
   with a *Job Tracker* board and an *Interviews* calendar.

## Daily use

```bash
cd ~/jobbing
claude
```

Then talk normally: "analyze this job", "go", "I applied", "prep me for
Thursday". The skills also work as slash commands (`/analyze`, `/apply`,
`/prep`, …). You can drag cards between columns in Notion yourself; Claude
reads the board fresh every time.

A typical first session:

1. Paste a job posting. Read the analysis and correct the highlights.
2. Say "go". Approve or tweak the tailoring plan.
3. Open the PDFs in `applications/<Company>/`. Ask for changes until
   they're right. Claude attaches the final versions to the Notion page.
4. Apply on the company's site, then tell Claude "I applied to <Company>".

## Using the skills outside this folder

The repo is also a Claude Code plugin, so you can use the skills from any
directory:

```bash
claude plugin marketplace add grggls/jobbing-skills
claude plugin install jobbing@jobbing
```

You still need `scripts/install.sh` for the `jobbing` command. Set
`JOBBING_HOME` to the folder that holds your `CONTEXT.md` (the clone, by
default). Don't install the plugin if you only work inside the clone, or
you'll see every skill twice.

## Your data

- **In Notion:** companies, statuses, scores, research, outreach contacts,
  interview prep and debriefs, comparisons, and copies of the final PDFs.
- **On your machine** (git-ignored): `CONTEXT.md`, `BOOKMARKS.md`, `.env`,
  `applications/` (the CV/cover-letter JSON and PDFs), and `scan_results/`.
  Back these up yourself.

## More

- [docs/INSTALL.md](docs/INSTALL.md): install steps and troubleshooting
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): how it fits together
- [docs/DECISIONS.md](docs/DECISIONS.md): why it's built this way
- [CLAUDE.md](CLAUDE.md): instructions Claude reads in this repo

Development: `scripts/install.sh --dev`, then `make check`. GPL-3.0.
