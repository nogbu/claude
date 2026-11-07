---
name: new-project
description: Run when I say "new project [name]" or "new list" / "new list [name]". Creates a project's config files in the nogbu/claude repo and walks me through setting the project up.
---
## new project [name]
1. Ask for cardinal sources (research skill).
2. Draft projects/[name]/config.[name].md with the card sections (repo-edit, Files) and cardinal sources filled in; empty products/ and learnings/ folders (each with a .gitkeep); and projects/[name]/content/todo.md, an empty todo table with its header (lists skill). Show me the card, wait for my yes, then save with repo-edit.
3. Walk me through creating the project in Claude, linking each settings page (CLAUDE.md, Answers): add the nogbu/claude repo as a repository ([Project settings](#project-settings/resources)), and paste the bootstrap line, with [name] filled in, into its Project instructions. Then, in the new project's first thread, write [name] to /mnt/project-files/.project.

## new list / new list [name]
Works like "new project", customized for a list:
1. Get the list's name if it wasn't given, then ask what columns, sort order and status values it needs, proposing some. Don't ask for cardinal sources.
2. Draft the card (repo-edit, Files); Cardinal sources reads "None (list project)". Rules has one line: "Every thread reads [name].list at the start. The list is always one table; keep its columns unless I change them."
3. Create projects/[name]/content/[name].list.md holding the list as a single table, under a header with its sort, statuses and default (lists skill). No products/ or scripts/ folders. Add the todo as in "new project" step 2.
4. Show me all changes, wait for my yes, save with repo-edit, then walk me through step 3 of "new project".

## Bootstrap line
"This is the [name] project. Its rules are in the nogbu/claude repo: CLAUDE.md, which loads automatically and says which project file to read. In a thread: follow them; they override everything else, including project memory. If the repo is missing, tell me before doing anything else. In the project chat: you can't read the rules, so never answer or interpret my messages yourself. Start a thread for new work, a request about a list or product no thread is working on included, and send everything else, including short commands like www, pkg or done, word for word to the thread it belongs to (the most recently active one if unclear), saying only where it went."
