# Changelog

## 0.1.0-draft (2026-11-03)

First public import. Everything here is a draft; only part of it has run in a real account (a walkthrough with the first three core skills, German pack, free plan).

- English and German packs with the same structure and a parity check.
- Core skills: `setup-brain`, `onboarding-interview`, `weekly-review`, `fact-check`, `brain-check`.
- Module skills: `decision-clarify`, `decision-check`, `knowledge-note`, `appointment-prep`, `plain-prose-de`, `plain-prose-en`, `vibe-pack`, `build-router`; optional add-on `transcript-minutes`.
- Eleven modules as data, area rules written to `00_Status`, account text for the personal preferences.
- Checks, ZIP builder and invented test personas.
- `START_HERE.md` for handing the repository link to an assistant (not yet tested).

Added after the first import: `area-manager` (optional add-on) to add, pause and update areas while the second brain is in use; a status and version column in the field map; area rules marked as paused are ignored.

Added after the first import: optional add-on `style-profile` (builds a style profile from your own texts; offered at the end of the interview). Not run in claude.ai yet.

Added later: `docs/` with the skill documentation and test guides for `plain-prose`, `style-profile`, `transcript-minutes` and `vibe-pack`, so you can run the tests in a separate test account yourself.

Added later: the README now separates skills into A (out of the box: core, module skills, add-ons) and B (tailored to you by a short interview, planned and not built).

Added later: a top-level `skills/` directory with an overview and one page per skill (flow diagram, example, limits, test status) and a gates page; `tools/skill_seiten_pruefen.py` generates and checks the fact block of every page.

Added later: the skill check of `vibe-pack` and `transcript-minutes` also covers the English pack (sections, trigger words, template, check line); their self-tests and output checks remain German only. All 18 Mermaid diagrams of the skill pages were rendered once with the Mermaid CLI without errors.

Added later: `appointment-prep` 0.7 (short by default, three knowledge levels, three health levels) and the new module skill `letter-explain` 0.7 (explains letters, deadlines, fraud). Both are simulated only and not run in claude.ai; the English wording is a first translation. Also new: templates in `spec/vorlagen/` and the add-on `skill-tailor` 0.1, which asks three to five questions and builds a tailored copy of a skill as a ZIP; only marked places change, the protective rules stay word for word, and `tools/vorlage_pruefen.py` checks this. Not run in claude.ai yet.

Added later: the setup now asks for the Google Docs and Google Sheets connectors next to Google Drive (Drive finds and reads, Docs and Sheets write); block mode is only the fallback when Docs is not available. `START_HERE.md` asks once whether module skills should be tailored, builds them with the procedure of the new add-on `skill-tailor` where a template exists (step 7a) and falls back to the ready-made ZIPs. `skill-tailor` has its own skill page; the templates are checked in every export. Not run in claude.ai yet.

Fixed after the first walkthrough over the link (free plan, 04.11. to 07.11.): the setup names the module skills of the active areas that are not installed yet (table "Skills per area" in `setup-brain`, checked by `skelett.py`), and the instructions say to name a missing skill instead of guessing; the line "Skills loaded" in `00_Status` is gone because it went stale and Claude trusted it over its own skill list; the journal is declared newest-at-bottom, as it is written; titles drop a name that is still open; the tools block says Claude writes directly into the documents on a smartphone too, block mode only without the Docs connection; things Claude should do or avoid ("I do not work on Mondays") go into the section Rules of the profile.

Fixed after the test of 2026-11-10: `skill-tailor` 0.5 reads the template in code from the file instead of typing it out, so the code check compares against the real template; in the `appointment-prep` template a restricted choice of appointment types now also narrows the trigger sentence of the description; `appointment-prep` and `letter-explain` give deadlines, duties and consequences as fact only with an official source, advice and advocacy portals count as hints.

Fixed after the test of 2026-11-10 (second round): the project instructions say to read `00_Status` from Drive before the first answer in every chat, even if the question seems answerable without Drive, and the skills no longer say "if you may read Drive" but "first, skip only without a Drive connection"; in three tests Claude had skipped reading. The project knowledge stays empty: a copy there had gone stale in a test, so setup, README and START_HERE no longer ask to add documents to it. Where a skill sets a line limit, the instructions ask to count the lines before sending and cut.

Changed after the test of 2026-11-10 (third round): the assistant asks before every entry in the profile, also after "remember this", and shows the line first.

Changed after the drive export of 2026-11-10: when the assistant appends to a document, its text starts with a line break and it reads the end back; in a test one journal entry had been glued to the previous one.

Known gaps: interview stage 2 has one question; the English wording has not been reviewed by a native speaker; most skills have not been run in a real account; the setup takes longer than the 20-minute target in simulation.
