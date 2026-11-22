---
name: paper-brief
description: Write a structured one-page brief of a research paper and save it to notes/. Use when the user asks to brief, summarize, or take reading notes on a paper or an arXiv id.
---

# Paper brief

1. Fetch the paper with the arxiv `get_abstract` tool, never from memory.
2. Fill in [template.md](template.md) exactly: same headings, same order.
3. Save it as `notes/<arxiv-id>.md`, then reply with the path and the claim.

## Rules

- **Claim** is one sentence with no hedging words.
- **Open doubts** lists at least two things the abstract does not establish.
- Stay under 200 words. Where the abstract is silent, write "not stated".
