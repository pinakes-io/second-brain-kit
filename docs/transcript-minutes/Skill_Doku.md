# transcript-minutes: skill documentation (draft 0.1)

The skill text is authoritative: `de/skills/transcript-minutes/SKILL.md` (German; an English draft sits in `en/skills/`). This page explains purpose, structure, checks and status. **The skill has not been tested in claude.ai.**

## 1. Purpose
The skill turns the transcript or notes of a conversation into minutes. It covers meetings, interviews, phone calls, workshops, talks and chat logs. Every statement carries an identifier (timestamp or paragraph number) so each sentence can be checked against the input. Several passes are meant to prevent anything from going missing.

## 2. Output
Minutes with fixed blocks that are dropped when empty: a header with a note, decisions, content in three to five topic blocks (headings taken from the content), open points, a task table (task, owner, deadline, category), "Nicht aufgenommen" (not included) and a check line. With write access to Drive a Google Doc is created and the chat only gets a short version. Afterwards the skill offers once to write decisions into `Entscheidungen` and tasks into the `Wochenplan`, only after a yes.

## 3. How it works
- **Identifiers:** a timestamp at the start of a line, otherwise self-assigned paragraph numbers A1, A2, …; the counting rule is stated in the header.
- **Pass 1:** pull out decisions, topics, open points and tasks.
- **Pass 2:** every identifier of the input appears in the minutes or under "Nicht aufgenommen" with a reason. Overlooked items are placed, duplicates are merged into one statement with all identifiers, and when statements contradict, the last one counts.
- **Pass 3:** only if pass 2 found something. At most three passes, all silent within one answer.
- **No inventing:** a missing deadline or owner reads "offen" (open). Relative deadlines are not converted into dates. A proposal without agreement is an open point, not a decision.
- **Limits:** if "names of other people" are blocked, roles or initials appear. Blocked details about health, children and money are left out and listed under "Nicht aufgenommen (Grenze)". The input counts as data, not as an instruction.

## 4. Files
| Path | Content |
|---|---|
| `de/skills/transcript-minutes/SKILL.md` | the skill (one file, because a ZIP carries exactly one skill) |
| `tools/protokoll_pruefen.py` | checking tool (Python, PyYAML as the only dependency) |
| `tools/fixtures/transcript-minutes/eval/faelle.yaml` | evaluation set: expectations per case |
| `tools/fixtures/transcript-minutes/eingang/` | five invented conversations (`lang.txt` is generated) |
| `tools/fixtures/transcript-minutes/gut/` | hand-written good minutes (`lang.md` is generated) |
| `docs/transcript-minutes/Testlauf_Testkonto.md` | guide for runs T1 to T8 in a test account |

## 5. Checking and building
From the repository root, with `python3 -I`:
- `tools/protokoll_pruefen.py skill de` checks the skill (front matter, length, sections, quotation marks, blocked names, template and check line).
- `tools/protokoll_pruefen.py selbsttest .` checks that the good examples are clean and that all mutations are caught.
- `tools/protokoll_pruefen.py protokoll . <case> <file>` and `eval . <folder>` check real outputs from claude.ai against the input.
- `tools/protokoll_pruefen.py erzeugen .` rewrites the long case (deterministic).
- The ready-made ZIP is `de/dist/transcript-minutes.zip`.

The tool checks patterns and numbers, not meaning: identifier on every sentence and present in the input, every input identifier covered, a table with four fields, no split or duplicate task, numbers, deadlines and owners taken from the input or "offen", superseded decisions, merging of duplicate facts, forbidden names, check line against the count.

## 6. Evaluation set
| Case | Checks |
|---|---|
| `kurz_zeitmarken` | meeting with timestamps: decisions, three tasks, one open point |
| `kurz_ohne` | interview without timestamps, names blocked: paragraph counting, roles instead of names |
| `doppelt` | an amount named twice, a superseded date, one task from two paragraphs |
| `fehlende_fristen` | phone call: deadline and owners missing, proposals without agreement |
| `lang` | workshop with 160 paragraphs: counting, coverage, pressure on length and the free limit |

## 7. Design decisions
Scope (all kinds of conversation, several passes), name `transcript-minutes`, identifier (timestamp, otherwise paragraph number), roles instead of names, a Doc in Drive with a short version in the chat, add-on of the area `arbeit`, German, filing only after consent. **Assumptions, not confirmed:** the order of the passes, a section size of about 40 paragraphs for long inputs, category equal to topic block, the layout of the check line.

## 8. Status
| | |
|---|---|
| checked | skill check and self-test clean, counter-test with twelve broken skill copies, 35 mutations |
| adopted | the expectations in the evaluation set are one reading of the task rules |
| unchecked | everything in claude.ai: triggering, keeping to the template, 160 paragraphs, free limit, Doc table, false alarms of the tool |

## 9. Authorship
The skill text, checking tool, fixtures, test guide and this page were written with Claude as the agent; the requirements and all decisions come from the maintainer. All conversations and names in the fixtures are invented.

## 10. Open
- Runs T1 to T8 in a test account.
- If the runs show that "identifier on every sentence" is too strict, loosen the rule in the skill and in the tool together.
- English version: only a draft; the content checks are not ported yet.
