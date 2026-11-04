# vibe-pack: test run in a test account (draft)

> Purpose: check whether `vibe-pack` triggers in claude.ai, keeps to its template and produces a pack that passes `tools/pack_pruefen.py`. Inputs come from `docs/vibe-pack/eval/faelle.yaml`, all data invented.
> Test account only (free account, test Google account). Nothing here has been checked in claude.ai yet; fill in the "Result" column yourself.
> Mind the free usage limit: each case needs two to three messages. Go in order of importance, stop at the limit and note where you stopped.

## Preparation
1. Upload `de/dist/vibe-pack.zip` into the test account (Settings > Customize > Skills).
2. **Remove or switch off** every skill named `build-router` and `build-code` in the test account first, including the real `build-router`. Otherwise a router triggers on "build" and distorts this run.
3. New chat in a test project. No Drive needed; `vibe-pack` only reads when Drive is connected.

## Cases, in this order
| No. | Case | Message 1 | Answer to follow-up questions |
|---|---|---|---|
| 1 | `einkaufsliste` | `Ich möchte eine Einkaufsliste bauen, die ich am Handy abhaken kann.` | `Im Browser am Handy, ohne Anmeldung. Läuft auf meinem Rechner, ich baue mit Cursor.` |
| 2 | `kundenliste` | `Ich will eine Liste mit meinen Kundinnen und Kunden und den nächsten Terminen bauen. Mit Name, Telefonnummer, nächstem Termin und einer Notiz zur Behandlung.` | `Nur auf meinem Laptop. Als Beispiel ein Eintrag: Maria Beispiel, 0151 0000000, Dienstag 10 Uhr, Rücken.` |
| 3 | `bestandsskript` | `Mein Skript, das Rechnungen sortiert, geht seit gestern nicht mehr. Ich habe den Ordner umbenannt.` | Only if Claude asks for it, the error message: `FileNotFoundError: [Errno 2] No such file or directory: 'rechnungen/eingang'` |
| 4 | `ki_zusammenfassung` | `Ich will eine App bauen, die lange Rechnungstexte mit KI zusammenfasst. Sie soll lokal laufen.` | `Ein Skript reicht. Das Modell soll möglichst wenig kosten.` |
| 5 | `ablauf_mail_tabelle` | later, with `build-router` installed (needs the router) | |

## What to check per case
| Case | Expected | Result |
|---|---|---|
| all | The skill triggers (name visible in the chat?). At most two rounds with at most three questions each, recommendation first. Dialogue German, pack English. The pack is **one** block with the marker lines `=== AGENTS.md ===` and `=== PLAN.md ===`, and at the end the check line with `🔎 Pack:`. The offer to file build projects in the Doc comes at most once. File name of the rules file: named with its date or marked as unchecked. | |
| 1 | Non-goals name login and hosting. No Docker, no database server. A tracer with expected output. At most five leaf nodes. | |
| 2 | The real-data rule is in the pack. A note that privacy questions must be settled before real use, **without legal advice**. The sample entry (name, number, date) is **not** in the pack. No cloud stack. | |
| 3 | No new pack. Separates confirmed (the path does not exist) from assumed (the rename as the cause). Advises a commit before any change. Proposes the smallest fix with evidence and rewrites nothing completely. Asks for the error message as text if it is missing. | |
| 4 | The AI block stands verbatim under the rules. No framework fixed. The technology justified in one sentence. | |

## After each pack
Paste the pack block into a chat where the repository is available (not into the test account) and check it with the tool:
- Case 1: `python3 -I tools/pack_pruefen.py pack . <file> --fall einkaufsliste`
- Case 2: `--fall kundenliste` (reports a copied phone pattern as suspected real data)
- Case 4: `--fall ki_zusammenfassung`
Case 3 has no pattern search; check it by hand.

## Note down
- Number of messages until the pack; free limit reached? When?
- Characters of AGENTS.md according to the check line (limit 2,000).
- The exact wording of every deviation from the expected, especially: missing markers, a German pack, more than eight rules, placeholders in angle brackets.

## Reading the results
| Result | Consequence |
|---|---|
| Skill does not trigger | Sharpen the description or strengthen the routing in the instruction block. |
| Pack German or without markers | Move the rule "in English" and the marker lines to the front of the skill. |
| Sample data in the pack (case 2) | Move the real-data rule to the start of the section "Das Pack". |
| More than two rounds of questions | Stress the limit in the skill; order the questions by effect. |
| Tool reports placeholders | Tighten the skill's self-check. |
| Return trip (case 3) rewrites everything | Shorten the section "Rücklauf" and put the smallest fix first. |

## After the test
Save the result in `docs/vibe-pack/Ergebnis_Testlauf.md`. Remove the test skills from the test account again.
