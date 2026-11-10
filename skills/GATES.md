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
| `setup-brain` | skeleton, word for word | version of 2026-11-03 ran (setup on 2026-11-04) | none listed |
| `onboarding-interview` | skeleton, spec, personas | 0.4 ran (2026-11-04) | none listed |
| `weekly-review` | skeleton, word for word | yes (2026-11-10) | none listed |
| `fact-check` | spec only | yes (2026-11-05, 2026-11-10) | none listed |
| `brain-check` | spec only | yes (2026-11-05) | none listed |
| `decision-clarify` | spec only | yes (2026-11-06) | none listed |
| `decision-check` | spec only | yes (2026-11-06) | none listed |
| `knowledge-note` | spec only | yes (2026-11-05, 2026-11-06) | none listed |
| `appointment-prep` | spec only | tailored version once (2026-11-10); fixed version not yet | own draft |
| `letter-explain` | spec only | yes, one letter (2026-11-10) | own draft |
| `plain-prose-de` | own tool, self-test, 15 cases | no (simulated twice) | none listed |
| `plain-prose-en` | own tool, self-test, 15 cases | no (simulated twice) | own work |
| `build-router` | spec only | no | none listed |
| `vibe-pack` | own tool; skill check in both packages, self-test and pack patterns German only | no | own work |
| `transcript-minutes` | own tool; skill check in both packages, self-test and minutes check German only | no | own work |
| `style-profile` | own tool, self-test | no | own draft |
| `area-manager` | skeleton consistency, mutation test | yes (2026-11-06) | none listed |
| `skill-tailor` | templates checked against the fixed skills, self-test | 0.4 once (2026-11-10); 0.5 not yet | own draft |

## What "ran" means

Ran means: used at least once in a free test account with the German pack, with an invented person and invented letters, between 2026-11-01 and 2026-11-10, and checked against the tool calls and, where noted, a Drive export. It does not mean tested by other people or in a paid plan. The English pack has not run in claude.ai. The test guides under `docs/` describe how to repeat the tests.
