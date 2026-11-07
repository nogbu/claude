#!/bin/bash
# Save repo edits (repo-edit skill, Saving).
# Usage: shared/scripts/save.sh "[file]: [change] ([project])" file [file...]
# Commits only the named files, then pushes to main; if the push is rejected it
# pulls with --rebase once and pushes again (never forced), then prints "pushed [sha]" or "NOT pushed".
# Each pushed commit is logged in .git/thread-saves, so undo.sh can revert this thread's saves.
# Before committing it reports numbers that left the named .md files (numcheck.py), without blocking.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
[ $# -ge 2 ] || { echo 'Usage: save.sh "[file]: [change] ([project])" file [file...]'; exit 1; }
msg=$1; shift
git config core.hooksPath .githooks
for f in "$@"; do
  if [ -e "$f" ] || git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then git add -A -- "$f"; fi
done
git diff --cached --stat -- "$@"   # only the named files; anything else staged stays out of the commit
md=$(printf '%s\n' "$@" | grep '\.md$' | grep -v '^shared/speed.md$')   # report only: numbers that left the named .md files (text moved to another named file counts; speed.md entries are meant to go)
[ -n "$md" ] && python3 shared/scripts/numcheck.py $md | grep -v '^all numbers kept' | sed 's/^/numcheck (check each was meant to go): /'
if git diff --cached --quiet -- "$@"; then echo "NOT pushed: nothing to commit in $*"; exit 1; fi
git commit -q -F <(printf '%s\n' "$msg") -- "$@" || { echo "NOT pushed: commit refused (see the check above)."; exit 1; }
if ! git push -q origin HEAD:main 2>/dev/null; then
  git pull --rebase -q origin main || { echo "NOT pushed: couldn't rebase onto main (a conflicting edit, or other unsaved changes in the clone); stop and show me."; git rebase --abort 2>/dev/null; exit 1; }
  git push -q origin HEAD:main || { echo "NOT pushed: push rejected twice."; exit 1; }
fi
git fetch -q origin main
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
  printf '%s\t%s\n' "$(git rev-parse HEAD)" "${msg%%$'\n'*}" >> "$(git rev-parse --git-dir)/thread-saves"  # for undo.sh
  echo "pushed $(git rev-parse --short HEAD)"
else
  echo "NOT pushed: origin/main doesn't match the new commit."; exit 1
fi
