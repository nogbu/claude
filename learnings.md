# Learnings

Settled facts every project shares. Facts for one project go in that project's own `learnings.md`.

One fact per line, with where it came from and when it was confirmed:

`- [what it's about]: [the fact] (source: [where it came from], confirmed [date])`

A fact goes here only after it's been checked against its source. The automatic lookup shows matching lines to Claude before it answers each message.

- Coordinator thread tools: start_thread sets the exact title Claude writes, rename_thread changes it later, list_threads filters by state, message_thread reopens a resolved thread, and get_project_settings / update_project_settings read and replace the project instructions, only when Nwani asks (source: admin project's coordinator, from its tool descriptions, confirmed 2026-10-26)
- Thread tools: a thread can rename itself (rename_thread), list the project's threads with title and state (list_threads), and message the coordinator (message_coordinator), and resolve itself or another thread (set_thread_resolved), but can't start a thread or edit project instructions (source: this session's tool list, confirmed 2026-10-26, resolving confirmed 2026-11-07)
- Thread attachments: a thread holds at most 24 attached outputs. A reply past that still posts, but its files are skipped (source: the reply tool's error in the New claude repo design thread, "the thread already has the maximum of 24 attached outputs", confirmed 2026-11-07)
- Idle threads: a thread with no activity for a week is resolved automatically and can be reopened (source: https://code.claude.com/docs/en/claude-projects, Overview, confirmed 2026-10-26)
- Nwani's time zone: Eastern (US). "Today" means the date in Eastern time, not UTC (source: Nwani in the 7FAM thread, "edt", confirmed 2026-11-06)
