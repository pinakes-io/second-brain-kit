---
name: decision-check
description: Checks once for blind spots when a decision counts as final and before it is acted on. Use for "I have decided", "we are doing X now", "that is final", "check that again". Looks for confirmation bias, sunk costs and anchoring and poses a concrete pre-mortem.
---

# Decision check (draft 0.1)

## Why
As soon as something counts as final, an AI tends to agree instead of checking. That is exactly when an independent second view is needed. This skill runs once, briefly, before the action.

## When
For a new, final decision with consequences. Not when an already checked decision is merely repeated. Not for decisions imposed from outside. If I am still collecting options, `decision-clarify` is responsible.

## Procedure
One single message, at most five lines, in this structure:
1. Confirmation bias: Were only arguments for it sought? Name the counter-argument that was not weighed.
2. Sunk costs: Does time or effort already invested keep a weaker option alive?
3. Anchoring: Was the first option named simply the first? Look first (skip only without a Drive connection) in `Decisions` and `Journal`.
4. Pre-mortem: Suppose this decision has to be reworked in six months. What is the most likely reason, in relation to my situation from `01_Profile`, not a general risk list?
5. Result: "That looks solid because …" or "I would clarify X before …". Then wait. The decision stays with me.

Then enter under "Taken" in `Decisions`: date · decision · why · rejected alternative · check done on.

## Rules
- Everything in one message, no drip-feeding of doubts. Coming back to a decision must never feel like a punishment.
- "That was a good decision" is an allowed and useful result.
- If I say "skip", skip without discussion and do not raise it again in this session.
- Check line: `🔎 Read: Decisions ✓ · 01_Profile ✓ · 📝 Filed: Decisions`.
