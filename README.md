# jobbing-skills

Run your job search with Claude. Paste a job posting and Claude tells you
honestly whether it's worth applying, writes a CV and cover letter tailored to
that job, preps you for each interview, and keeps everything on a board in
your Notion.

You don't need to be a developer. Setup is one command you paste into
Terminal, then everything happens by talking to Claude.

## What it does

| You say | Claude does |
|---|---|
| "Analyze this job: <paste or URL>" | Scores the fit 0–100, lists green and red flags, researches the company, and drafts the experience to lead with. You decide go or skip. |
| "Go" | Adds the company to your Notion board, proposes a tailoring plan, then writes the CV and cover letter PDFs once you approve it and attaches them to the Notion page. |
| "Find contacts at Acme" | Finds the hiring manager, recruiter, and peers, and drafts a LinkedIn note for each. |
| "Scan my job boards" | Checks the job boards you list and shows only the postings that fit. |
| "I have an interview with Jane at Acme on Thursday" | Researches Jane, writes likely questions, talking points, and questions to ask, and files it under Interviews in Notion. |
| "Debrief Acme: …" | Turns your rambling notes into a structured record. |
| "Any stale conversations?" / "Compare Acme and Beta" | Follow-up reminders and side-by-side offer comparisons. |

Claude checks every claim against your profile and won't invent numbers. It
stops for your approval before writing a CV or changing anything on your
board.

## Install (about 10 minutes, Mac)

You need the [Claude app](https://claude.ai/download) and a Notion account
(the free plan is fine).

1. Open **Terminal** (press ⌘-Space, type "Terminal", press Return).
2. Paste this line and press Return:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/grggls/jobbing-skills/main/install.sh)"
   ```

3. If it asks for a password, type the one you use to log in to your Mac.
   Nothing appears on screen while you type; that's normal. If a window asks
   to install "command line developer tools", click **Install**.

That's it. The installer sets up everything it needs (Homebrew, Python, and
a few tools) and puts jobbing-skills in **Documents → jobbing-skills**. You
never need to edit any settings files. Running the same line again later
updates it.

## Get started

1. **Connect Notion.** In the Claude app, open Settings → Connectors →
   Notion and allow access.
2. **Open the folder in Claude.** In the Claude app, open the **Code** tab
   and choose the folder `Documents/jobbing-skills`.
3. **Tell Claude about yourself.** Say "Help me fill in CONTEXT.md from my
   CV" and paste your CV. Read what it writes and correct anything that's
   wrong. Use the **Hard Rules** section for things Claude must never get
   wrong ("I've never managed people", "my side project has no revenue").
4. **Set up Notion.** Say "Set up my Notion tracker". Claude creates a *Job
   Search* page with a *Job Tracker* board and an *Interviews* calendar.
5. **Add your job boards (optional).** Say "help me edit BOOKMARKS.md for
   my field", or edit the file yourself.

## Daily use

Open the Claude app's Code tab on `Documents/jobbing-skills` and talk
normally: "analyze this job", "go", "I applied", "prep me for Thursday".
You can drag cards between columns in Notion yourself; Claude reads the
board fresh every time.

A typical first session:

1. Paste a job posting. Read the analysis and correct the highlights.
2. Say "go". Approve or tweak the tailoring plan.
3. Open the PDFs in `Documents/jobbing-skills/applications/<Company>/`. Ask
   for changes until they're right. Claude attaches the final versions to
   the Notion page.
4. Apply on the company's site, then tell Claude "I applied to <Company>".

## Your data

- **In Notion:** companies, statuses, scores, research, outreach contacts,
  interview prep and debriefs, comparisons, and copies of the final PDFs.
- **In Documents → jobbing-skills:** your profile (`CONTEXT.md`), job board
  list (`BOOKMARKS.md`), and the CV/cover-letter files in `applications/`.
  These never leave your Mac except through Claude. Back them up the way
  you back up the rest of Documents.

## For developers

- Terminal users can run `cd ~/Documents/jobbing-skills && claude`.
- The repo is also a Claude Code plugin marketplace:
  `claude plugin marketplace add grggls/jobbing-skills`, then
  `claude plugin install jobbing@jobbing-skills`. Set `JOBBING_HOME` to the
  folder that holds your `CONTEXT.md`. Don't install the plugin if you work
  inside the folder, or you'll see every skill twice.
- From a clone: `./install.sh --dev`, then `make check`.

More: [docs/INSTALL.md](docs/INSTALL.md) (install details and
troubleshooting), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md),
[docs/DECISIONS.md](docs/DECISIONS.md), [CLAUDE.md](CLAUDE.md). GPL-3.0.
