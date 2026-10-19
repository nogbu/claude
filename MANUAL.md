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
- Everything you need to decide is in the message just above the card. The card itself only has the question and the buttons.

**What you'll see:** questions on cards, not buried in paragraphs.

**When it goes wrong:**
- If Claude asks a question in plain text, the system should have stopped it. Say so, and Claude will check why the safety check didn't catch it.
- Known gap: a question inside quotation marks can slip through.

**What's behind it:** a written rule tells Claude to use cards. An automatic check (a hook) reads every reply before it's sent and stops any reply with a question mark in it. Another check stops any card with text in its context box, because the app often doesn't show that box.

---

## Going off on tangents (open questions)

**What it's for:** letting you follow any tangent without losing track of the questions you haven't answered yet.

**How you use it:**
- Ignore a card whenever you like and ask or say something else. Claude follows you.
- Once the tangent is settled, Claude brings back the newest unanswered question on a fresh card. When you answer it, Claude brings back the next newest, and so on until nothing is left.
- To get rid of a question, answer it, or say to drop it.

**What you'll see:** the message just above each card ends with a **Still open:** list of everything else waiting, newest first.

**When it goes wrong:** if a turn ends without bringing back an open question, say so. The check below should have caught it.

**What's behind it:** at the end of every turn, a check reads the thread's own record of cards. If any card is still unanswered and the turn didn't end on a card, Claude is stopped and told which one to bring back. It only stops a turn once, so it can't get stuck in a loop.

---

## How Claude writes lists

**What it's for:** lists that are easy to scan.

**What you'll see:** any list of three or more things is a bulleted list, one item per line, never strung together in a sentence.

**When it goes wrong:** a list written with commas can still slip through. Point it out.

**What's behind it:** a written rule, plus a check that stops any reply with a semicolon (the usual way Claude strings items together) or a "Still open:" line without bullets under it.

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
| Reply check | Replies that ask you a question in text, use semicolons, or have a "Still open:" line without bullets |
| Card check | Cards with text in the context box |
| Open-cards check | Turns that end without bringing back an unanswered card |

**When it goes wrong:** hooks only work when the `nogbu/claude` repo is the only repo in a project. If it's not, they silently don't run.

---

## Coming later

These are planned but not built. Each gets its own section here once it exists.
- **Save check:** an automatic check that rules can only change after you click Save.
- **Manual check:** an automatic check that refuses a rule or hook change unless this manual is updated too.
- **Usage report:** shows how long a thread took and how much it used, so speed and cost recommendations come with real numbers.
- **Weekly audit:** Claude reviews its own setup against a fixed checklist and brings you its top three improvements on cards.
- **Project folders:** each project (plantagram, 3dp and others) gets its own rules, separate from the shared ones.
