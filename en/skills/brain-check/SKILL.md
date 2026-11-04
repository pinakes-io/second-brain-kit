---
name: brain-check
description: Checks the second brain for order and proposes repairs. Use when I write "tidy up", "check the structure", "brain-check" or "it is a mess", or when documents are missing or duplicated. Reads first, changes only after my yes and never deletes.
---

# Brain check (draft 0.1)

## Goal
On request, check the state and, when things have got out of hand, bring them back in order with my agreement. You read first, you propose, I decide.

## Check (read only)
Read `00_Status` (version stamp, active modules, filing map, area rules, limits) and list the folder "Second Brain". Report each point as ✓, ⚠ or ✗:
1. **Target against actual:** Is a document from the filing map or the version stamp missing? Then setup-brain creates it.
2. **Duplicates:** Titles with "Copy of", "_old", "_new", "(1)" or two documents with the same title.
3. **Outside the map:** Documents in the folder without an entry in the filing map, or documents of an area in the wrong place.
4. **Area rules:** Is the block of every active module in `00_Status`? Is the section missing?
5. **Inbox:** Lines older than 14 days without ✔. Then weekly-review fits.
6. **Profile:** Values outside the fixed lists (status, source), version numbers per document, required questions open for a long time.
7. **Fact-Ledger:** Entries on money, deadlines or rules older than 90 days. Then fact-check fits.
8. **Freshness:** `Journal` very long (over about 150 lines: suggest the monthly condensing into the `Archive`), "Last update" in `00_Status` older than 60 days.
9. **Own areas:** Does one resemble a template module (work, learning, …)? Then suggest switching.
You see only what the connection delivers. What you could not check stands as ✗ with the reason.

## Report
At most ten lines: one symbol and one sentence per point. Below it the **repair proposals** as a numbered list, at most five, each with what, where and effect. Ask exactly once: "Which shall I carry out? (numbers, all, none)".

## Repair (only after a yes, per number)
- Allowed: create missing documents (setup-brain), mark lines in the `Inbox` with ✔ and the target, add missing area rules, bring values in the profile onto the fixed lists (the old value stays in the `Journal`), condense journal sections and put the original into the `Archive`, move a duplicate into the `Archive`.
- For duplicates: name both titles, compare the contents and show the difference, then ask per file. Never merge without showing both versions.
- Never: delete, share, change permissions, work outside the folder.
- Read back after every change. Write in `Journal`: "brain-check <date>: <what was changed>". Without write access output a block: "Insert into document X under section Y: …".

## Rules
- If I say "check only" or "skip", change nothing.
- Invent no findings. What you did not read is ✗.
- If you come across a document with ID, account, tax or insurance numbers, report only "sensitive document" without its content and do not touch it.
- Check line: `🔎 Read: 00_Status ✓ · folder ✓ · Inbox ✓ · 📝 Filed: Journal`. If a step is missing, write ✗ and the reason.
