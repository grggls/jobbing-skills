---
name: reassess
description: Re-score an application after interviews give new information. Starts from the existing fit assessment, applies debrief notes and the user's input to each scoring component, shows a before/after, and writes the new score after approval.
---

# Reassess the Fit

The first score from `analyze` uses only the job posting. Interviews give new
facts. Use this skill to update the score with those facts. Example:
"Reassess Acme. The team is 3 people, not 8."

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Load the scoring skill.
3. Find and fetch the company page. Read the `Score`, the Fit Assessment,
   Experience to Highlight, Company Research, and the `Interviews` relation.
4. If there is no Fit Assessment, tell the user to run `analyze` first.

## Procedure

### Step 1: Read the interview data

Fetch each linked interview page. Read `## Debrief` and the `Vibe` value.
Find:

- what the role really includes
- what went well and what went badly
- new facts about the team, stack, culture, scope, and pay

### Step 2: Get the user's input

Ask the user what changed, if they did not tell you. Examples:

- team size or structure
- the real tech stack or tools
- scope that is larger or smaller than the posting said
- culture or management signals
- the confirmed salary range
- new red flags (for example, high turnover in the role)
- new green flags (for example, a strong leader)

### Step 3: Calculate the new score

1. Start from the old component points. Do not calculate from zero.
2. Change each component only for a fact from the interviews or the user:
   - Domain fit: did the interviews confirm the domain?
   - Skills match: is the real stack the stack in the posting?
   - Seniority and scope: is the real scope the scope in the posting?
   - Location and remote: did the rules change?
   - Company signals: new facts about leadership, health, money, turnover?
3. Give more weight to facts that two or more sources confirm.
4. Vibe ratings of 1–2 in many interviews are a strong negative signal.
   Ratings of 4–5 in many interviews are a strong positive signal.
5. The user's facts (team size, stack, scope) have priority over the
   posting.

### Step 4: CHECKPOINT

Show the change:

```text
Old score: 72 (analyze, 2026-02-15)
New score: 81 (+9)

Changes:
- Skills match: +5. The stack is GCP and Terraform, closer to CONTEXT.md.
- Company signals: +4. Strong CTO interview. The team seems healthy.
- Seniority and scope: no change.
```

Also show the new green flags, red flags, gaps, and keywords. Wait for the
user to approve.

### Step 5: Write the result

1. Replace the `## Fit Assessment` section with `notion-update-page`
   (`command: "update_content"`). Keep the old score, its date, and the
   list of changes in the new text. This keeps the history on the page.
2. Set the `Score` property to the new score (`command:
   "update_properties"`).

### Step 6: Note large changes

If the score changed by 15 points or more, tell the user:

1. what the first analysis did not see
2. which component changed most
3. if the scoring skill needs a change to prevent this error

## Do not

- Do not write before the user approves.
- Do not change the score without a fact for each change.
- Do not ignore negative facts. A lower score is a valid result.
- Do not add new components. Use the five components of the scoring skill.
