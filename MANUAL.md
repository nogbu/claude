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

## Facts Claude can rely on (learnings)

**What it's for:** making sure Claude answers from checked facts instead of guessing, like a fertilizer's dosage or whether a rule exists.

**How you use it:**
- When a fact is settled, ask Claude to add it to the learnings. Each project has its own learnings file, and there's one shared file for facts every project uses.
- Each line holds one fact, where it came from, and when it was confirmed.

**What you'll see:**
- Any number with a unit, like a dosage, size, time or temperature, comes with its source: a learnings line, a link, or the word "unverified".
- If Claude says "unverified", treat it as a guess.

**When it goes wrong:** if Claude gets a fact wrong that's in the learnings, say so. The lookup should have shown it. The likely cause is that the fact uses different words than your message. Adding the word you used to that line fixes it.

**What's behind it:** every time you send a message, a check searches the rules and learnings for the words in it and shows Claude the matching lines before it answers. A second check stops any reply with a number and unit but no source. It also stops a reply that points to a file Claude didn't actually open.

---

## Reviewed answers

**What it's for:** catching the simple wrong deductions you shouldn't have to look for, like ranking a full team against half-drafted ones, before you see them.

**How you use it:** nothing to do. When you catch a mistake that got through anyway, say so. Claude adds that kind of mistake to the review checklist, so every later answer is checked for it.

**What you'll see:**
- Answers that say plainly when the data can't support what you asked, instead of answering anyway.
- Longer answers take a little more time, because a second Claude checks them first.

**When it goes wrong:** the reviewer is also Claude, so it can miss things. Each miss you report becomes a checklist line, so the same kind of miss gets caught next time.

**What's behind it:** a separate helper (Opus, high effort) gets your message, the conversation and Claude's draft. Its only job is to find what's wrong: whether the draft reaches your actual goal, what it assumed without checking, what's missing, and anything on the review checklist. A check refuses any reply longer than 40 words unless the reviewer's report came back first. Short replies like "Saving now" skip it.

---

## Speed and usage (optimization)

**What it's for:** keeping Claude fast and cheap without making answers worse.

**How you use it:**
- Ask for a usage report on any thread to see how long it took and how much it used.
- Ask for an audit any time. Claude goes through the optimization checklist item by item and brings you its best findings on cards.

**What you'll see:**
- Every speed or cost recommendation comes with real numbers from the usage report, and the same numbers again after the change so you can see whether it helped.
- Any change that would make Claude read or check less says what it could miss. If it could miss anything important, Claude doesn't recommend it.

**When it goes wrong:** if a recommendation has no numbers, or an obvious idea is missing, say so. The fix is to add the missing idea to the checklist so every later audit checks it.

**What's behind it:** a usage script reads the thread's own record. The checklist was written from Anthropic's documentation, so you don't have to know how Claude works inside to get good recommendations.

---

## Helpers and skills

**What it's for:** letting you decide how much horsepower each predefined task gets.

**How you use it:** when Claude sets up a reusable helper or skill (like the audit), it asks you on a card which model and effort level the task should use, with its recommendation. Pick one.

**Good to know:** the task runs at its own level, so your thread's level doesn't change and nothing has to be switched back.

**What's behind it:** a written rule, plus a check that refuses to save a helper or skill file that doesn't name both.

---

## Automatic checks (hooks)

**What they're for:** catching mistakes that can be spotted with a simple test, so they don't depend on Claude remembering a rule.

**How they work:** a hook is a small program that runs at a set moment, like right before Claude sends a reply. It checks one simple thing. If the check fails, Claude is stopped and told why, then fixes it before you see anything.

**Hooks or written rules:** if something can be checked with a simple yes/no test, it should be a hook. If it needs judgment, like "keep replies short," it stays a written rule.

**Checks in place:**
| Check | What it stops |
|---|---|
| Lookup | Nothing. It shows Claude the rules and learnings that match each of your messages. |
| Reply check | Replies, and edits of sent replies, that ask you a question in text, use semicolons, have a "Still open:" line without bullets, give a number and unit with no source, or point to a file Claude didn't open |
| Card check | Cards with text in the context box |
| Helper check | Saving a helper or skill that doesn't name its model and effort level |
| Open-cards check | Turns that end without bringing back an unanswered card |
| Review check | Replies and edits longer than 40 words that the reviewer didn't check first |

**Where they come from:** project threads don't run a repo's own hooks or helpers ([Projects docs](https://code.claude.com/docs/en/claude-projects#what-threads-pick-up-from-your-repositories)). So the checks and the reviewer come as one plugin, house-rules, built from this repo, which keeps the master copy.

**What each project needs:** the `nogbu/claude` repo in its repositories, for the rules and learnings. The checks only act in threads that have that repo, so a project without it isn't affected. The plugin is on your claude.ai account, and this project's threads picked it up from there with no project setting (tested 2026-10-23). Other projects should get it the same way, but that hasn't been tested yet.

**When a check changes:** saving the change to this repo also rebuilds the plugin's copy in it, through a GitHub Action, a small job GitHub runs on every change. The plugin is added from this repo on your [Plugins page](https://claude.ai/customize/plugins), so new threads should get the change. Whether they get it on their own, or you have to update it on that page, is still being tested.

**When it goes wrong:** if a check should have stopped something and didn't, the plugin may be missing or out of date. Say so, and Claude checks which.

---

## Coming later

These are planned but not built. Each gets its own section here once it exists.
- **Save check:** an automatic check that rules can only change after you click Save.
- **Manual check:** an automatic check that refuses a rule or hook change unless this manual is updated too.
- **Weekly audit:** an audit that runs on its own every week and brings you its top three findings on cards.
- **Project folders:** each project (plantagram, 3dp and others) gets its own rules, separate from the shared ones.
