---
name: outreach
description: Find LinkedIn contacts at a company after the user applies (hiring manager, recruiter, peers) and write a tailored connection request (under 300 characters) for each. Saves them to the company's Notion page after approval.
---

# LinkedIn Outreach

Use this skill after the user applies to a company, or when the user asks for
contacts at a company.

## Before you start

1. Load the workflow skill. Obey its rules. Do its section 2 steps if you did
   not do them in this session.
2. Find and fetch the company page. Read the position, the JD, the research,
   and "Experience to Highlight".
3. If the company has no page, tell the user. Offer to run `analyze`.

## Procedure

### Step 1: Find contacts

Use web search (for example `site:linkedin.com/in "{Company}" "{title}"`).
Find:

- **Hiring manager**: the probable manager of the role
- **Recruiter**: a technical recruiter or talent acquisition person
- **Peers**: one or two people on the team of the role

### Step 2: Record each contact

For each contact, record:

1. **Name** and **title**
2. **LinkedIn URL**: only a URL that you found. If you did not find it, write
   "not found".
3. **Note**: why this person is a good contact. Their background, their team,
   and any connection to the user that you can confirm.
4. **Message**: a connection request (see Step 3)

### Step 3: Write the messages

Rules for each message:

- Count the characters. Keep it under 300 (the LinkedIn limit).
- Name the company. Do not make the reader guess it.
- Name the role that the user applied for.
- Give one or two facts from `CONTEXT.md` that matter to this person.
- Change the angle for each type of contact:
  - managers: the user's experience in their area
  - recruiters: a short summary of experience
  - peers: a shared interest or technology
- End with a question or interest in their work. Do not end with "Happy to
  connect" or "Would welcome a conversation".
- Write like a peer, not like a candidate who sells.
- Obey the writing rules in the workflow skill. Do not use em dashes.

### Step 4: CHECKPOINT

Show the contacts and the messages, with the character count for each
message. Wait for the user to approve or change them.

### Step 5: Save to the company page

Write the approved contacts to the `## Outreach Contacts` section of the
company page with `notion-update-page` (`command: "update_content"`). Use
this format:

```markdown
- **Jane Smith** — VP Engineering · [LinkedIn](https://www.linkedin.com/in/janesmith)
  - Note: Leads the platform org. Was an SRE at Google before.
  - Message: "Hi Jane, I applied for the Platform Lead role at Acme. ..."
```

The user sends the messages. You do not send them.

## Do not

- Do not invent profile URLs, mutual connections, or shared interests.
- Do not use one message for all contacts.
- Do not put the full CV in a message. Use one or two facts.
- Do not write to Notion before the user approves.
