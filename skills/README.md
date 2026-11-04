# Skills

Every skill is one `SKILL.md` that Claude loads in claude.ai, packaged as one ZIP per skill. This section has one page per skill: when it starts, how it works as a flow, a short example, its limits, its files and what has really been tested. The [gates page](GATES.md) shows which checks each skill has passed. The skill files themselves (the `SKILL.md` that Claude loads) are in `en/skills` and `de/skills`, the core skills in `en/skeleton/skills` and `de/skeleton/skills`.

## Two kinds of skills

- **A. Out of the box.** Ready-made ZIPs in `de/dist` and `en/dist`.
  - **A1 Core:** always there, five skills.
  - **A2 Module skills:** switched on by the interview, together with the core at most 12 uploads.
  - **A3 Add-ons:** offered when they fit, outside the 12.
- **B. Tailored to you.** Draft, not run in claude.ai: `skill-tailor` reads a template, asks three to five choices and builds a checked ZIP. Templates exist for `appointment-prep` and `letter-explain`; every other skill comes as kind A.

## The map

```mermaid
flowchart LR
  subgraph A1["A1 Core, always"]
    SB["setup-brain"]
    OI["onboarding-interview"]
    WR["weekly-review"]
    FC["fact-check"]
    BC["brain-check"]
  end
  subgraph A2["A2 Module skills"]
    DC["decision-clarify"]
    DK["decision-check"]
    KN["knowledge-note"]
    AP["appointment-prep"]
    LE["letter-explain"]
    PD["plain-prose-de"]
    PE["plain-prose-en"]
    BR["build-router"]
    VP["vibe-pack"]
  end
  subgraph A3["A3 Add-ons"]
    TM["transcript-minutes"]
    SP["style-profile"]
    AM["area-manager"]
    ST["skill-tailor"]
  end
  OI --> SB
  AM --> SB
  BC --> SB
  BC --> WR
  DC --> DK
  KN --> FC
  AP --> FC
  DC --> FC
  BR --> VP
  SP --> PD
  SP --> PE
  TM --> WR
  LE --> AP
  ST --> AP
  ST --> LE
```

An arrow means "hands over to" or "feeds": the interview leads to the setup, the style profile feeds both plain-prose skills, the build router hands over to the vibe pack, and so on.

## From first contact to daily use

```mermaid
sequenceDiagram
  participant You
  participant Claude
  participant Drive
  You->>Claude: Link to the repository
  Claude->>You: onboarding-interview (eight questions)
  You->>Claude: Answers, then yes
  Claude->>Drive: setup-brain creates folder and documents
  loop every week
    You->>Claude: weekly review
    Claude->>Drive: weekly-review files plan and journal
  end
  You->>Claude: new area, pause, update rules
  Claude->>Drive: area-manager changes status and rules
  You->>Claude: appointment, decision, research, text
  Claude->>Drive: the matching module skill files its result
```

## All skills

<!-- index:start -->
| Skill | Kind | Area |
|---|---|---|
| [`brain-check`](brain-check.md) | A1 · Core, always | Core |
| [`fact-check`](fact-check.md) | A1 · Core, always | Core |
| [`onboarding-interview`](onboarding-interview.md) | A1 · Core, always | Core |
| [`setup-brain`](setup-brain.md) | A1 · Core, always | Core |
| [`weekly-review`](weekly-review.md) | A1 · Core, always | Core |
| [`appointment-prep`](appointment-prep.md) | A2 · Module skill | Appointments, post and offices (`termine`) |
| [`build-router`](build-router.md) | A2 · Module skill | Build (`bauen`) |
| [`decision-check`](decision-check.md) | A2 · Module skill | Decisions (`entscheidungen`) |
| [`decision-clarify`](decision-clarify.md) | A2 · Module skill | Decisions (`entscheidungen`) |
| [`knowledge-note`](knowledge-note.md) | A2 · Module skill | Knowledge and sources (`wissen`) |
| [`letter-explain`](letter-explain.md) | A2 · Module skill | Appointments, post and offices (`termine`) |
| [`plain-prose-de`](plain-prose-de.md) | A2 · Module skill | Writing style (`schreibstil`) |
| [`plain-prose-en`](plain-prose-en.md) | A2 · Module skill | Writing style (`schreibstil`) |
| [`vibe-pack`](vibe-pack.md) | A2 · Module skill | Build (`bauen`) |
| [`area-manager`](area-manager.md) | A3 · Add-on, outside the upload budget | Core |
| [`skill-tailor`](skill-tailor.md) | A3 · Add-on, outside the upload budget | Core |
| [`style-profile`](style-profile.md) | A3 · Add-on, outside the upload budget | Writing style (`schreibstil`) |
| [`transcript-minutes`](transcript-minutes.md) | A3 · Add-on, outside the upload budget | Work and goals (`arbeit`) |
<!-- index:end -->

## How to read a page

- **Facts** at the top (kind, area, ZIP, size, description) are generated from the `SKILL.md` and the spec and checked at every export by `tools/skill_seiten_pruefen.py`.
- **Flow** is the same procedure as in the skill, drawn. The skill text is authoritative.
- **Status** says what was checked by a tool and what has run in claude.ai. Nothing here claims more than that.
