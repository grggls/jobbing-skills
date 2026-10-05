---
name: scoring
description: Scoring formula (0-100) for job postings against the user's CONTEXT.md. Used by analyze, scan, disaggregate, and reassess. Edit this skill to change component weights or thresholds.
---

# Scoring Formula

This skill tells you how to score a job from 0 to 100. The `analyze`,
`scan`, `disaggregate`, and `reassess` skills use it.

The formula is general. The user's preferences come from the "Scoring
Preferences", "Target Roles", "Compensation", and "Location and Remote"
sections of `CONTEXT.md`. Read those sections before you score.

## 1. Components

| Component | Points | What to examine |
|-----------|--------|-----------------|
| Domain fit | 0–30 | The company's domain against "Domains that score high" and "Adjacent domains". |
| Skills match | 0–25 | The JD's required skills and stack against "Core stack / skills". |
| Seniority and scope | 0–20 | The real responsibilities against "Target Roles". |
| Location and remote | 0–15 | The job's location rules against "Location and Remote". |
| Company signals | 0–10 | Funding, stage, growth, reviews, layoffs. |

The score is the sum of the five components.

## 2. Rules

### Seniority and title

- Score the scope, not the title. Companies can change the level after they
  meet the user.
- Do not decrease the score for a title that seems too junior if the job has
  one or more of these:
  - leadership of people or of a function
  - a new function ("first hire", "founding team", "build from scratch")
  - work across teams (Product, executives, other departments)
  - budget or vendor responsibility
- Give a large decrease only when the responsibilities are junior.
- A title that is below the user's level is a small yellow flag. Write it in
  the red flags. Do not decrease the score for it alone.
- Do not give much weight to "N years of experience" requirements. A
  difference of ±3 years is acceptable at senior levels.

### Domain and skills

- Give the highest points to domains in "Domains that score high".
- Give medium points to "Adjacent domains".
- Give low points to "Role types that score low".
- Count adjacent tools that transfer directly (for example, one cloud
  provider for another) as a partial match.

### Location

- Use the "Locations that score high" and "Locations that score low" lists.
- A job that needs work authorization the user does not have gets 0–3
  points for location. Write it in the red flags.

### Company

- Write a red flag for bad reviews or recent layoffs. Do not reject the job
  for these alone.
- If the posting has no salary, write it in the red flags. Do not decrease
  the score for it.
- A company in "Hard exclusions" gets no score. Write "Excluded" and the
  reason.

## 3. Thresholds

- **60 or more**: a match. Recommend `analyze` (if not done) and `apply`.
- **40–59**: a near miss. Show it. Let the user decide.
- **Less than 40**: skip.

The user can change the match threshold with `SCORE_THRESHOLD` in the
workspace `.env` file.

## 4. Output

For each job, give:

- `score`: 0–100, and the points for each of the five components
- `reasoning`: two or three sentences
- `green_flags`: strong matches, each with the `CONTEXT.md` fact behind it
- `red_flags`: concerns (a red flag does not always decrease the score)
- `gaps`: requirements that the user does not have, or has only a little
- `keywords_missing`: JD terms to use in the CV if the user applies
