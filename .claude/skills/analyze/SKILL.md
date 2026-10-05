---
name: analyze
description: Analyze one job posting for fit against the user's CONTEXT.md. Gives a 0-100 score, green and red flags, gaps, a salary read, company research, and draft "Experience to Highlight" bullets. Always the first step before apply. Use when the user pastes a job posting or a job URL.
---

# Analyze a Job Posting

Use this skill when the user gives you a job posting or a job URL. It is
always the first step before `apply`.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Load the scoring skill.
3. Read `CONTEXT.md` if you did not read it in this session.

## Procedure

### Step 1: Get the JD

1. If the user gave a URL, run `jobbing browse URL`.
2. If that fails, follow section 11 of the workflow skill.
3. Query the tracker for the company (workflow skill, section 8). If it has
   a page, tell the user. Ask if they want a new analysis.

### Step 2: Research the company

Use web search. Find these facts and give the source of each:

- funding stage and amount, and the date
- headcount
- news from the last 6 months (layoffs, funding, acquisitions, changes in
  direction)
- employee reviews (for example Glassdoor), with the rating
- the tech stack or tools, from the JD, the company blog, or GitHub

If you cannot find a fact, write "not found". Do not use vague words such as
"well-funded". Give the number.

### Step 3: Score the job

Use the scoring skill. Give the points for each component.

### Step 4: Show the analysis

Show these items to the user:

- **Fit:** underqualified, a good match, or overqualified
- **Score:** 0–100, with the points for each component
- **Green flags:** each with the role or achievement from `CONTEXT.md`
- **Red flags:** about the job, the company, or the posting
- **Gaps:** requirements the user does not have or has only a little
- **Missing keywords:** JD terms to use in the CV
- **Location line:** the line from "CV Location Lines" in `CONTEXT.md`
- **Salary:** the posted range, or a researched estimate (say that it is an
  estimate). Compare it with the floor in `CONTEXT.md`.
- **Company research:** the facts from Step 2
- **Experience to Highlight:** 4–8 draft bullets (see Step 5)

### Step 5: Draft the "Experience to Highlight" bullets

1. Select the roles and achievements from `CONTEXT.md` that match the JD.
2. Write each bullet with a real fact or number from `CONTEXT.md`.
3. Make sure that the domain experience is described correctly.
4. Make sure that each technical claim is correct.

### Step 6: CHECKPOINT

1. Show the analysis and the bullets.
2. Ask the user to correct the bullets and to decide: "go" or "skip".
3. Stop. Wait for the answer.

### Step 7: After the decision

- If the user says "skip", stop. Do not create files.
- If the user says "go", use the `apply` skill. Keep the score, the flags,
  the gaps, the keywords, the research, the JD, and the approved bullets.
  `apply` writes them to the company page in Notion.

## Do not

- Do not make the score higher to encourage the user.
- Do not score from the title and company name only.
- Do not write bullets that claim more than `CONTEXT.md` supports.
- Do not start `apply` without a clear "go" from the user.
- Do not give a positive analysis for a company in "Hard exclusions".
- Do not present a language skill as a qualification if `CONTEXT.md` gives a
  low level for it. Write it as a gap if the JD needs that language.
