#!/bin/bash
# Measures everything a "refactor claude" pass needs before any judgment, in parallel, into one folder
# (refactor-config step 1). Usage: shared/scripts/refactor-prep.sh [OUTDIR] [--no-pull] [--no-tests] [--clear-saved]
#   OUTDIR defaults to /tmp/refactor-prep. --no-pull skips pull.sh (tests). --no-tests skips test.py.
#   --clear-saved also deletes from shared/speed.md every entry whose fix is saved ("Fix saved" or "Covered by"),
#   after listing them in speed-saved.txt; the thread then saves speed.md with save.sh.
# Writes: summary.txt (read this first), rules.tsv (every row), new-rows.tsv and pairs.txt (rows changed since the
# last refactor commit, each with its candidate pairs), check.txt (check.py --all), load.txt (words read at start,
# per project), words.txt (rule file word counts and caps), commits.txt and changed.txt (since the last refactor),
# speed-saved.txt, untested.txt (test.py --covers: what each test runs, and the scripts no test runs), dups.txt (a
# value stated in more than one file),
# env.txt (hook and setup timing, only when their scripts changed; disk), tests.txt (test.py, in the background;
# tests.done appears when it finished).
cd "$(git rev-parse --show-toplevel)" || exit 1
out=/tmp/refactor-prep; pull=1; tests=1; clear=0
for a in "$@"; do case $a in --no-pull) pull=0;; --no-tests) tests=0;; --clear-saved) clear=1;; *) out=$a;; esac; done
mkdir -p "$out"; S=shared/scripts
[ $pull = 1 ] && bash $S/pull.sh > "$out/pull.txt" 2>&1
last=$(git log -1 --format=%h --grep='^refactor (')
[ -n "$last" ] || last=$(git rev-list --max-parents=0 HEAD | tail -1)
start=$(date +%s)
# deepen a shallow clone once, before the parallel rules.py runs and test.py race for .git/shallow.lock
[ "$(git rev-parse --is-shallow-repository)" = true ] && git fetch -q --unshallow origin main
if [ $tests = 1 ]; then rm -f "$out/tests.done"; nohup bash -c "python3 $S/test.py > '$out/tests.txt' 2>&1; touch '$out/tests.done'" >/dev/null 2>&1 & fi
python3 $S/rules.py > "$out/rules.tsv" 2>"$out/rules.err" &
python3 $S/rules.py --pairs --since "$last" > "$out/pairs.txt" 2>>"$out/rules.err" &
python3 $S/rules.py --since "$last" > "$out/new-rows.tsv" 2>>"$out/rules.err" &
python3 $S/check.py --all > "$out/check.txt" 2>&1 &
{ for p in $(ls -d projects/*/ | xargs -n1 basename); do python3 $S/index.py --load "$p"; done; } > "$out/load.txt" 2>&1 &
python3 $S/numcheck.py --dups > "$out/dups.txt" 2>&1 &
{ git log --format='%h %ad %s' --date=short "$last..HEAD"; } > "$out/commits.txt" &
{ git diff --stat "$last..HEAD" | tail -200; echo; echo "content files changed (sampling candidates):"; git diff --name-only "$last..HEAD" -- 'projects/*/content/*.md' 'projects/*/products/*/*.md' 'projects/*/learnings/*.md' 'shared/*.md'; } > "$out/changed.txt" &
{ for f in CLAUDE.md projects/*/config.*.md .claude/skills/*/*.md; do printf '%6d %s\n' "$(wc -w < "$f")" "$f"; done | sort -rn; echo "caps (check.py, its own count): CLAUDE.md 1,500; card 400; SKILL.md 1,000; other skill file 2,000; learnings and reference files 1,500"; } > "$out/words.txt" &
python3 $S/test.py --covers > "$out/untested.txt" 2>&1 &
{ grep -n 'Fix saved\|Fixes saved\|Covered by' shared/speed.md; } > "$out/speed-saved.txt" &
{ if git log --format=%h "$last..HEAD" -- .claude/hooks shared/scripts/setup-env.sh projects/3dp/scripts/orca-setup.sh | grep -q .; then
    t0=$(date +%s.%N); CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/session-start.sh >/dev/null 2>&1; echo "start hook: $(echo "$(date +%s.%N) - $t0" | bc) s (its scripts changed since $last)"
  else echo "start hook and setup-env unchanged since $last: not re-timed"; fi
  echo "setup-env done: $(ls -la /tmp/setup-env.done 2>/dev/null || echo 'not yet')"; df -h / | tail -1; du -sh /opt/orca . 2>/dev/null; nproc; } > "$out/env.txt" 2>&1 &
wait
if [ $clear = 1 ] && [ -s "$out/speed-saved.txt" ]; then
  python3 - "$out/speed-saved.txt" <<'EOF'
import re, sys
lines = open("shared/speed.md", encoding="utf-8").read().split("\n")
gone = {int(l.split(":", 1)[0]) for l in open(sys.argv[1], encoding="utf-8") if l.strip()}
open("shared/speed.md", "w", encoding="utf-8").write("\n".join(l for n, l in enumerate(lines, 1) if n not in gone))
print(f"speed.md: {len(gone)} saved entries deleted (save it with save.sh)")
EOF
fi
{
  echo "refactor-prep: last refactor commit $last ($(git log -1 --format=%ad --date=short "$last")); HEAD $(git rev-parse --short HEAD); $(cat "$out/pull.txt" 2>/dev/null); $(( $(date +%s) - start )) s"
  echo "rows: $(($(wc -l < "$out/rules.tsv") - 1)) in rules.tsv; $(($(wc -l < "$out/new-rows.tsv") - 1)) changed since $last in new-rows.tsv, with their candidate pairs in pairs.txt ($(wc -l < "$out/pairs.txt") lines)"
  echo "check.py --all: $(grep -c '^check' "$out/check.txt") lines in check.txt ($(grep -c 'report only' "$out/check.txt") report only)"
  echo "commits since $last: $(wc -l < "$out/commits.txt") in commits.txt; changed files in changed.txt"
  echo "speed.md: $(grep -c '^- ' shared/speed.md) entries, $(wc -l < "$out/speed-saved.txt") with a saved fix in speed-saved.txt$([ $clear = 1 ] && echo ' (deleted)')"
  echo "$(grep '^untested' "$out/untested.txt") (untested.txt); $(tail -1 "$out/dups.txt") (dups.txt)"
  echo "load.txt (words read at start per project), words.txt (rule files), env.txt (hook, disk)"
  [ $tests = 1 ] && echo "test.py running in the background: tests.txt, tests.done when finished (about 60 s)"
  [ -s "$out/rules.err" ] && echo "rules.py errors: see rules.err"
} | tee "$out/summary.txt"
