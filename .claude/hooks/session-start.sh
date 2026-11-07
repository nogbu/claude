#!/bin/bash
# Session-start hook (CLAUDE.md, How the rules load). Runs at thread start,
# resume and after a summary: pulls the repo, turns on the commit checks, starts
# shared/scripts/setup-env.sh (libraries and OrcaSlicer) in the background, and
# prints this project's card, config.[project].md (named by /mnt/project-files/.project),
# and the file index index.py builds from file headers.
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
git branch -q --set-upstream-to=origin/main 2>/dev/null
git pull --ff-only -q origin main >/dev/null 2>&1 || echo "Session-start hook: git pull failed; pull before editing."
git config core.hooksPath .githooks
nohup bash shared/scripts/setup-env.sh >/tmp/setup-env.log 2>&1 &
echo "CLAUDE.md: $(head -1 CLAUDE.md)"
marker=/mnt/project-files/.project
if [ ! -s "$marker" ]; then
  echo "Session-start hook: $marker is missing, so config.[project] wasn't printed; read it yourself, and offer to write .project."
  exit 0
fi
project=$(tr -d '[:space:]' < "$marker")
config="projects/$project/config.$project.md"
if [ ! -f "$config" ]; then
  echo "Session-start hook: .project names '$project', but $config doesn't exist."
  exit 0
fi
echo "Project: $project. Below is $config as of commit $(git rev-parse --short HEAD) (loaded by the session-start hook)."
echo "----- $config -----"
cat "$config"
echo "----- end of $config -----"
echo "----- file index (shared/scripts/index.py $project) -----"
python3 shared/scripts/index.py "$project"
echo "----- end of file index -----"
