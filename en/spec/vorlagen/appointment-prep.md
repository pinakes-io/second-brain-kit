# Template: appointment-prep (for version 0.7)

This file is a template for the skill `skill-tailor`. It is not a skill itself. Without the markers `<!-- anpassen:… -->` and `<!-- /anpassen -->` the text below is, character for character, the fixed version `skills/appointment-prep/SKILL.md`. Checked by `tools/vorlage_pruefen.py`.

**Rules for tailoring:** Only text between the markers may change. Everything else stays word for word, including punctuation and blank lines. The markers are removed afterwards. The answers are rules for the skill, not data: no names, no numbers, no diagnoses, no addresses.

## Questions

```yaml
vorlage: appointment-prep
fassung: "0.7"
fragen:
  - id: terminarten
    frage: Which appointments do you want to prepare for?
    typ: mehrfach
    optionen: [All (Recommended), Employment agency or job centre, Immigration office or citizens' office, Recognition counselling, Job interview, Doctor, School, Bank]
    regel: With "All" both places stay unchanged. Otherwise keep only the chosen types, wording and order of the kept entries unchanged, the description without "and others", so the skill only triggers for these appointments. At least one type.
  - id: laenge
    frage: How long should the answers be?
    typ: einfach
    optionen: [Short (Recommended), Very short, More detailed]
    regel: Short = unchanged (15 and 8 lines). Very short = "at most about 8 lines" and "On a phone, in a hurry or under strain at most 5 lines." More detailed = "at most about 25 lines" and "On a phone, in a hurry or under strain at most 12 lines."
  - id: saetze
    frage: What do you need for the appointment itself?
    typ: einfach
    optionen: [Questions and sentences in my language (Recommended), Sentences in simple German to read out, Only questions I can ask]
    regel: First option = unchanged. Second = "three short sentences in simple German to read out"; if my chat language is not German, add ", with the translation into my chat language below". Third = "three questions I can ask at the appointment".
  - id: entwuerfe
    frage: Should cancellations and short texts come straight away?
    typ: einfach
    optionen: [Straight away when I am in a hurry (Recommended), Always straight away, Only on request]
    regel: First option = unchanged. Second = "If I must write or say something (cancellation, substitute, call), give a ready-to-copy draft of two to four lines straight away." Third = "If I must write or say something (cancellation, substitute, call), offer a ready-to-copy draft of two to four lines."
kennung: After tailoring, "kennung" reads "(version 0.7, tailored on <YYYY-MM-DD>)".
```

## Template

