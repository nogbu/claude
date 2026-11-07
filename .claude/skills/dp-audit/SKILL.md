---
name: dp-audit
description: Run a full audit when I say "audit this design" or "dp audit"; a form audit only on "form audit", a function audit only on "function audit". Before asking whether a 3dp design is ready to build, and before any 3dp build not preceded by that question, ask whether to run a full audit first when its script changed since the last full audit, or since a form audit and a function audit on the same commit (the commit in each grid header); skip it if I say no; never run one just because a picture is shown. A complete audit of a design against the design principles, listing every change needed for full compliance.
---
dp compliance outranks everything else: earlier decisions in the product doc or log, changes already agreed, my own earlier choices, looks, effort, and how long the audit takes.

Three kinds: the form audit checks how the design looks and prints, the function audit its fits, loads and use, as dpreqs.py splits the requirements (General in both); the full audit checks both. A form or function audit passes --audit form or --audit function to dpreqs.py and dpgrid.py, and every step below covers only its requirements.

1. Pick the design this thread is discussing; if it covers more than one, or none, ask which first.

2. Read design-principles.md and the design's build script in full; from the product doc read only its dp exceptions, Decisions and the values the build script takes, and from the log only entries those cite. List each file read with its last commit (CLAUDE.md, First reply). If it has no build script, say so and use its build/[name]_audit-model.py: run it as is if its last commit is newer than every change to the product doc and concept scripts; otherwise update it (or write it, if missing) to model the current design, and save it (repo-edit).

3. Requirements list. Run projects/3dp/scripts/dpreqs.py; its numbered list (every dp bullet except Short name and Talking to me, word for word) is the requirements list, and the grid cites its numbers. Nothing is left out because it seems not to apply.

4. Item inventory, made by running code on the actual build geometry of each whole assembled part, never block by block and never from a hand sketch, starting from projects/3dp/scripts/dpcheck.py --json [file] --inventory [file] on its model, which lists every part, edge, step and overhang it measures, alike ones as one item with each place. Add the rest by hand, so the list has every:
   - part and how it prints
   - edge: outside and inside, vertical and horizontal, including edges the script doesn't model yet (an edge another part fills doesn't exist)
   - place where two surfaces meet at different heights or depths (a step), including steps between parts and at every seam
   - joint, fit and contact face (anything a test piece, insert or mating part rests or presses against), with every edge that bounds it, each checked against design principle 2's Limits bullet
   - overhang, bridge and spot over air
   - load path
   - way a part could be printed, assembled or used wrong
   Give the count for each kind. List only the kinds the audit's requirements apply to (dpreqs.py --json, "applies"): a function audit skips edges, steps and overhangs.

5. Check grid. Run projects/3dp/scripts/dpgrid.py make on dpcheck's --json and the item inventory, with --script [the build script]. It writes the full grid: dpcheck's rows for requirements it covers as "all", the edge cells the inventory measured (TODO ones carry the measurements to judge from), and N/A with the map's reason for every cell whose requirement doesn't apply to that item's kind (the "applies" map in dpreqs.py). Check every other cell by hand, a "part" requirement's cells included: PASS, FAIL or N/A, with evidence: script output, a measurement from the geometry, or a quote from a doc read in this thread. N/A needs a one-line reason. No blank cells or "probably fine".

6. Zero trust. Treat every existing decision, exception and stated reason as unproven. A reason counts only if its source is opened in this thread and says what's claimed, or a check in this thread proves it. A reason marked inference, or citing a source that doesn't say it, counts as no reason, and the item FAILS. My own earlier choices are checked the same way; if one breaks dp, list the change anyway and say it reverses my choice. An exception whose reason is "executive override" stands: mark it PASS and propose no change.

7. Changes. For every FAIL, write one change: what, where on the part, the exact size, and which requirement it meets. Each change is one decision: if a fix has parts I could accept or turn down separately (e.g. two edges, or a size plus a move), give each part its own number. Apply all the changes to the geometry in a scratch copy and run steps 4 and 5 again on the changed design, because a fix can break something else. Repeat until a full pass finds no FAIL.

8. Second pass. Before step 4, start a fresh worker that won't see your results, give it steps 3 to 6 for every requirement dpcheck doesn't cover as "all", and keep working; compare once both are done. Anything it finds that you missed: add it, find why it was missed, and recheck that whole category.

9. Report, in plain language:
   - The full check grid as a file in /mnt/project-files/notes/ (dpgrid heads it with the audit's kind, the build script's path and its last commit).
   - In the reply: the counts (requirements, items, cells checked, FAILs) and the numbered change list, each change saying exactly where on the part it is. Draw no pictures (build-3dp, Walkthrough pictures).
   - Anything that couldn't be checked, and why. Never drop a check silently.
   Change no repo file. Ask how I want to go through the changes.
