---
name: product
description: Load for any product work (a 3D design, recipe, meal or exercise plan, keyword list or other work spanning threads), before building one, and when my first message is "resume [product]" (misspellings count).
---
## Product docs
- Work spanning threads gets a product folder, projects/[project]/products/[name]/, whose doc, state.md, holds current state only: Product rules, latest rev, every value needed to rebuild it with its script, decisions and why, open questions, each with the intent behind it (what a pending change is for and which way it goes), numbered agreed changes (each with its purpose and sizes), the next step and the script's path.
- When a product comes up, read its doc first. Without one, search projects/[project]/ by name and topic before offering one.
- Log: parked designs, explored alternatives and history whose conclusions the doc carries move unchanged to the folder's log.md, newest first, each under a heading (title; parked, alternative or history; date; what would bring it back), with a reason in Decisions for a rejected alternative. Move text either way as it stops or starts being current, saying what moved. Read the log only before a build, at an item's trigger, for a value the doc lacks, for entries a dp-audit cites, or when I ask. Dropping or rewriting logged text needs my yes. Retired products' folders move to products/retired/.
- Log what's no longer current as it stops being current; check.py's 1,500-word cap only warns, so never tighten a doc just to fit it.

## Resume
On "resume [product]", find the doc in the index by short name or description (several matches: ask; none: list the short names). Read only the doc, then post a "Where we left off:" card, one open thread per option (questions, pending decisions, unbuilt changes), grouped to fit, the most recent recommended unless it waits on another open item (a part not yet designed, an unconfirmed measurement); then recommend that item. Before offering to print a built, unprinted piece, check it against design-principles.md if they changed since it was built (git log).

## Building
- Before building or asking to build: list logged items the build touches or should revive, and the build's and design's open decisions (layout, plates, counts, names); resolve each with me, never by default; apply all agreed changes in one pass.
- While iterating, don't rebuild after each agreed change.
- Commit each built file's script, named after its file, to the product's build/ folder with any data file it reads.
- Name builds "name_rev10.ext", test variants "name_rev9.2_short-label.ext", and refer to them by rev ("rev9.7"). Save built files to /mnt/project-files/[type]/ and attach them.
- Only "save [x] as final" makes something final; never ask. Name it "name_final.ext" (built files in [type]/finals/).
- Compute derived values from the build script's geometry, not a hand model, and confirm what a test result came from (material, settings, method) before building on it. Read how physical equipment is built before writing steps for it.
