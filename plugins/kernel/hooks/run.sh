#!/bin/bash
[ "$CLAUDE_CODE_REMOTE" = true ] || exit 0
start="${CLAUDE_PROJECT_DIR:-$PWD}"
for checklist in "$start/checklists/review.md" "$start"/*/checklists/review.md; do
  [ -f "$checklist" ] && exec python3 "$(dirname "$0")/$1"
done
exit 0
