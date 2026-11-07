---
name: lists
description: Load for any list or table of items (a todo, hopper.list, a plant inventory) and on "list [short name]", "list products", "dir", or "add [x] to todo" / "2d" / "td".
---
## List docs
- A list doc is a content file holding one list or table. Its header gives sort (the columns it sorts by), statuses (in order) and default (the status of new rows). Its rules header field holds its add commands, any scan and any other rule for it alone; those win over this skill.
- Change a list only with shared/scripts/list.py (show, add, done, set, remove or sort), then save with repo-edit. Edit by hand only what list.py can't do, then run its sort.
- "list [short name]": run any scan its rules field names, then show it with list.py.

## Todo
- Every project has a todo, projects/[project]/content/todo.md: columns Task, For (me or Claude), Status (open or done), Added; sorted open first, then oldest first.
- "add [task] to todo" (or "2d", "td") adds an open row, For me unless it's Claude's task, and confirms it.

## Products
"list products" / "dir": list the short names of the product docs in the file index (index.py), one per line, with what each holds in a few words. In admin, list each project's products under its name. In a list project, run "list [name]" instead.
