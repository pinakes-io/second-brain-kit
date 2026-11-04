# Updating

Your second brain lives in your Google Drive. Updating the kit changes the skills and instructions, not your documents.

## Before you update

Open `00_Status` and note the package version in the version stamp. Compare it with the version in the repository (`CHANGELOG.md`).

## Steps

1. **Skills.** Download the new ZIPs from `<pack>/dist/`. In claude.ai open the skills settings, remove the old version of each skill you want to replace and upload the new ZIP. Skill folder name and `name` in the file must match, otherwise the upload fails.
2. **Project instructions.** Compare the project instructions with `<pack>/skeleton/anweisungen/Projekt-Anweisungen.txt`. If the file changed, paste the new text. Keep your own additions.
3. **Area rules.** Ask the assistant to run `setup-brain` again. It creates only what is missing and adds missing area rules to `00_Status` without changing existing text.
4. **Check.** Ask for `brain-check`. It reads first and proposes repairs; nothing changes without your yes.
5. **Version stamp.** Ask the assistant to set the package version and "last update" in `00_Status`, and to add a line to the `Journal`.

## What never changes

Your profile, journal, notes and documents. If a new version adds a module, the interview or `setup-brain` offers it; nothing is switched on without your yes.

## If something goes wrong

Keep the old ZIPs until the new ones work. Open an issue without personal data and name the pack, the skill and what happened.
