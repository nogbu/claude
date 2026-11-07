#!/bin/bash
# Checks a review's proposed changes before they go to me (refactor-config step 6): applies a diff in a scratch
# clone of the repo, runs check.py on it as a commit would, runs the test.py tests of every script the diff
# touches, and prints each changed rule file's words before and after with its cap.
# Usage: shared/scripts/refactor-check.sh DIFF [OUTDIR]
#   DIFF is a unified diff against HEAD (git diff > changes.diff). OUTDIR keeps the scratch clone (default: a temp folder).
# Prints "refactor-check: ok" or "refactor-check: FAILED" with what failed; exit 1 on a failure.
set -u
root=$(git rev-parse --show-toplevel) || exit 1
diff=$(realpath "${1:?Usage: refactor-check.sh DIFF [OUTDIR]}")
out=${2:-$(mktemp -d /tmp/refactor-check-XXXX)}
rm -rf "$out/repo"; git clone -q "$root" "$out/repo" || exit 1
cd "$out/repo" || exit 1
git -c user.name=check -c user.email=check@check apply --index "$diff" || { echo "refactor-check: FAILED: the diff doesn't apply to $(git rev-parse --short HEAD)"; exit 1; }
fail=0
echo "scratch clone $out/repo at $(git rev-parse --short HEAD); staged: $(git diff --cached --name-only | paste -sd' ')"
echo "--- check.py (as a commit)"
python3 shared/scripts/check.py || fail=1
echo "--- words before and after, counted as check.py counts them (cap)"
for f in $(git diff --cached --name-only -- CLAUDE.md 'projects/*/config.*.md' '.claude/skills/*/*.md'); do
  python3 - "$f" <<'EOF'
import subprocess, sys
sys.path.insert(0, "shared/scripts"); import check
f = sys.argv[1]
old = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True).stdout
new = open(f, encoding="utf-8").read()
c = check.cap(f, new)
print(f"{f}: {check.count(f, old)} -> {check.count(f, new)} words (cap {c[0]}, {c[1]})")
EOF
done
scripts=$(git diff --cached --name-only -- 'shared/scripts/*' 'projects/*/scripts/*' '.githooks/*' '.claude/hooks/*')
if [ -n "$scripts" ]; then
  tests=$(python3 shared/scripts/test.py --for $scripts)
  untested=$(for s in $scripts; do python3 shared/scripts/test.py --for "$s" | grep -q . || echo "$s"; done | paste -sd' ')
  [ -n "$untested" ] && echo "--- no test covers: $untested (add one to test.py's COVERS)"
  if [ -n "$tests" ]; then
    echo "--- test.py $tests"
    python3 shared/scripts/test.py $tests || fail=1
  fi
fi
[ $fail = 0 ] && echo "refactor-check: ok" || { echo "refactor-check: FAILED (see above)"; exit 1; }
