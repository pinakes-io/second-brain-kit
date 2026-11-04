# Gates

Before a state of this repository is published, it passes a fixed list of gates. This page says what each gate is, how it is checked, and which skill stands where.

## The gates

| Gate | What it checks | How |
|---|---|---|
| Fresh export | The published tree is built from scratch, without history, from the working repository. | `tools/export_bauen.py` (internal), run before every push |
| Checks and self-tests | Spec, skeleton skills word for word against the spec, language parity, skill content tools, ZIP rules; every tool proves itself on deliberately broken copies. | `tools/spec_pruefen.py`, `tools/skelett.py`, `tools/lang_parity.py`, `tools/plain_prose_pruefen.py`, `tools/style_profile_pruefen.py`, `tools/protokoll_pruefen.py`, `tools/pack_pruefen.py`, `tools/zip_bauen.py`, `tools/skill_seiten_pruefen.py` |
| Forbidden patterns | No personal names, private paths or names of style sources anywhere in the export. Source names are compared by checksum, never stored in clear text. | scan in the export script |
| Secret scan | No keys, tokens or passwords. | `detect-secrets` over the export |
| Licence | The whole repository is MIT. | `LICENSE` |
| Provenance | Where each skill comes from is recorded in an internal list and reviewed before publication. | internal rights list |
| Tests in claude.ai | The skills run in a free test account, never in a main account. | test guides in `docs/` |
| Publication | Pushing is done by the maintainer only. | by hand |

All checks run on every export. They check patterns, numbers and consistency, not meaning; that is why the test in claude.ai is its own gate.

## Skill by skill

"Spec only" means the skill is covered by the spec check, the language parity check and the ZIP rules, but has no content tool of its own. "Own work" means the maintainer confirmed that the idea and the sources are his own; "own draft" means the skill was written from scratch for this repository; "none listed" means the internal list has no open point for this skill.

| Skill | Content checks | Run in claude.ai | Provenance |
|---|---|---|---|
| `setup-brain` | skeleton, word for word | earlier version ran | none listed |
| `onboarding-interview` | skeleton, spec, personas | earlier version ran | none listed |
| `weekly-review` | skeleton, word for word | earlier version ran | none listed |
| `fact-check` | spec only | no | none listed |
| `brain-check` | spec only | no | none listed |
| `decision-clarify` | spec only | no | none listed |
| `decision-check` | spec only | no | none listed |
| `knowledge-note` | spec only | no | none listed |
| `appointment-prep` | spec only | no (simulated, draft 0.7) | own draft |
| `letter-explain` | spec only | no (simulated, draft 0.7.1) | own draft |
| `plain-prose-de` | own tool, self-test, 15 cases | no (simulated twice) | none listed |
| `plain-prose-en` | own tool, self-test, 15 cases | no (simulated twice) | own work |
| `build-router` | spec only | no | none listed |
| `vibe-pack` | own tool; skill check in both packages, self-test and pack patterns German only | no | own work |
| `transcript-minutes` | own tool; skill check in both packages, self-test and minutes check German only | no | own work |
| `style-profile` | own tool, self-test | no | own draft |
| `area-manager` | skeleton consistency, mutation test | no | none listed |
| `skill-tailor` | templates checked against the fixed skills, self-test | no (simulated, draft 0.4) | own draft |

## What "ran" means

The first free-account walkthrough used the first versions of the three skeleton skills with an invented person. Since then the interview, the setup and other parts have changed, and none of the later versions has been run in claude.ai yet. The tests that close this gap are described in the test guides under `docs/`.
