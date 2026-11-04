# Contributing

Thank you for helping. This kit is for ordinary people who set up a second brain with claude.ai and Google Drive, so the most useful contributions are small, tested and easy to read.

## Ground rules

- **No real personal data. Ever.** Not in files, issues, pull requests, screenshots or examples. Test people are invented. If you report a problem, blank out names, numbers and addresses first.
- **No copyrighted text.** Do not paste passages from books, articles, courses or other prompt collections. Write in your own words and name the idea, not the source text.
- **No secrets.** No keys, tokens, passwords or account details, also not "just for testing".
- **One skill, one job.** A skill is one `SKILL.md` in its own folder, short and plain. Extra files inside a skill are not reliably available in claude.ai, so everything the skill needs stands in `SKILL.md`.
- **Honest status.** Mark what you ran in a real account and what you only wrote. Do not describe a draft as tested.

## How the repository is organised

`en/` is the English pack and the source language. `de/` is the German pack with the same structure. Question IDs, module IDs and field IDs are the same in both. `tools/` holds the checks and the ZIP builder. Tool and file names are German for historical reasons and will be renamed.

## Before you open a pull request

Change both packs, or say why you changed only one. Then run the checks (Python 3 and PyYAML are needed):

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

The checks test structure and consistency. They cannot tell you whether a skill works in a real account. If you ran it, say in the pull request which plan, which pack and what happened.

## Proposing a new skill or module

Open an issue first with the problem, who needs it and what the person says to start it. A module is described in `spec/module/<id>.yaml` (see `spec/Modul_Vorlage.yaml`): activation, skills, instruction block, Drive documents, filing-map lines. Keep to the upload budget: at most 12 skills per person.

## Language

English is the source. Translations should follow the structure of the English pack. A native-speaker review is welcome and valued, especially for the German pack and for the English wording.

## License

By contributing you agree that your contribution is licensed under the MIT License of this repository.
