# plain-prose-de / plain-prose-en: test guide for claude.ai (draft 0.1)

**Purpose:** check that both skills behave in claude.ai the way they did in simulation. So far they were **only simulated** (two runs with 15 cases) and **not tested in claude.ai**. Run the test in a separate test account, never in your main account.

The test needs **no Drive and no Google account**. The `Stilprofil` document is not read, so the check line `🔎 Gelesen` does not appear (the skill says so). The interplay with a style profile is a separate test (see `docs/style-profile/Skill_Doku.md`).

## 1. Preparation
- Use a free test account.
- Upload the ready-made ZIPs, one skill per ZIP: `de/dist/plain-prose-de.zip` and `de/dist/plain-prose-en.zip` (the English pack has the same skills in `en/dist/`).
- Create the messages: `python3 -I tools/plain_prose_pruefen.py eingaben . /tmp/pp_inputs` writes 15 files `<id>.txt`. Each file is a complete message (request, blank line, text).

## 2. Run
1. Upload both ZIPs as separate skills. Note whether an error message appears.
2. One **new conversation** per case. Paste the message from `<id>.txt` and send it. Answer no follow-up questions and send no second message (except in a case that asks one; then note it).
3. Copy the answer **completely** (text, the `✎ Geändert` line, the count line) and save it as `<id>.txt` in one folder, for example `tools/fixtures/plain-prose/eval/testrun_claude-ai_<date>/`.
4. The **free usage limit** arrives quickly. Spread the 15 cases over two days. The first six give a first picture: `de_intern_mail`, `de_gender`, `de_gut`, `de_laenge`, `en_business`, `en_quote`.

## 3. Evaluation
`python3 -I tools/plain_prose_pruefen.py eval . <folder>` checks facts (numbers, required text), forbidden patterns, over-editing, length target, markdown, filler phrases, typography, and the count line against a measurement. **Limit:** the fact diff finds missing numbers and required text, but not a deleted statement that contains no number. That stays a blind comparison by you (original against result, without knowing which is which).

## 4. Log (fill in)
| Question | Answer |
|---|---|
| Did the right skill start (shown in the chat)? Yes/No per case | |
| Was the wrong skill chosen (de instead of en or the reverse)? | |
| Did a follow-up question appear although the default applies? | |
| Is there anything before or after the text (preamble, "Here is …")? | |
| Markdown (asterisks, hashes) in the text? | |
| Was a quotation changed (`de_vertrag`, `en_quote`)? | |
| Is the count line roughly right (rough sample)? | |
| Did non-breaking spaces arrive, or plain ones? | |
| Number of messages until the limit | |
| Other | |

## 5. What counts as a failure
A case fails if `eval` reports it, or if your blind comparison shows a lost statement. Find out whether the cause is the skill, the tool or the case before changing anything.
