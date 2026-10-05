---
name: track
description: Tracker operations outside the analyze/apply flow. Change a status, close an application with a conclusion, update research, highlights, fit assessment, or outreach contacts, and list or check the companies in the Notion Job Tracker.
---

# Tracker Operations

Use this skill to change tracker data at any time. Examples: "I applied to
Acme", "Acme rejected me", "add this to the Acme research", "what is on my
board?".

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Find the company page (workflow skill, section 8) and fetch it.
3. If the company has no page, tell the user. Offer to run `analyze`.

## Operations

### Change the status

Only change the status when the user tells you to. Call `notion-update-page`
with `command: "update_properties"` and `{"Status": "Applied"}`.

Status values, in sequence: `Targeted`, `Applied`, `Followed-Up`,
`In Progress (Interviewing)`, `Done`. Do not use other values.

The board view moves the card. You do not need to do anything else.

### Close an application

1. Ask the user for the outcome in their own words, if they did not give it.
2. Set `Status` to `Done` and `Conclusion` to a short version of the outcome.
3. Write the full outcome in the `## Conclusion` section of the page.

Do not write a conclusion that the user did not give you.

### Replace a section

Use this for Company Research, Experience to Highlight, Fit Assessment,
Outreach Contacts, Questions I Might Get Asked, and Questions to Ask.

1. Fetch the page and read the section.
2. If the section has content that the change removes, tell the user and get
   approval.
3. Call `notion-update-page` with `command: "update_content"`. Replace the
   old section text with the new text.

For a new score after interviews, use the `reassess` skill. If you change the
score here, also change the `Score` property.

### Show the board

Query the tracker with `mode: "rows"`. Group the rows by `Status`. Show the
company, position, score, and date for each row. Sort each group by score,
highest first.

### Check the data

Query all rows. Report these problems:

- a page without `Status`, `Position`, or `Date`
- a page with `Status` `Done` and no `Conclusion`
- a `Score` property that does not agree with the score in `## Fit
  Assessment`
- two pages for the same company

Do not repair a problem until the user approves the change.

## Rules

- Do not create a second page for a company that has one.
- Do not set `Done` without a conclusion.
- Interview prep and debriefs use the `prep` and `debrief` skills.
