# style-profile: skill documentation and test guide (draft 0.1)

The skill text is authoritative: `de/skills/style-profile/SKILL.md` (German pack) and `en/skills/style-profile/SKILL.md` (English pack). This page explains purpose, structure, checks and testing. **The skill has been neither tested in claude.ai nor simulated.** Only the checking tool is tested (self-test with good examples and mutations).

## 1. Purpose
From two or three of your own texts the skill derives your writing style profile and, after you agree, files it in the Drive document `Stilprofil`. The skills `plain-prose-de` and `plain-prose-en` read it and follow it before their default rules.

## 2. Design decisions
- Name: `style-profile`.
- Add-on: the interview offers it when the area `schreibstil` is active. It does not count toward the upload budget (`skills_nachruestbar` in the module).
- Privacy: only **derived traits** are stored, no text samples and no whole sentences. Under "Beispieltexte" there is only the note "no text samples stored".
- Default: minimum amount about 250 words; below about 500 words the result counts as provisional. To be measured in the first claude.ai runs.

## 3. Output
Nine lines with fixed labels, each with a confidence in brackets (high, medium, low): `Geltung`, `Anrede`, `Satzlänge`, `Ton`, `Genderform`, `Zeichensetzung`, `Englisch`, `Häufige Wörter`, `Nie benutzt`. Traits without evidence read "not recognisable". "Nie benutzt" lists only what the person said themselves; it cannot be derived from texts.

## 4. Limits written into the skill
Only your own texts count (forwarded mails, quotations, templates and AI drafts do not). No names, places, companies, numbers, or health, child or money details in the profile or the answer. No word sequence from the texts (at most two words in a row). No inferences about the person (age, gender, origin, mood, character). Nothing is deleted: a new line against an old one marks the old one "ersetzt am" (replaced on).

## 5. Files
| Path | Content |
|---|---|
| `de/skills/style-profile/SKILL.md`, `en/skills/style-profile/SKILL.md` | the skill (one file per ZIP) |
| `tools/style_profile_pruefen.py` | checking tool: `skills`, `messen`, `eingaben`, `eval`, `selbsttest` |
| `tools/fixtures/style-profile/eval/faelle.yaml` | six invented cases with expectations |
| `tools/fixtures/style-profile/eval/eingang/<id>/` | the text samples per case (invented; `fremd.txt` is somebody else's text) |
| `tools/fixtures/style-profile/eval/gut/<id>.txt` | hand-written good answers for the self-test |

## 6. Checking
From the repository root, with `python3 -I`:
- `tools/style_profile_pruefen.py skills .`: front matter, length, forbidden words, required lines, consistency with `plain-prose`.
- `tools/style_profile_pruefen.py selbsttest .`: the good examples must pass and every mutation (filing without consent, an inference, wrong sentence length, wrong text count, missing question, a name in the result, a copied word sequence, a foreign text not named, a sentence length despite too little material) must be caught.
- `tools/style_profile_pruefen.py eval . <folder>`: checks real answers `<folder>/<id>.txt`. Sentence length is held against the counted samples (median, 90th percentile, maximum), plus text count, required labels, names, word sequences and inferences. **Limit:** it checks patterns and numbers, not whether a tone is described correctly.
- `tools/style_profile_pruefen.py eingaben . <folder>`: writes the six messages for a run in claude.ai.

## 7. Test in claude.ai (separate test account)
1. Upload `de/dist/style-profile.zip` (or `en/dist/`) into a free test account; add the ZIPs of `plain-prose-de`/`-en` if you want to see the interplay.
2. Send the six messages from `eingaben`, each in a **new conversation**. Do not give consent (the question is the end point of the first turn). No Drive needed.
3. Save the answers as `<id>.txt` and check them with `eval`.
4. **Additionally with your own texts, not in the repository:** paste two or three real texts and check whether the lines are right, whether the skill asks for the kind of text, and whether nothing from the texts appears verbatim in the result. Keep real texts, names and answers out of the repository, commits and external services.
5. With Drive (only in a test Google account): give consent and check that the lines land under "Stilregeln" and "Wörter" in the `Stilprofil`, that "Beispieltexte" carries the note, that the check line `📝 Abgelegt` appears, and that a second round marks the old lines instead of deleting them.
6. Then run a text through `plain-prose-de`: does it follow the lines `Anrede`, `Genderform` and `Satzlänge`?

## 8. Open
- No simulated trial run exists for this skill.
- Whether `plain-prose` uses the lines `Anrede`, `Satzlänge` and `Ton` explicitly is not fixed; the skill only says the style profile takes precedence and names the lines Genderform and Englisch.
- The instruction block of `schreibstil` deliberately does not name `style-profile`: the interview offers it and its description triggers it. That keeps the blocks short and word for word identical in `setup-brain` and `area-manager`.
- English pack: only the structure is checked (`lang_parity.py`), not the content.
