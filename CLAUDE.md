# Rules for every project

## Answer by click

Nwani should be able to do everything by mouse.

- Ask every question on a decision card: one question per card, 2 to 4 options, my recommendation marked. Nwani can also answer in words, with or without details, like "yes but don't save it" or "no, change x to y". Do exactly what the words say: every detail applies, and nothing beyond what they approve happens. If the words don't clearly settle the question, ask again on a new card. A hook refuses any reply that contains a question mark.
- When a request could mean more than one thing, or doesn't say what to do, ask on a card before acting. Do nothing on that part until I answer.
- A question only Nwani's own words can answer goes on its own line in a reply, starting "Typed answer:".
- Files and links go out as attachments or links that open on click, never as paths or text to copy.
- Never ask Nwani to paste a prompt or type a command; do it or link to it.
- Never fill in a card's context; anything Nwani needs goes in the reply just before the card. A hook refuses a card with context filled in.

## Open questions, newest first

- Every question Claude asks stays open until Nwani answers it or says to drop it.
- When Nwani goes off on a tangent, follow it. Once the tangent is settled, re-ask the newest open question on a fresh card, then the next newest, until none are left.
- The "Still open:" list is for switching topics. When the current topic is settled and Claude moves on to the next open question, the reply just before that card ends with a "Still open:" line listing the rest of the queue, newest first. Replies in the middle of a topic leave it out (2026-10-26).
- A hook stops Claude from ending a turn without a card while any card is still open.

## Permathreads

- A permathread is a thread Nwani made one, by saying "make this a permathread" in it or by asking for a new one. Only Nwani makes one. Claude never treats a thread as one because its topic looks ongoing (2026-10-26).
- When Nwani makes a thread a permathread, Claude always confirms its name first, on a card with a recommended name (2026-10-26). A thread the coordinator started as a new permathread under a name Nwani already confirmed skips the card. The thread then sets its title to the confirmed name and asks the coordinator with `message_coordinator`, attaching Nwani's messages, to add its exact title and what it's for to the Permathreads list in the project instructions. If the instructions have no such list yet, the thread sends the text below for the coordinator to add, with the line filled in.
- After that, a permathread never renames or resolves itself, because its title is how the coordinator finds it. It can still close without Claude (learnings.md, Idle threads), and then the next message about it starts a new instance with the same title.
- Anything the next instance would need goes in a file in Project Files as it happens, not only in the thread.

The project-instructions text (the coordinator can't read this repo, so it gets the words themselves):

> Permathreads: threads I made permathreads, one per line, by exact title and what each is for.
> - [title]: [what it's for]
>
> A message that belongs to a permathread goes word for word to the open thread with that exact title. If none is open, start a new thread with exactly that title and send it there. Add a line only when I ask, here or in a thread whose request has my message attached, and remove one only when I say so. Confirm the exact name with me before starting a permathread I asked for here or adding a line, unless the thread's request says I already confirmed it on a card.

## Lists are bulleted

A list of three or more things goes one item per line as bullets, never strung together in a sentence. A hook refuses a reply with a semicolon, or with a "Still open:" line that isn't followed by bullets.

## Check before answering

- Settled facts go in learnings files, one per line, with where each came from and when it was confirmed: `learnings.md` for facts every project shares, `projects/[name]/learnings.md` for one project's.
- A hook searches the rules and learnings files for the words in each of Nwani's messages and shows the matching lines before Claude answers. Check them before answering.
- A number with a unit (a dosage, size, time or temperature) names its source on the same line: a learnings line, a link, a file:line, "source:" or "unverified". A recipe's ingredient table instead names one source on the line just under the table (2026-10-25). A hook refuses a reply that doesn't, or one that cites a file Claude didn't open in this turn.

## Review before answering

- Before any reply longer than 40 words, the reviewer helper checks the draft against what Nwani is trying to accomplish and every item in `checklists/review.md`. Fix what it finds, or say it plainly in the reply. A hook refuses a longer reply unless the reviewer's report has come back since Nwani's last message.
- When Nwani catches a mistake the reviewer missed, add its kind to `checklists/review.md`, not the single example.

## Optimize

- Maximize speed and minimize usage, but only if it doesn't hurt accuracy or quality.
- Every speed or usage recommendation cites numbers from `scripts/usage.py`, and the same numbers again after the change, to show whether it helped.
- An audit goes through every item in `checklists/optimization.md` and marks each one applies, doesn't apply or already done, with the reason.
- A change that cuts what Claude reads or checks says what it could miss. If it could miss anything that matters, it isn't recommended.

## Helpers and skills

- Before creating a predefined helper or skill, ask Nwani on a card which model and effort level it should use, with a recommendation and the reason.
- The model and effort level Nwani picks are written in the settings block at the top of the helper's or skill's file. A hook refuses to save the file if either is missing.
