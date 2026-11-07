#!/bin/bash
# Undo this thread's newest save (config redesign, section 8.1).
# Usage: shared/scripts/undo.sh   Run it again to undo the save before that.
# save.sh logs each pushed commit in this clone's .git/thread-saves (each thread has its own clone).
# This makes a revert commit (history is never rewritten), pushes it to main the way save.sh does,
# and prints "undone [sha] with [new sha]" or "NOT undone".
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
log="$(git rev-parse --git-dir)/thread-saves"
[ -s "$log" ] || { echo "NOT undone: this thread has no saves left to undo."; exit 1; }
line=$(tail -1 "$log"); sha=${line%%$'\t'*}; msg=${line#*$'\t'}
git config core.hooksPath .githooks
git pull -q --ff-only origin main 2>/dev/null || { echo "NOT undone: couldn't pull main first; stop and show me."; exit 1; }
git merge-base --is-ancestor "$sha" HEAD || { echo "NOT undone: $sha isn't on main."; exit 1; }
# "[file]: [change] ([project])" becomes "[file]: undo [change] ([project])", which the commit-msg check accepts.
new_msg="${msg%%: *}: undo ${msg#*: }"
if ! git revert --no-commit "$sha" 2>/dev/null; then
  echo "NOT undone: a later edit changed the same lines. Conflicting files:"
  git diff --name-only --diff-filter=U
  git revert --abort 2>/dev/null; exit 1
fi
git diff --cached --stat
git commit -q -F <(printf '%s\n\nReverts %s.\n' "$new_msg" "$sha") || { git revert --abort 2>/dev/null; echo "NOT undone: commit refused (see the check above)."; exit 1; }
if ! git push -q origin HEAD:main 2>/dev/null; then
  git pull --rebase -q origin main || { git rebase --abort 2>/dev/null; git reset -q --keep HEAD~1; echo "NOT undone: couldn't rebase onto main; stop and show me."; exit 1; }
  git push -q origin HEAD:main || { echo "NOT undone: push rejected twice."; exit 1; }
fi
git fetch -q origin main
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
  sed -i '$d' "$log"
  echo "undone $sha with $(git rev-parse --short HEAD)"
else
  echo "NOT undone: origin/main doesn't match the revert commit."; exit 1
fi
