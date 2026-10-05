---
name: prep
description: Prepare the user for a scheduled interview. Researches the interviewer, writes likely questions with answer guidance, talking points, and questions to ask. Creates a page in the Notion Interviews database linked to the company.
---

# Interview Prep

Use this skill when the user has an interview. Example: "I have a technical
screen with Jane Smith at Acme on Thursday."

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Find and fetch the company page. Read: Position, Score, Fit Assessment,
   Experience to Highlight, Company Research, Job Description, Questions I
   Might Get Asked, Questions to Ask, and the `Interviews` relation.
3. If the company has no page, stop. Tell the user to run `analyze` and
   `apply` first.
4. Fetch the earlier interview pages for this company, if there are any.

## Procedure

### Step 1: Get the interview data

Get these four items from the user's message:

- **Company**: must match a company page
- **Interviewer**: name and title
- **Date**: change relative dates ("Thursday") to `YYYY-MM-DD`. Use today's
  date from the system.
- **Type**: one of Phone Screen, Technical, System Design, Behavioral, Panel,
  Hiring Manager, Executive, Take-Home

If an item is not clear, ask the user.

### Step 2: Research the interviewer

Use web search. Find their current role, time at the company, career
history, talks, articles, and open-source work. Find real points of
connection with `CONTEXT.md`.

If you find nothing, write "No public profile found". Then prepare from the
role only. Do not invent facts.

### Step 3: Write the prep

Write four sections. Make each one specific to this company, role, and
interviewer.

**1. Interviewer background**

- who they are and what they care about
- connection points with the user's experience

**2. Likely questions**, with answer guidance from `CONTEXT.md` and
"Experience to Highlight". Use the type of interview:

- Phone Screen: motivation, career story, salary expectations
- Technical: architecture decisions, debugging stories, stack details
- System Design: scale, trade-offs, real systems the user built
- Behavioral: leadership, conflict, hiring, work across teams
- Panel: a mix, matched to each panelist
- Hiring Manager: team vision, expectations, management approach
- Executive: strategy, business impact, organization
- Take-Home: questions to clarify scope, documentation approach

**3. Talking points**: stories from `CONTEXT.md` and "Interview Stories",
each with a real number.

**4. Questions to ask this interviewer**: 5–8 questions.

1. Start from the company page's `Questions to Ask` section.
2. Keep only the questions that this person can answer.
3. Add questions for this person, from your research.

### Step 4: Apply the senior interview checklist

Use this checklist when "Target Roles" in `CONTEXT.md` is senior, staff,
principal, lead, or management. Senior candidates often fail on these four
items.

1. **Measured impact.** Each story has a real business number (revenue, cost,
   latency, speed of delivery). If a story has no number in `CONTEXT.md`,
   flag it. The user can find the number or use a different story.
2. **Architecture decisions.** At least one real decision: the options, the
   trade-offs, how the user got agreement, and the long-term risks.
3. **Root cause.** Each incident story has the investigation steps and the
   change that stopped the problem from occurring again.
4. **Clear communication.** Each answer takes less than 4 minutes. Use the
   STAR structure (Situation, Task, Action, Result). Flag stories that can
   become too long.

Put the checklist, with a result for each item, at the end of the prep.

### Step 5: CHECKPOINT

Show the full prep. Wait for the user to correct or approve it. Do not write
files before approval.

### Step 6: Write to Notion

1. Create the interview page with `notion-create-pages`. Use the interviews
   data source as parent. Properties:
   - `Interview`: `{Interviewer} — {Type}`
   - `Company`: an array with the company page URL
   - `Interviewer`, `Interviewer Role`, `Type`
   - `date:Date:start`: the interview date, `date:Date:is_datetime`: 0
   - `Outcome`: `Pending`
   - Leave `Vibe` empty.
2. Body: `## Prep Notes` with the approved prep, then empty `## Debrief` and
   `## Raw Notes` sections.
3. If the company page's `## Questions I Might Get Asked` section is empty,
   write the likely questions to it. If it has content, do not change it.
4. Give the user the link to the interview page.

## Do not

- Do not write generic prep that fits any company.
- Do not use the same questions for each type of interview.
- Do not invent facts about the interviewer or mutual connections.
- Do not use numbers that are not in `CONTEXT.md`.
