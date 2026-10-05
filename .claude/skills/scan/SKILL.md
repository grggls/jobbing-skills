---
name: scan
description: Scan the job boards in BOOKMARKS.md for postings that fit the user. Python fetches the pages; Claude extracts and scores the postings in the conversation. No API key needed.
---

# Scan Job Boards

Use this skill when the user asks you to find new jobs on their boards.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Load the scoring skill.
3. Read `CONTEXT.md` if you did not read it in this session.

## Procedure

### Step 1: Get the tracked companies

Query the tracker with `mode: "rows"` and no filter. Keep the list of
`Company` values. Do not show jobs from companies in this list.

### Step 2: Fetch the boards

1. Run `jobbing scan bookmarks`. Show the categories to the user.
2. Ask which categories to scan. The default is all.
3. Fetch:

```bash
jobbing scan fetch                                  # all boards
jobbing scan fetch --categories "Startups" "Remote" # some categories
jobbing scan fetch --limit 5                        # quick test
```

The command writes `scan_results/{YYYYMMDD_HHMMSS}_fetch.json`. If
`BOOKMARKS.md` has no links, tell the user to add links to it.

### Step 3: Find the jobs

Read the results file. For each board:

1. Find job postings whose titles match "Target Roles" in `CONTEXT.md`.
2. Remove:
   - companies from Step 1
   - jobs that are clearly outside "Target Roles"
   - companies in "Hard exclusions"
3. Do not remove a job only because of its title. Read the scope. A
   "Senior" job that builds a new function can match a "Lead" target.
4. If two boards show the same company and role, keep one result.
5. If a board shows only boilerplate and no jobs, write "no listings" for it.

### Step 4: Score the jobs

1. For each job that remains, get the JD with `jobbing browse URL`.
2. Score it with the scoring skill.

### Step 5: Show the results

Show:

- the number of boards scanned and the number of jobs found
- matches (score 60 or more): title, company, score, reason, URL
- near misses (40–59): title, company, score, one-line reason
- the number of skipped jobs (less than 40)

Most boards have zero to two good jobs. If there are no matches, say so. Do
not add weak jobs to make the list longer.

### Step 6: Next step

For each job that the user wants, use the `analyze` skill. Do not create
company pages from this skill.

## Do not

- Do not call the Anthropic API. You do the extraction and scoring.
- Do not use WebFetch for job boards. Use `jobbing browse` or
  `jobbing scan fetch`.
- Do not say that a page is not available before you try `jobbing browse`.
