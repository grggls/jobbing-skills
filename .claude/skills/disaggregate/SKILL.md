---
name: disaggregate
description: Parse a batch of aggregator job listings (Jobgether, Lensa, LinkedIn job emails, job digests) that hide the real employer. Removes duplicates, finds the original companies, and gives quick scores. Use when the user pastes many listings or says "got a bunch of job emails".
---

# Disaggregate Aggregator Listings

Aggregators such as Jobgether and Lensa repost one job many times (for
example, one listing for each US state). They hide the real company. Use this
skill to find the real jobs and to score them quickly.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Load the scoring skill.
3. Read `CONTEXT.md` if you did not read it in this session.

## Procedure

### Step 1: Parse the input

For each listing, get: the title, the aggregator, the location, and other
details.

### Step 2: Remove duplicates

This step saves the user the most time. Put listings in one group when:

- the titles are the same with small changes in word order
  ("VP of Engineering, Reliability" and "Engineering VP, Reliability")
- the aggregator, role family, and requirements are the same
- two aggregators show the same requirements

### Step 3: Find the original company

For each group:

1. Search for the title and key requirements without the aggregator name.
   Example: `"VP of Engineering Reliability" -jobgether -lensa`.
2. Look at the aggregator's own offer page. Jobgether pages
   (`jobgether.com/offer/...`) sometimes name the company.
3. Search Greenhouse, Lever, and Ashby job boards for the same posting.
4. If you have a probable company, check its career page.
5. If you cannot find the company, write "not identified". Do not guess.

### Step 4: Score each unique job

1. Get the real JD with `jobbing browse URL`.
2. Score it with the scoring skill.
3. If you have only part of the JD, score what you can. Mark the unknown
   components. Give a low score when you are not sure.

### Step 5: Show the results

Put a blank line before the table.

| # | Listings | Original company | Role | Score | One-line view |
|---|----------|------------------|------|-------|---------------|
| 1 | Jobgether ×6 (FL, CA, MD, VA, MN, NC) | Acme | VP Eng, Reliability | 75 | Strong match, good pay |
| 2 | Lensa ×1 | not identified | Director, Infrastructure | — | Company not found |

### Step 6: Next step

For each job with 60 or more points, offer the `analyze` skill.

## Aggregator patterns

- **Jobgether**: posts on Lever (`jobs.lever.co/jobgether/...`). Makes 5–15
  copies of one job with changed titles.
- **Lensa**: posts on lensa.com. Often removes the company name.
- **Recruiting agencies** (for example Pentasia): post for clients that they
  do not name. They are agencies, not aggregators.
- **LinkedIn**: check if the poster is the real company or an intermediary.

## Do not

- Do not score from the title only. Get the JD.
- Do not do the full `analyze` here. This skill is a quick filter.
- Do not recommend a company in "Hard exclusions".
