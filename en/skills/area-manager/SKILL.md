---
name: area-manager
description: Adds areas (modules) while the second brain is in use, pauses them or updates their rules. Use when the person writes "new area", "add an area", "pause an area", "update the rules" or "I also want to use …". Changes only additively and after a yes and never deletes.
---

# Area manager (draft 0.1)

## Goal
The second brain grows with me: new areas come in, unused ones rest, rules get better. Every change is additive, happens after a yes, can be repeated and is recorded. You never delete.

## Preparation (silent)
Read `00_Status` (version stamp, field map with status and version, limits, area rules) and list the folder "Second Brain". If `00_Status` is missing, say so and offer setup-brain. Without write access you output every change as a block: "Insert into document X under section Y: …".

## A. Add an area
1. **Clarify:** Which area? Show from the directory below the areas that are not active yet, plus "own area (please name it)". Ask exactly once.
2. **Check:** (a) Limits: you leave out fields and questions with a blocked tag and note them under "Suppressed fields". (b) Skills: name the skills of the area that are not yet in your own skill list. (c) Follow-up offers from the Note column, for example entscheidungen with arbeit.
3. **Show the plan:** documents that will be created, the block, skills I still have to load. Ask exactly once: "Add it like this? (yes / change)".
4. **Create:** After the yes call setup-brain (it creates only what is missing and adds the block). Then enter in `00_Status`: a line in the field map (status active, version, why "added later on <date>"), filing map, active modules, profile version plus 1 (in `00_Status` and `01_Profile`). Write an entry in `Journal`.
5. **Skills:** Name the missing ZIPs one after the other and stop after each: "Stop: tell me when it is loaded."
6. **Questions:** Open required fields of the area become lines in `02_Open_Questions` (section = area). Offer at most three questions now, the rest later.
Own area: only `State_<Name>`, a line in the filing map and the field map and the block "Own areas". If the name resembles an area in the directory, ask whether that one fits instead.

## B. Pause or switch an area back on
1. **Pause:** Set the status "paused" with the date in the field map and add the note "(paused since <date>, do not follow)" to the block in `00_Status`. Documents and skills stay. Say that I can switch the skills off in the settings.
2. **Archive:** Only if I want it, suggest moving the documents of the area into the `Archive`, file by file, after my yes, with read-back.
3. **Switch back on:** Status "active", remove the note, entry in `Journal`. If the version of the block is older than the one in the directory, offer C.

## C. Update rules
1. For every active or paused area compare the version in the field map with the version in the directory.
2. If it differs, show the block from `00_Status` and the new block one below the other and name the differences in two or three lines. Ask per area: "Take it? (yes / no / later)".
3. After "yes": replace the block, enter the new version and ask which own lines in the old block should stay. Put them under the new block with the note "own addition". Write an entry in `Journal`.
4. After "no" or "later" you change nothing and do not ask again in this session.

## Rules
- Only additive and after my yes; one confirmation per plan, not per document.
- Read back after every change. Check line at the top: `🔎 Read: 00_Status ✓ · folder ✓`, at the end: `📝 Filed: 00_Status, Journal, <new documents>`. If a step is missing, write ✗ and the reason.
- No ID, account, tax or insurance numbers.
- If I say "skip" or "just look", change nothing.
- This skill is optional. Without it setup-brain creates the areas during the first setup.

## Directory of areas
| Area | Version | Documents | Skills | Note |
|---|---|---|---|---|
| person | 0.1 | – | none | always on |
| werkzeuge | 0.1 | – | none | always on |
| arbeit | 0.1 | State_Work | none | add-on: transcript-minutes; with arbeit also offer entscheidungen |
| entscheidungen | 0.1 | Decisions | decision-clarify, decision-check | offered together with arbeit |
| familie | 0.1 | State_Family | none | – |
| wissen | 0.1 | Knowledge, 00_Knowledge_Index | knowledge-note | – |
| termine | 0.1 | State_Appointments, Letter_Scans | appointment-prep, letter-explain | – |
| lernen | 0.1 | State_Learning, Learning_Log | none | candidate for a project of its own |
| schreibstil | 0.2 | Style_Profile | plain-prose-de, plain-prose-en | – |
| bauen | 0.1 | Build_Projects | build-router, vibe-pack | workflow skill (n8n) can be added later |
| eigen:<Name> | – | State_<Name> | none | the block "Own areas" |

## Blocks
Write the block word for word into the section "Area rules" of `00_Status`, the heading "## Area …" as "### Area …".
```
## Area Person and situation
- My tone and preferences are in `01_Profile`, sections "How Claude talks to me" and "Rules". Stick to them.
- The limits in `00_Status` come first. You do not ask for or store blocked details.
- Changes to the profile only after my yes, with value, status, source and date.

## Area Tools
- Devices and tools are in `01_Profile`, section Technology. You write directly into the documents on a smartphone too; you output blocks to paste only if Google Docs is not connected.
- If you cannot use a tool (for example Drive is not connected), say so in one line and offer the block mode.

## Area Work and goals
- State, goals and evidence are in `State_Work`. Read it before you advise on work, career or training.
- Details on qualifications, deadlines or requirements go through fact-check. If transcript-minutes is installed, use it for conversation minutes.

## Area Decisions
- If a real decision is pending and a wrong assumption would be costly ("I have to decide", "A or B"), use decision-clarify. If I say "final" or "I have decided", use decision-check, once.
- Pending and taken decisions are in the document Decisions, with the reason. You only add entries after my yes.
- What is imposed from outside (obligation, law) you explain, you do not clarify it.

## Area Family and household
- State and appointments are in `State_Family`. If details of children are blocked, children appear only with appointments (date, time, place) as "child 1", "child 2"; if names are blocked, you write roles ("partner").
- You leave out blocked fields and do not ask for them.

## Area Knowledge and sources
- After research that I will need again later, and when I say "file as knowledge", use knowledge-note: one note per topic in the folder Knowledge, check 00_Knowledge_Index first.
- Numbers, deadlines and rules in it go through fact-check and are also entered in the Fact-Ledger.
- If a note already exists for a topic, read it first, then answer.

## Area Appointments, post and offices
- For a letter or notice, use letter-explain; for an appointment or an invitation, use appointment-prep. After the appointment you enter the result, deadlines and evidence in State_Appointments.
- Deadlines without an appointment go into State_Appointments with a source; numbers go through fact-check. If health is set to “appointments only”, enter only date, time and “appointment” for medical appointments, at most with the town.

## Area Learning
- Learning state and focus are in `State_Learning`, exercises in the `Learning_Log`. Before an exercise ask for time and goal and fit the difficulty to the state.
- After a session you suggest one line for the `Learning_Log` (date, what, how it went) and write it only after my yes.

## Area Writing style
- Edit German texts ("rework", "tighten", "plain prose") with plain-prose-de; English texts with plain-prose-en. You talk to me in English, only the text itself stays in its language.
- Style rules and words are in the Style_Profile. You only add new rules there after my agreement.

## Area Build
- If I want to build something (app, script, workflow), the skill build-router starts first. It hands over to vibe-pack (code) or, if installed, to the workflow skill.
- If a skill is not loaded, say so in one line and stop. Do not build a plan from memory.
- The project state is in the doc Build_Projects. Until acceptance only invented sample data goes into a project, no real data.
- Tool, prior knowledge and kind of data are in the profile, section Build.

## Own areas
- For an own area <Name> the document `State_<Name>` applies: read it first and file state, goals and evidence there.
```
