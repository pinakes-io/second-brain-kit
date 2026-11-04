# AGENTS.md

Rules for people and coding agents who **work on this repository**. If you are an assistant helping a person to set up their second brain, do not use this file: read `START_HERE.md`.

## What this repository is

A kit of text files (instructions, skills, templates) and small checking scripts. `en/` is the English pack (source language), `de/` the German pack with the same structure. `tools/` holds the checks and the ZIP builder. Tool and file names are German for historical reasons.

## Rules

- No real personal data. Test people are invented. No keys, tokens or passwords. No copyrighted text from books, articles or other prompt collections.
- Change both packs, or say why only one. Question IDs, module IDs and field IDs stay identical.
- One skill is one folder with one `SKILL.md`. Everything the skill needs stands in that file.
- Skill names: lowercase letters, digits and hyphens, at most 64 characters, equal to the folder name, never "anthropic" or "claude". Descriptions: at most 1,024 characters, no angle brackets, written in the third person.
- Do not describe a draft as tested. Say what ran in a real account and what only passed the checks.
- Do not push and do not publish. Prepare changes for review.

## Checks to run before you finish

```text
python3 tools/spec_pruefen.py en/spec
python3 tools/spec_pruefen.py de/spec
python3 tools/skelett.py pruefen en
python3 tools/skelett.py pruefen de
python3 tools/plain_prose_pruefen.py skills en
python3 tools/plain_prose_pruefen.py skills de
python3 tools/lang_parity.py pruefen de en
python3 tools/zip_bauen.py en
python3 tools/zip_bauen.py de
```

## Where things are

- Modules: `<pack>/spec/module/*.yaml` (the table in `Feldkarte.md` is generated from them)
- Interview questions: `<pack>/spec/Fragen_Stufe1.yaml`, `Fragen_Stufe2.yaml`
- Core instructions and the three core skills: `<pack>/skeleton/`
- Other skills: `<pack>/skills/`
- Built ZIPs: `<pack>/dist/` (rebuild with `tools/zip_bauen.py`)
