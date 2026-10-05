---
name: followup
description: Find stale interview processes. Reads every "In Progress (Interviewing)" company in the Notion Job Tracker and its interview pages, calculates days since the last contact, and suggests follow-up actions. Read-only.
---

# Follow-Up Check

Use this skill when the user asks "any stale conversations?" or "check my
follow-ups". This skill reads data. It does not write to Notion and does not
send messages.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Get the threshold. Default: 5 days. The user can set
   `FOLLOWUP_THRESHOLD_DAYS` in the workspace `.env` file.

## Procedure

### Step 1: Find the active processes

Query the tracker with `mode: "rows"` and a filter: `Status` is
`In Progress (Interviewing)`.

### Step 2: Read the interview data

For each company, fetch each page in its `Interviews` relation. Get `Date`,
`Interviewer`, `Type`, `Outcome`, and the follow-up items in `## Debrief`.

### Step 3: Calculate the staleness

1. The last activity date is the newest interview `Date`. If there are no
   interview pages, use the company `Date`.
2. Days since last activity = today (from the system) minus that date.
3. Put each company in one group:
   - **Needs attention**: more days than the threshold
   - **Recently active**: the threshold or fewer days
   - **No interview data**: status is "In Progress" but there are no
     interview pages
4. An interview with a date in the future is a scheduled next step. Put that
   company in "Recently active" and show the date.

### Step 4: Suggest an action for each stale company

- After a screen: a short check-in with the interviewer about the timeline.
- After a technical round: ask the recruiter about the next round.
- After a hiring-manager talk: a check-in with that person.
- If the newest debrief has open follow-up items, show them.
- If there is no interview data: ask the user to add a debrief, or to change
  the status.

### Step 5: Show the report

Sort by days, most stale first.

```markdown
## Follow-Up Check — 2026-03-10

### Needs attention (2)

**Acme Corp** — 8 days since last contact
  Last: Technical with Jane Smith (2026-03-02)
  Suggested: Ask the recruiter about the timeline for the next round
  Open item: Send the architecture diagram (from the debrief)

### Recently active (1)

**Beta GmbH** — 2 days since last contact
  Last: Hiring Manager with Alice Chen (2026-03-08)

### No interview data (1)

**Gamma Inc** — status is "In Progress" but there are no interview pages
```

If no company is stale, write: "All active processes have recent activity."

### Step 6: Offer actions

Ask if the user wants you to:

- write a follow-up email for a stale company
- change the status of a company
- record a debrief that is missing

Do the action only when the user tells you to.

## Do not

- Do not write to Notion or send messages.
- Do not change a status.
- Do not assume an outcome. "Pending" means pending.
- Do not ignore companies with no interview data.