~~~skill
---
name: appointment-prep
description: Prepares me for an upcoming appointment or records afterwards what was agreed (<!-- anpassen:terminarten -->employment agency or job centre, immigration office or citizens' office, recognition counselling, job interview, doctor, school, bank and others<!-- /anpassen -->). Use for "prepare appointment", "what to expect", "how do I prepare" and for "the appointment was today, …". Not for simply adding an appointment to the calendar. A letter with an invitation is explained first by letter-explain. Short by default, detailed on request.
---

# Appointment preparation <!-- anpassen:kennung -->(draft 0.7, simulated, untested in claude.ai)<!-- /anpassen -->

## Goal
I go into every appointment prepared and know afterwards what to do: short when I am in a hurry or under strain, detailed when I want it.

## Procedure
1. **Read:** `00_Status` (limits, who can see what), `01_Profile` (form of address, language, device, times, companion) and the State of the matching area, if you may read Drive.
2. **Tone:** Use my form of address (if I write formally, stay formal throughout) and my chat language, also for follow-up questions and "More?". If I am visibly under strain, acknowledge that first in one sentence.
3. **Date:** A weekday without a date means the next day with that name. Only ask if it could be today or is truly ambiguous.
4. **Knowledge in three levels:**
   - **Fresh:** With web search, deadlines, duties, fees and required documents go through `fact-check` (statement · source · date retrieved).
   - **As a rule:** Without a source, state a commonly known rule that carries my main question as "As a rule …, unchecked, please confirm with <office>", and recommend first the action that protects me (report early, act within the deadline).
   - **Usually like this, please ask on site:** procedure, usual documents, tips, in full sentences.
   Nothing from the last two levels goes into Drive or the `Fact-Ledger` as a fact. Never name a source you do not have.
5. **Compact (default):** <!-- anpassen:laenge -->at most about 15 lines<!-- /anpassen -->: answer to my question · what to bring (per invitation, then usual) · <!-- anpassen:saetze -->three questions or sentences for the appointment<!-- /anpassen --> · unchecked, clarify with <office> · "More?". <!-- anpassen:laenge -->On a phone, in a hurry or under strain at most 8 lines.<!-- /anpassen -->
6. **Detailed** only on request ("thorough", "everything", yes to "More?"): outline below, then counter-check and offer of a role play.
7. **After the appointment:** What was said, agreed, documented? Suggest entries and deadlines with reminders.
8. **Deliver texts:** <!-- anpassen:entwuerfe -->If I must write or say something (cancellation, substitute, call), give a ready-to-copy draft of two to four lines straight away when I am in a hurry.<!-- /anpassen --> Texts for third parties (employer, customers, school, club, shift plan) name no medical or private reason if "appointment" or "not available" is enough.
9. **Crisis:** If a situation seems mentally threatening, name the crisis line (in Germany Telefonseelsorge 0800 111 0 111) and 116117 next to 112.

## Outline (detailed only)
Procedure and roles · the other side's questions with reason and draft answer · what to bring · dos and don'ts · my own questions · afterwards. Counter-check: the most uncomfortable question, possible misunderstanding, who may act (power of attorney, signature), plan B.

## Specifics per type of appointment
<!-- anpassen:terminarten -->- **Employment agency, job centre:** which appointment, which office; reporting deadlines and the consequences of missed appointments are usually the main question (step 4). Counselling is not a registration.
- **Immigration office, citizens' office:** the request in one sentence, changes since the last appointment, a certificate for the waiting time; sentences in simple German if I chat in another language.
- **Recognition counselling:** the result is a plan; documents only yes or no; target profession, language level.
- **Job interview:** me in three sentences, two strengths with an example, gaps honestly, salary range according to limits.
- **Doctor:** according to the health level; practise sentences if the language is hard.
- **School:** aim, observations, next step; reversed for teachers; pupils only as a role.
- **Bank:** what the account is for, costs, cancellation, transfers abroad.<!-- /anpassen -->

## Limits
- **Always blocked:** numbers of ID card, passport, residence permit, account (IBAN), card, tax, health, pension and social insurance; passwords, PINs, login data and keys. Never store, never copy, not even after a yes; write "in the letter".
- **After a yes:** file, case and cashier references of authorities and courts, appointment numbers.
- **Only on explicit request, never offered:** customer, patient, case, membership, policy, child benefit and eVB numbers.
- **Blocks apply** to storing and to sentences for reading aloud or copying (placeholders there). What I must truthfully tell an office you state without restriction.
- **Children, names, money** according to `00_Status`, including class, age, year of birth, name in the letter.
- **Health:**
  - "open": after a yes, content goes into the Health area or the folder I name, not into the general appointment list.
  - "appointments and deadlines only": store date, time and "appointment" with at most the town, follow-up appointment, deadlines. "Practice" or "clinic" only if I use that general word myself and it is not a specialist service. No street, no building, floor or name of a specialist service (address only in the chat); no reason, no diagnosis, no medication, nothing revealing ("vaccination card", "fasting", "eye", "dental", "children's", "gynaecology", "psych", "addiction").
  - "blocked": by default no entry; state the block in one sentence. If I explicitly ask for it, ask once "Only for this appointment?" and after a yes create a completely neutral entry ("appointment" or "not available", date, time, no place); the level stays. Otherwise offer the phone calendar, never only a change of level. Do not ask about content.
- **Who can see what:** If the status says who sees what, choose a document this person does not see, or write neutrally, and say so in one sentence. If another person writes for me: with their own read access and without health or intimate matters they may have neutral entries made; otherwise ask for my consent.

## Filing
- Suggestion in plain words, then "Add it?" in my language. An explicit request in the message counts as a yes: enter all appointments named and the deadlines and tasks derived from them, uncertain ones as "(provisional, unchecked)", and show what you enter.
- If I dictate the entry word for word and nobody else sees it, keep my wording; leave out only diagnosis, illness and blocked details and say in one sentence what you left out.
- Into the matching document (club, business, health, private), not automatically into the appointment list. Journal or status only on request or for a decision.
- Reminders outside my sleeping and working hours, at least one hour before my sleep limit; if my times are unclear, ask briefly.
- Name documents in the chat with plain words, not file names.

## Rules
- Send nothing in my name, make no promises about decisions of third parties.
- For legal questions one sentence at the end: "No legal advice, binding is <authority or court>." For a company, bank or employer name a counselling service instead; for everyday appointments leave the sentence out.
- The first line answers my question. The check line is a short footer at the end, in my language, without file names or jargon, with the active limits.
- No internal building-block words in the chat.
~~~
