---
name: debrief
description: Record a post-interview debrief. The user gives raw notes; Claude puts them into a structure (questions asked, what went well, what went badly, what they learned, updated view, follow-ups, vibe 1-5) and writes it to the interview page in Notion.
---

# Interview Debrief

Use this skill right after an interview. Example: "Debrief Acme. I just
talked to Jane. It went well, she asked about..."

The full task must take less than five minutes for the user.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Find and fetch the company page. Read the `Status`, the `Score`, and the
   `Interviews` relation.
3. If the company has no page, stop. Tell the user to run `analyze` and
   `apply` first.

## Procedure

### Step 1: Get the interview data

From the user's message, get:

- **Company**
- **Interviewer**: needed if the company has more than one interview page
- **Date**: today, if the user does not give one
- **Raw notes**: the user's thoughts

If the company has many interview pages and the user gives no interviewer,
ask.

### Step 2: Find the interview page

Look in the company's `Interviews` relation for a page with this interviewer
and date. If it exists (from `prep`), fetch it and read `## Prep Notes`.

### Step 3: Put the notes in a structure

Use only what the user told you. If a part is empty, write "Nothing noted".

1. **Questions they asked**, in the user's words. Mark easy questions and
   deep questions.
2. **What went well**: answers that got a good reaction, and topics where
   the interviewer asked more.
3. **What went badly**: questions that surprised the user, and weak answers.
   This is input for the next round.
4. **What I learned**: new facts about the role, team, company, or culture.
   Corrections to earlier assumptions.
5. **Updated view**: did the interview change the user's view of the job? If
   a fact changes the fit, recommend the `reassess` skill. If nothing
   changed, write "No change".
6. **Follow-up**: actions, the expected time of the next step, and people to
   contact.
7. **Vibe** (1–5), from the user:
   - 1: bad signs, probably withdraw
   - 2: not enthusiastic, concerns remain
   - 3: neutral, need more data
   - 4: good conversation, optimistic
   - 5: strong mutual fit

### Step 4: CHECKPOINT

Show the debrief. Wait for the user to correct or approve it.

### Step 5: Write to Notion

- If the interview page exists: write the debrief under `## Debrief` with
  `notion-update-page` (`command: "update_content"`). Set `Vibe` and
  `Outcome` with `command: "update_properties"`. If `## Debrief` already has
  content, ask the user before you replace it.
- If the page does not exist: create it as in Step 6 of the `prep` skill,
  with an empty `## Prep Notes`. Then write the debrief.
- Put the user's raw notes under `## Raw Notes`.

Set `Outcome` to `Pending` unless the user gives the result.

If the company's `Status` is `Applied` or `Followed-Up`, ask the user if it
must change to `In Progress (Interviewing)`. Change it only if they agree.

### Panel interviews

- Separate conversations with different people: one page for each person.
- One conversation with many people: one page. Set `Interviewer` to all
  names, for example "Jane Smith + Sam Lee".

## Do not

- Do not add facts that the user did not give.
- Do not change the vibe rating that the user gives.
- Do not describe the interviewer's reactions unless the user described
  them.
- Do not set an outcome other than "Pending" unless the user gives it.
