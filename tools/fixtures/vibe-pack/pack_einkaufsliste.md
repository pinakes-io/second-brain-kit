```
=== AGENTS.md ===
Project: A shopping list web page that I can open on my phone and tick off items.
Done means: I open the page on my phone, type an item and it appears in the list. Tapping an item crosses it out. After reloading the page the list is still there.
Not now: Login, Sync between devices, Hosting, Sharing the list with others.
Stack: Plain HTML, CSS and JavaScript in one folder, because it needs no install and every browser runs it. Runs locally.
Run: open index.html in the browser   Test: open test.html in the browser, it must show PASS

1. Never delete, skip or weaken tests. If one fails, fix the code or ask me.
2. No fake implementations: no stubs, hardcoded results or silent TODOs presented as done.
3. Secrets only from environment variables, never in code, logs or the repo.
4. Nothing destructive (delete, overwrite, force) without asking me first.
5. Do not change existing interfaces. Add a new one next to them.
6. Docs before code: for any API, library or command read the current docs first. If unsure, say so. Do not guess.
7. Small steps, one commit each. Say a step is done only after showing the command and its output.
8. Stop after three failed attempts at the same problem and report what you tried.

Use invented sample data only, until I accept the project.
At the end of every session write HANDOVER.md: goal, done, state, next step, open questions, last error text.

=== PLAN.md ===
Risks: The list is lost on reload if saving is forgotten. Buttons are too small for a thumb on a phone. The agent adds a login nobody asked for.
0 Setup: git init, first commit, the run command starts with an empty page.
1 Tracer: Add one item and show it in the list. Expected: typing milk and pressing Add shows milk on screen.
2 Verification: run test.html, paste its output, mark the tracer done only then.
3 Cross out: tapping an item crosses it out. Expected: the tapped item is struck through.
4 Keep the list: store the list in the browser. Expected: after a reload the items are still there.
5 Phone layout: buttons large enough for a thumb. Expected: usable on a 360 pixel wide screen.
Last: write HANDOVER.md.
```
