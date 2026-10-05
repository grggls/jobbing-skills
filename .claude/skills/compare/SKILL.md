---
name: compare
description: Side-by-side comparison of two or more active opportunities on weighted dimensions (compensation, fit, team, mission, growth, location, risk). Reads the Notion company and interview pages. Writes only one comparison page under Job Search → Comparisons.
---

# Compare Opportunities

Use this skill when the user must choose between two or more jobs, for
example when offers overlap. Example: "Compare Acme and Beta" or "compare my
active ones".

This skill does not change company or interview pages. It writes one
comparison page.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Read the "Compensation", "Target Roles", "Location and Remote", and
   "Scoring Preferences" sections of `CONTEXT.md`.

## Procedure

### Step 1: Select the companies

- Use the companies that the user names.
- For "my active ones", query the tracker for `Status` =
  `In Progress (Interviewing)`.

### Step 2: Collect the data

For each company:

1. Fetch the company page. Use the properties (Salary, Environment, Focus,
   Score) and the sections (Fit Assessment, Company Research, Outreach
   Contacts).
2. Fetch each page in its `Interviews` relation. Use `Vibe`, `Outcome`,
   `Type`, `Date`, and `## Debrief`.

### Step 3: Rate each dimension

| Dimension | Weight | Evidence |
|-----------|--------|----------|
| Compensation | High | salary, offer details, equity, benefits; compare with the floor in `CONTEXT.md` |
| Fit | High | the current score, the real stack, the debrief notes on the work |
| Team and culture | Medium | the average vibe, interviewer quality, reviews |
| Mission | Medium | `Focus` and the research against the user's preferred domains |
| Growth | Medium | real scope from interviews, company growth, career path |
| Location and remote | Low | `Environment`, time zones, travel, work authorization |
| Risk | Low | red flags, layoffs, money runway, turnover |

Give each dimension one rating: **Strong**, **Good**, **Neutral**,
**Concern**, or **Unknown**. Use "Unknown" when there is no data. Do not use
"Neutral" for missing data.

A salary below the floor in `CONTEXT.md` always gets "Concern" for
compensation. Say this clearly.

### Step 4: Write the comparison

Write three parts:

1. **Summary table**: one row for each dimension, one column for each
   company. Put the main fact in each cell, for example "Strong (€140K)".
   Put a blank line before the table.
2. **Details**: for each dimension, one short paragraph for each company,
   with the evidence and its source page.
3. **Synthesis**: where each company is stronger, the trade-offs, and the
   open questions. Do not choose a winner. The user decides.

### Step 5: Save the page

1. Fetch the home page (`jobbing notion` gives its URL). Find the child page
   "Comparisons".
2. Create a page under it with `notion-create-pages`. Title:
   `{Company 1} vs {Company 2} — {YYYY-MM-DD}`. Body: the three parts.
3. Give the user the link.

### Step 6: Discuss

Show the comparison. The user can change the weights or add facts. Make a new
version if they ask.

## Do not

- Do not change company or interview pages.
- Do not choose a winner.
- Do not guess data. Write "not available".
- Do not give all dimensions the same weight.
