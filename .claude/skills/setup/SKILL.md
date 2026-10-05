---
name: setup
description: One-time setup of the user's Notion job tracker. Creates the "Job Search" page, the "Job Tracker" database with a board view, the "Interviews" database, and a "Comparisons" page, then saves their URLs with `jobbing notion`. Use when `jobbing notion` reports that Notion is not set up, or when the user asks to set up Jobbing in Notion.
---

# Set Up the Notion Tracker

Do this one time for each user. Other skills need the result.

## Before you start

1. Load the workflow skill. Read sections 7 and 8 (the Notion schema).
2. Run `jobbing notion`. If it shows three URLs, Notion is already set up.
   Tell the user. Stop unless the user wants a new tracker.
3. Make sure that the Notion connector operates: call `notion-search` with
   `query: "Job Search"`. If the result is "unauthorized", stop. Tell the
   user to reconnect Notion (`/mcp` in Claude Code, or Settings →
   Connectors in the Claude app).
4. If the search finds a "Job Search" page or a "Job Tracker" database, show
   them to the user. Ask if you must use them or create new ones.

## Procedure

### Step 1: Create the home page

1. Ask the user where to put the "Job Search" page. The default is a private
   page at the top of their workspace.
2. Call `notion-create-pages`:
   - For the default, use `creation_mode: "draft"` and no parent.
   - For a page that the user names, use `parent: {page_id: ...}`.
   - Title: `Job Search`. Icon: `💼`.
   - Content: one line: "Job search tracker. Managed by the jobbing skills."
3. Keep the page URL and ID.

### Step 2: Create the Job Tracker database

Call `notion-create-database` with `parent: {page_id: <home page ID>}`,
`title: "Job Tracker"`, and this schema:

```sql
CREATE TABLE (
  "Company" TITLE,
  "Position" RICH_TEXT,
  "Status" SELECT('Targeted':gray, 'Applied':blue, 'Followed-Up':purple, 'In Progress (Interviewing)':yellow, 'Done':green),
  "Score" NUMBER,
  "Date" DATE,
  "Job Posting" URL,
  "Salary" RICH_TEXT,
  "Environment" MULTI_SELECT('Remote':blue, 'Hybrid':yellow, 'On-site':gray),
  "Focus" MULTI_SELECT('Other':default),
  "Conclusion" RICH_TEXT
)
```

Keep the database URL and the data source ID from the `<data-source>` tag.

### Step 3: Create the Interviews database

Call `notion-create-database` with the same parent,
`title: "Interviews"`, and this schema. Put the tracker data source ID in
`RELATION`:

```sql
CREATE TABLE (
  "Interview" TITLE,
  "Company" RELATION('<tracker data source ID>', DUAL 'Interviews'),
  "Interviewer" RICH_TEXT,
  "Interviewer Role" RICH_TEXT,
  "Type" SELECT('Phone Screen':gray, 'Technical':blue, 'System Design':purple, 'Behavioral':pink, 'Panel':orange, 'Hiring Manager':yellow, 'Executive':red, 'Take-Home':brown),
  "Date" DATE,
  "Vibe" NUMBER,
  "Outcome" SELECT('Pending':gray, 'Passed':green, 'Rejected':red, 'Withdrawn':brown)
)
```

The `DUAL 'Interviews'` relation adds an "Interviews" property to the
tracker.

### Step 4: Create the views

1. Board view on the tracker. Call `notion-create-view` with:
   - `database_id`: the tracker URL
   - `data_source_id`: the tracker data source ID
   - `type: "board"`, `name: "Board"`
   - `configure: 'GROUP BY "Status"; SHOW "Company", "Position", "Score"'`
2. Calendar view on the interviews database. Call `notion-create-view` with
   `type: "calendar"`, `name: "Calendar"`, and `configure: 'CALENDAR BY "Date"'`.

### Step 5: Create the Comparisons page

Call `notion-create-pages` with `parent: {page_id: <home page ID>}` and title
`Comparisons`.

### Step 6: Save the URLs

```bash
jobbing notion --home "<home page URL>" --tracker "<tracker URL>" --interviews "<interviews URL>"
```

The command writes the URLs to the workspace `.env` file and shows them.

### Step 7: Verify

1. Fetch the tracker. Make sure that it has the properties in section 7.1 of
   the workflow skill, including "Interviews".
2. Fetch the interviews database. Make sure that it has the properties in
   section 7.3.
3. Give the user the link to the "Job Search" page. Tell them to open the
   "Board" view of the tracker.

## If a step fails

- Show the error to the user.
- Do not create a second copy of a page or database that exists. Fetch the
  home page to see what exists, then continue from the step that failed.
- If `notion-create-view` fails, the tracker still operates. Tell the user to
  add a board view in Notion: open the database, select "+ Add view",
  select "Board", group by "Status".
