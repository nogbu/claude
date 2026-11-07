#!/bin/bash
# Pull main and list the files the pull changed (repo-edit skill, Saving).
# Usage: shared/scripts/pull.sh   Prints "changed: [files]", "no changes" or "NOT pulled".
cd "$(git rev-parse --show-toplevel)" || exit 1
old=$(git rev-parse HEAD)
git fetch -q origin main 2>/dev/null || { echo "NOT pulled: couldn't reach GitHub; try again."; exit 1; }
git merge -q --ff-only FETCH_HEAD 2>/dev/null || { echo "NOT pulled: the clone has commits main doesn't; stop and show me."; exit 1; }
changed=$(git diff --name-only "$old" HEAD | paste -sd' ')
if [ -n "$changed" ]; then echo "changed: $changed"; else echo "no changes"; fi
