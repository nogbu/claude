---
name: repo-edit
description: Load before creating, changing or moving any file in the nogbu/claude repo, and on "save [x]", "remember [x]", "save this to [short name]" or "undo".
---
## Saving
1. Run shared/scripts/pull.sh first, before drafting a rule change as well as before saving; re-read a rule file only if it lists it.
2. Save with shared/scripts/save.sh "[file]: [change] ([project])" [files]. Check its diff shows only your change. Say a change is saved only after it prints "pushed [sha]"; on a rebase conflict, show me both versions. If the thread can't push, say so and give me the exact text.
3. When check.py refuses a save for a project card's word cap, scan the whole card for repeats, conflicts with the change and wordy bullets, and propose the cuts that clear the cap while losing the least; never stop at the first ones that fit.
4. Report each content save in one line: the file, what changed and the sha. "undo" runs shared/scripts/undo.sh, which reverts this thread's newest save; run it again for the one before.
5. When an update raises questions, hold the answers and apply them in one update (one read, one write, one check), changing nothing between answers, scratch files included.

## Where things go
"save [x]" and "remember [x]" draft x for the right file (CLAUDE.md, Permission). Place each new rule, learning or note by asking in order:
1. Can a script or commit check do it? Write the code, no rule.
2. Needed only for some tasks? That task's skill, or a learnings file.
3. Needed by every thread in one project? The project card.
4. Needed by every reply everywhere? The core.

Before proposing a rule, alone or in a list of candidates, list every existing rule it contradicts, combines with, makes obsolete or shortens, found with python3 shared/scripts/rules.py --find on its key words and their synonyms, and include those edits in the draft.

## Files
- Layout: CLAUDE.md; .claude/skills/[skill]/SKILL.md, plus any file the skill reads; .claude/hooks/ and .githooks/; shared/ for content every project uses, shared/scripts/ for shared scripts; projects/[project]/ holds config.[project].md, content/, learnings/[topic].md, data/ (settings as JSON, read with shared/scripts/lookup.py), scripts/ for scripts no product owns, and products/[name]/ with state.md, log.md and build/ (its build scripts and their data). Any thread can read any project's files by path.
- A project card has Cardinal sources (with the theme), then Overrides (what overrides the core) and Rules when they have entries, plus any section the project needs; leave out an empty one.
- Every content file starts with a header: about, read-when (optional in a product doc) and readonly; name only when its short name isn't its file name; rules for its own rules. index.py prints one line per file from about plus read-when.
- Learnings and how-to notes go in a learnings file whose read-when says which task reads it, never the card.
- Tag every stored reference figure Measured, Listed or Estimated, and replace Listed and Estimated figures with Measured ones as they come in.
- Tag a decision 'agreed [date]' only when I said yes to it after seeing it (its picture or exact values); my asking for a change is not a yes to how you carried it out; a recommendation I haven't answered is 'proposed [date]'.
- Before saving a new script or skill step, run the whole task it serves once on a real input and time each step; script any step that leaves me writing output item by item (a grid, a list, a per-item check).
