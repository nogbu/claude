# User's manual

How to use the systems we've built for working with Claude. Each section covers one system: what it's for, how you use it, what you'll see, and what to do when it goes wrong. This manual is updated whenever a system changes.

---

## Starting work

**What it's for:** keeping each piece of work in its own place.

**How you use it:**
- Post what you want in a project's chat. Claude starts a thread for it on its own.
- Inside a thread, you can say "start a thread for X" and Claude sets it up. You never need to copy or paste a prompt.

**What you'll see:** a new thread under your message, with a checklist showing what Claude is doing.

**Good to know:** each thread starts fresh. It knows the rules and the files, but not what was said in other threads unless it goes and reads them.

---

## Answering Claude (Answer by click)

**What it's for:** letting you do everything with the mouse.

**How you use it:**
- When Claude needs a decision, it shows a **card** with 2 to 4 buttons. One is marked as Claude's recommendation. Click one.
- You can always type instead, with details: "yes but don't save it" or "no, change x to y". Claude does exactly what you write, nothing more.
- If Claude needs something only you can describe, it says **Typed answer:** before the question, so you know a click won't do.
- Files come as attachments and links you can click.

**What you'll see:** questions on cards, not buried in paragraphs.

**When it goes wrong:**
- If Claude asks a question in plain text, the system should have stopped it. Say so, and Claude will check why the safety check didn't catch it.
- Known gap: a question inside quotation marks can slip through.

**What's behind it:** a written rule tells Claude to use cards. An automatic check (a hook) reads every reply before it's sent and stops any reply with a question mark in it.

---

## Approving changes

**What it's for:** making sure rules and safety checks only change when you say so.

**How you use it:**
- Claude shows you the exact change: the new wording, and what it replaces.
- A card asks you to **Save**, **Change** or **Drop**.
- Nothing is saved until you click Save or type it. Changing the subject is not a yes.

**What you'll see:** after you save, a short note confirming what was saved.

**Undoing a change:** ask Claude to undo it. Every save is kept in history, so any change can be reversed.

**What's behind it:** today, Claude follows this as a written rule. An automatic check that enforces it is planned.

---

## Automatic checks (hooks)

**What they're for:** catching mistakes that can be spotted with a simple test, so they don't depend on Claude remembering a rule.

**How they work:** a hook is a small program that runs at a set moment, like right before Claude sends a reply. It checks one simple thing. If the check fails, Claude is stopped and told why, then fixes it before you see anything.

**Hooks or written rules:** if something can be checked with a simple yes/no test, it should be a hook. If it needs judgment, like "keep replies short," it stays a written rule.

**Checks in place:**
| Check | What it stops |
|---|---|
| Question check | Replies that ask you a question in text instead of on a card |

**When it goes wrong:** hooks only work when the `nogbu/claude` repo is the only repo in a project. If it's not, they silently don't run.

---

## Coming later

These are planned but not built. Each gets its own section here once it exists.
- **Save check:** an automatic check that rules can only change after you click Save.
- **Manual check:** an automatic check that refuses a rule or hook change unless this manual is updated too.
- **Usage report:** shows how long a thread took and how much it used, so speed and cost recommendations come with real numbers.
- **Weekly audit:** Claude reviews its own setup against a fixed checklist and brings you its top three improvements on cards.
- **Project folders:** each project (plantagram, 3dp and others) gets its own rules, separate from the shared ones.
