---
name: apply
description: Full application workflow after the user approves an analyze result. Creates the company page in the Notion Job Tracker, writes a tailored CV and cover letter JSON, renders the PDFs, uploads them to Notion, and runs an ATS keyword check.
---

# Apply to a Job

Use this skill after `analyze`, when the user says "go".

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Make sure that these items are in this session:
   - the `analyze` result (score, flags, gaps, keywords, research)
   - the JD text
   - the "Experience to Highlight" bullets that the user approved
3. If an item is missing, run `analyze` first.

## Procedure

### Step 1: Create the company page

1. Query the tracker for the company (workflow skill, section 8). If a page
   exists, do not create a second one. Update the existing page.
2. Call `notion-create-pages` with the tracker data source as parent.
   Properties:
   - `Company`: the company name
   - `Position`: the role title
   - `Status`: `Targeted`
   - `Score`: the score (a number)
   - `date:Date:start`: today, `date:Date:is_datetime`: 0
   - `Job Posting`: the URL
   - `Salary`, `Environment`, `Focus`: from the analysis
3. Body: the nine sections of workflow skill section 7.2, with this content:
   - `## Fit Assessment`: use the format below
   - `## Company Research`: the research bullets, each with its source
   - `## Experience to Highlight`: the approved bullets
   - `## Job Description`: the full JD text
   - other sections: empty

```markdown
**Score: 82/100** (Domain 25 · Skills 20 · Scope 17 · Location 12 · Company 8)

Two or three sentences of reasoning.

**Green flags:**
- ...

**Red flags:**
- ...

**Gaps:**
- ...

**Keywords missing:** keyword1, keyword2
```

4. Fetch the new page. Make sure that the properties and sections are
   correct. Give the user the page link.

### Step 2: CHECKPOINT — tailoring plan

Show the plan to the user. Do not write the JSON yet.

**CV plan:**

- **Summary angle:** how the first paragraph shows the role's main needs
- **Roles to emphasize:** which roles get the most space, and why
- **Domain signals:** which experience you show for this domain
- **Keywords:** the JD terms that you will put in the CV
- **Earlier experience:** include it or not, and why
- **Location line:** from "CV Location Lines" in `CONTEXT.md`

**Cover letter plan:**

- **Opening:** how you state the experience and the reason for this role
- **Paragraphs:** which role or achievement goes in each paragraph. Start
  from "Cover Letter Plan" in `CONTEXT.md`.

Stop. Wait for the user to approve or change the plan.

### Step 3: Write the JSON

1. Run `jobbing example`. The output is the template. Use the same keys.
2. Write `applications/{Slug}/{Slug}.json` in the workspace. Create the
   directory if it does not exist.
3. In the `cv` object:
   - Write the summary for this role. Put the approved domain signals in it.
   - Put the most relevant core skills first.
   - Write achievements as "Did X, measured by Y, by doing Z". Use only
     numbers from `CONTEXT.md`.
   - Add role bullets that match the JD. Older roles can use facts from
     "Earlier Experience" in `CONTEXT.md`.
   - Use the missing keywords where they are true.
   - Set `location` to the approved location line.
   - Set `name`, `email`, `linkedin`, `github` from "Profile" in `CONTEXT.md`.
4. In the `cl` object:
   - Follow the approved paragraph plan.
   - Keep the chronology correct. Current roles come first.
   - Use "Dear Hiring Team," or the hiring manager's name.
   - Keep it to one page.
5. Set `companyUpper` to the company name in capital letters.
6. Read the JSON again. Make sure that each item in the approved plan is in
   the JSON. If you said a fact goes in the summary, it must be in the
   summary.

### Step 4: Make the PDFs

```bash
jobbing pdf "{Company}"
```

The output gives the path of each PDF.

### Step 5: ATS check

1. Read the CV PDF with the Read tool. If `pdftotext` is installed, you can
   use `pdftotext {file} -` instead.
2. Make sure that the text extracts cleanly (no broken characters).
3. Count the important JD keywords in the CV text.

### Step 6: Show the result

Show the user:

- the PDF paths and sizes
- the keyword counts
- any concerns about the documents

The user reads the PDFs. To change a document, edit the JSON and run
`jobbing pdf "{Company}"` again. Use `--cv-only` or `--cl-only` for one
document.

### Step 7: Upload the final PDFs to Notion

When the user approves the PDFs, upload both to the company page. Use the
procedure in section 10 of the workflow skill. If you upload a new version
later, replace the old file in `## Documents`.

### Step 8: Application questions (if the form has them)

Write the answers in
`applications/{Slug}/{COMPANY}-APPLICATION-ANSWERS.md`. Use only facts from
`CONTEXT.md`.

### Step 9: Status

Do not set the status to "Applied". The user applies and then tells you.
Then set `Status` to `Applied` with `notion-update-page`
(`command: "update_properties"`).

## Do not

- Do not write the JSON before the user approves the plan.
- Do not use numbers that are not in `CONTEXT.md`.
- Do not use the same text for two companies.
- Do not write more than one page of cover letter.
- Do not use the phrases that the workflow skill prohibits.
- Do not leave TODO text or placeholders in the JSON.
- Do not say that the JSON contains an item if you did not check it.
