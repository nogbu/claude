---
name: refactor-config
description: Run when I say "refactor claude" or "refactor project". Searches every rule and every process for ways to run faster and use less without losing accuracy or quality, and proposes all fixes in one review.
---
## Goal
Find every way to make threads faster and lighter on usage without losing accuracy or quality. Nothing is beyond scrutiny, this skill and how work is split across threads included.

## Scope
- "refactor claude": CLAUDE.md, every skill in .claude/skills/, every projects/*/config.*.md, every Product rules section and rules header field, the hooks (.claude/settings.json, .claude/hooks/), every script in shared/scripts/ and projects/*/scripts/, and the project settings the bootstrap line sets up.
- "refactor project": projects/[project]/config.[project].md, the project's Product rules sections, rules header fields and scripts, checked against the core and skills.

## Run
- The command is my yes for the long work (CLAUDE.md, Answers); the first reply gives the expected time.
- After step 1, steps 2, 3 and 4 run at once: the thread takes 2, one helper each takes 3 and 4 (CLAUDE.md, Answers), briefed with the prep folder and its slice only; no second round of agents to verify, step 5's script does that.
- Nothing waits on me before step 6: a question a fix depends on goes on one card at the start, or into the review as options.
- Evidence: shared/speed.md, this project's threads and the commits since the last review (other projects' threads aren't readable here; no timing logs exist).

## Steps
1. Run shared/scripts/refactor-prep.sh [folder], which pulls, starts test.py in the background and measures the rest in parallel; read its summary.txt, then the files it names.
2. Rules: check each changed row against its candidate pairs (pairs.txt; full rows in rules.tsv) for:
   - Contradicts: the two can't both be followed. Keep one, or say which wins and when.
   - Combinable: they require the same thing, or one is a special case of the other. Word it once and delete the shorter.
   - Obsolete: a newer rule, learning, script or check does what an older row asks. Delete the older.
   - Shortened by: part of a row is covered elsewhere. Cut that part and name where it's covered.
   - Enforceable: a script, commit check or hook could do it or block breaking it. Write it and delete the rule.
   - Costly: following it takes more time, reads, tool calls or messages than its result needs. Make it cheaper or delete it.
   - Dead: it names a retired product, project, tool or script, or no thread used it in the last 60 days. Delete it, or say why it still earns its words.
   Each finding names both rows by id; every row against every other (rules.py --pairs alone) only when these checks changed.
3. Processes: walk every skill, CLAUDE.md routine (thread start, first reply, cards, saving, long threads), hook and script as a thread runs it, and find every saving:
   - Waits: anything idle until I answer, a script ends or a build finishes that could run ahead or in parallel.
   - Structural first: before proposing word cuts, caps or tightening, look for structural savings (steps run in parallel or in the background, steps scripted or skipped). Propose a cut or cap only with its measured saving per thread (tokens or seconds), weighed against its upkeep (tightening passes, blocked saves, lost detail).
   - Repeats: work done twice (re-reads, redraws, re-asks, re-checks) that could be done once or reused.
   - Manual: any step I or Claude does by hand that a script, check or hook could do.
   - Questions: any card or message I don't need, or questions the repo already answers.
   - Usage: reads, tool calls, agents, models or output bigger than the result needs.
   - Load: load.txt, ranked by words times how often threads read them; cut or move the largest first.
   - Scripts: tests.txt times every covered script; run each uncovered one (untested.txt) and add its test; fix failures; find slow spots, wrong results, output bigger than threads use, and copies of another script.
   - Accuracy: any step where a mistake got through, and the cheapest check that would catch it.
   - Sampling: re-check five results in changed files (changed.txt) against their sources; each error is an Accuracy finding.
   - Follow-up: each fix in the last review, against the threads and commits since; rework or revert any threads didn't follow or that saved less than claimed.
   - Blocks: every permission prompt, denied call and hook block that stalled a thread, each fixed with an allow rule, a hook change or a different call.
   - Summaries: each thread that hit a context summary: what filled it and what was reread or redone after, fixed at the source.
   - Environment: env.txt (the start hook and setup-env.sh, re-timed only when they changed; disk); anything threads rebuild that an earlier run could reuse.
   speed.md: --clear-saved deletes the entries whose fix is saved; each other entry gets its fix as a finding, or a reason why not.
4. What the lists can't show: vague wording that lets a rule slip; rules in the wrong layer (repo-edit, "Where things go"); stale names (check.txt); read-when fields and skill descriptions that sent threads to files or skills they didn't use, or missed ones they needed (speed.md); content files no thread read in 30 days, proposed for retired/; a value stated in more than one file (dups.txt), kept in its owner and pointed to from the others; this project's instructions differing from new-project's bootstrap line; product docs holding parked or superseded material (log moves) and logged items whose trigger has passed (drops). Propose cuts of repeats and restated context in every rule file in scope (pkg step 5) as fixes; a content file over its cap (check.txt) gets a log move only if it holds what's no longer current (product, Log).
5. Write every change as one diff and run shared/scripts/refactor-check.sh on it; fix what it reports.
6. Propose every fix in one review, ranked by measured time saved per thread (biggest first) and tagged with its file, each with its exact wording, what it saves, its setup cost and why accuracy and quality hold. End with a Checked list (one line per check in steps 2 and 4 and per process in step 3: "clean" or its fix numbers) and each file's word count before and after. Save the review, the diff and rules.tsv to /mnt/project-files/config-refactor/ and attach the review.
7. Save content changes (speed.md deletions, log moves, scripts) at once with repo-edit; change nothing else until I approve, then save every approved change in one commit whose message starts with "refactor (" (the next prep looks for it).
