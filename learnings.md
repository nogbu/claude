# Learnings

Settled facts every project shares. Facts for one project go in that project's own `learnings.md`.

One fact per line, with where it came from and when it was confirmed:

`- [what it's about]: [the fact] (source: [where it came from], confirmed [date])`

A fact goes here only after it's been checked against its source. The automatic lookup shows matching lines to Claude before it answers each message.

- Coordinator thread tools: start_thread sets the exact title Claude writes, rename_thread changes it later, list_threads filters by state, message_thread reopens a resolved thread, and get_project_settings / update_project_settings read and replace the project instructions, only when Nwani asks (source: admin project's coordinator, from its tool descriptions, confirmed 2026-10-26)
- Thread tools: a thread can rename itself (rename_thread), list the project's threads with title and state (list_threads), and message the coordinator (message_coordinator), but can't start a thread or edit project instructions (source: this session's tool list, confirmed 2026-10-26)
- Idle threads: a thread with no activity for a week is resolved automatically and can be reopened (source: https://code.claude.com/docs/en/claude-projects, Overview, confirmed 2026-10-26)
