---
name: fact-check
description: Checks numbers, deadlines, amounts, requirements and rules against current official sources before I pass them on, apply for something or decide on them. Use for "check that", "is that still true", "fact check" and always before you state a number or rule in a consequential answer.
---

# Fact check (draft 0.1)

## Goal
No number and no rule leaves the system unchecked. A fluent sentence is not proof. Every statement has a source, a retrieval date and a status.

## Procedure
1. First read (skip only without a Drive connection) the `Fact-Ledger` and look for the statement there.
2. If it is there with status ✔ verified and younger than 90 days, use it and name source and date.
3. Otherwise (no entry, older than 90 days, ⚠ unchecked, 📎 hint source, ❓ unknown) search the web. Order of sources: statutes and official portals, then the official page of the responsible body (in the profile under the responsible bodies, if entered), then specialist portals. Blogs and forums are only hints, never the sole source.
4. In the answer separate "Certain (source, date)" from "Assumed or still to clarify". Invent nothing. If sources contradict each other, name both and do not smooth it over.
5. Enter the result in the `Fact-Ledger`: ID · statement · source with retrieval date · as of · status · meaning for me. Conflicts get their own section "Conflicts". Without write access, output an update block and say that I have to enter it myself.
6. Answer with the result in one to three sentences, then the source with a link. Put it in your own words, no long literal quotes.
7. Counter-check: does this apply to my case? Read `01_Profile` for it. Say explicitly whether it fits, does not fit or whether details are missing (then name them).

## Rules
- For benefits, funding and permits the sentence belongs in: the responsible body decides case by case.
- Numbers and rules from documents I give you (PDF, letter, mail) stay unchecked until a source confirms them.
- Only the source counts, not your memory. If you find nothing, write ❓ unknown, not a guess.
- If I say "skip", the check is dropped without discussion, but the statement stays ⚠ unchecked. Do not ask again in this session.
- Check line at the start: `🔎 Read: Fact-Ledger ✓ · official sources ✓ · 📝 Filed: Fact-Ledger`. If a step is missing, write ✗ and the reason.
