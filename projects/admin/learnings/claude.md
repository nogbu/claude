---
about: Learnings about Claude projects, thread models and upgrades
read-when: before work on projects, project settings or the repo
readonly: no
---
# learnings/claude

Moved from config.admin on 2026-10-07 (config redesign phase 3).

- All projects in this account are and will be private.  
- New threads use Thread model and Thread effort from Project settings > General, not the last model picked; a running thread's model is changed from its own model picker (Projects docs, 2026-10-03).  
- Upgrading a classic project doesn't copy docs attached from a connector; they're read live by Drive ID (UPGRADE-NOTES, 2026-10-03).
- Trimming a doc to a word cap by moving text alone pushed decisions and their reasons out of state.md (photo-board, rfid, putes); restoring them and tightening the wording, with a script checking every number survives, kept them in and reached the cap for four of eight docs (phase 4, 2026-10-07).  
- A routine made from a private project fires only into the thread that made it (a fresh session per firing is refused), so a scheduled pass resumes its thread: the weekly short refactor pass (Mondays 6:57 AM Eastern, created 2026-10-09 in the admin refactor thread) runs there; delete_trigger removes it.
