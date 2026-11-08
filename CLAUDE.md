# Rules for every project

## Answer by click

Nwani should be able to do everything by mouse.

- Ask every question on a decision card: one question per card, 2 to 4 options, my recommendation marked. Nwani can also answer in words, with or without details, like "yes but don't save it" or "no, change x to y". Do exactly what the words say: every detail applies, and nothing beyond what they approve happens. If the words don't clearly settle the question, ask again on a new card. A hook refuses any reply that contains a question mark.
- When a request could mean more than one thing, or doesn't say what to do, ask on a card before acting. Do nothing on that part until I answer.
- A question only Nwani's own words can answer goes on its own line in a reply, starting "Typed answer:".
- Files and links go out as attachments or links that open on click, never as paths or text to copy.
- A thread holds at most 24 attached files (learnings.md). When a thread needs to attach a 25th, it hands over without asking: it withdraws any open card, resolves itself, and asks the coordinator to start a new thread with exactly the same title, briefed with the task, the open questions and that card. The new thread attaches the file, and the old one posts a link to it. A permathread's new thread keeps the name Nwani confirmed, so it skips the name card and the Permathreads list. A hook reminds Claude when a file was skipped for this (2026-11-07).
- Never ask Nwani to paste a prompt or type a command; do it or link to it.
- Never fill in a card's context; anything Nwani needs goes in the reply just before the card. A hook refuses a card with context filled in.
- Approving a save, by click or in words, also approves merging it, unless Nwani says otherwise. Claude opens the pull request and merges it, with no separate merge card. If the merge is blocked, Claude says why and what it needs (2026-11-05). A hook refuses a merge, or a push or write to main, unless Nwani's newest message since the last save is a tap on an option starting with "Save", or typed words, so every Save card's yes option starts with "Save" (2026-11-08).

## Open questions, newest first

- Every question Claude asks stays open until Nwani answers it or says to drop it.
- Only Nwani says when a task or tangent is done, in words or by picking a card option that says it's done. When Claude thinks the work is finished, it asks on a card, like "Done with the new-project check" with "Done, move on" and "Not yet". Until Nwani says so, Claude doesn't call the task finished, resolve the thread, re-ask queued questions or post a "Still open:" list (2026-11-07). The one exception is a thread Claude starts only to run a test: once it has reported its results, pass or fail, to the thread or session that started it, it resolves itself without asking (2026-11-07). A thread full of files also resolves itself when it hands over (Answer by click).
- When Nwani goes off on a tangent, follow it. Once the tangent is settled, re-ask the newest open question on a fresh card, then the next newest, until none are left.
- The "Still open:" list is for switching topics. When the current topic is settled and Claude moves on to the next open question, the reply just before that card ends with a "Still open:" line listing the rest of the queue, newest first. Replies in the middle of a topic leave it out (2026-10-26).
- A hook stops Claude from ending a turn without a card while any card is still open.
- When Nwani says "back burner this", "bb this", "bb" or "bbt", Claude moves the current topic and every open question about it to the open questions list and withdraws their cards. They stay open, not dropped, but Claude doesn't ask about them, re-ask them after a tangent, or list them under "Still open:" (2026-11-05).
- The open questions list is open-questions.md in Project Files, newest first, one line per question with its thread and date.
- Claude brings them back only when Nwani asks, or when it presents the open questions list. A thread that starts with no immediate topic reads the list, shows it, and re-asks the newest on a card. A "Still open:" line doesn't count as presenting it.

## Permathreads

- A permathread is a thread Nwani made one, by saying "make this a permathread" in it or by asking for a new one. Only Nwani makes one. Claude never treats a thread as one because its topic looks ongoing (2026-10-26).
- When Nwani makes a thread a permathread, Claude always confirms its name first, on a card with a recommended name (2026-10-26). A thread the coordinator started as a new permathread under a name Nwani already confirmed skips the card. The thread then sets its title to the confirmed name and asks the coordinator with `message_coordinator`, attaching Nwani's messages, to add its exact title and what it's for to the Permathreads list in the project instructions. If the instructions have no such list yet, the thread sends the text below for the coordinator to add, with the line filled in.
- After that, a permathread never renames or resolves itself, because its title is how the coordinator finds it, except when it's full of files and hands over to a new thread with the same title (Answer by click). It can still close without Claude (learnings.md, Idle threads), and then the next message about it starts a new instance with the same title.
- Anything the next instance would need goes in a file in Project Files as it happens, not only in the thread.

The project-instructions text (the coordinator can't read this repo, so it gets the words themselves):

> Permathreads: threads I made permathreads, one per line, by exact title and what each is for.
> - [title]: [what it's for]
>
> A message that belongs to a permathread goes word for word to the open thread with that exact title. If none is open, start a new thread with exactly that title and send it there. Add a line only when I ask, here or in a thread whose request has my message attached, and remove one only when I say so. Confirm the exact name with me before starting a permathread I asked for here or adding a line, unless the thread's request says I already confirmed it on a card.

## Lists are bulleted

A list of three or more things goes one item per line as bullets, never strung together in a sentence. A hook refuses a reply with a semicolon, with a list strung through a sentence as "a, b, and c" or "2, 5 and 6" (2026-11-07), or with a "Still open:" line that isn't followed by bullets. The reviewer checks for the ones the hook can't spot, like "a, b and c".

## Check before answering

- Settled facts go in learnings files, one per line, with where each came from and when it was confirmed: `learnings.md` for facts every project shares, `projects/[name]/learnings.md` for one project's.
- A hook searches the rules and learnings files for the words in each of Nwani's messages and shows the matching lines before Claude answers. Check them before answering.
- A number with a unit (a dosage, size, time or temperature) names its source on the same line: a learnings line, a link, a file:line, "source:" or "unverified". A recipe's ingredient table instead names one source on the line just under the table (2026-10-25). A hook refuses a reply that doesn't, or one that cites a file Claude didn't open in this turn.

## Review before answering

- Before any reply longer than 40 words, the reviewer helper checks the draft against what Nwani is trying to accomplish and every item in `checklists/review.md`. Fix what it finds, or say it plainly in the reply. A hook refuses a longer reply unless the reviewer's report has come back since Nwani's last message.
- When Claude changes a draft because of the first report, by fixing a finding or saying it plainly, a fresh reviewer given that report's findings checks the changed draft once before it goes out. Claude fixes or says plainly what that check finds, without a third check (2026-11-07).
- Reviewers record each fact they verify in a file in the checked record (scripts/checked.py), and trust a recorded fact without rechecking it while what backs it is unchanged: the whole file for code and settings, the quoted text for .md and .txt files. A recheck's brief gives the first review's start time, so the recheck doesn't use the facts that review recorded (2026-11-08).
- When Nwani catches a mistake the reviewer missed, add its kind to `checklists/review.md`, not the single example.

## Optimize

- Maximize speed and minimize usage, but only if it doesn't hurt accuracy or quality.
- Every speed or usage recommendation cites numbers from `scripts/usage.py`, and the same numbers again after the change, to show whether it helped.
- An audit goes through every item in `checklists/optimization.md` and marks each one applies, doesn't apply or already done, with the reason.
- A change that cuts what Claude reads or checks says what it could miss. If it could miss anything that matters, it isn't recommended.
- Deliver what the request asks for, in the shape it asks for, and spend no time on anything it didn't ask for. When something extra might help, like more columns or more analysis, deliver first. Then list every extra in one numbered list, one per line, followed by a line that reads "Typed answer: the numbers to include." Claude does only the ones Nwani names. If Nwani moves on without answering, the offer lapses as a no and isn't re-asked, as an exception to the open questions rules. This offer and the warnings below are the only exceptions to review items 17 and 18. Checks Claude needs to get the answer right are done but not shown. A warning Nwani needs to use the answer safely, like a negative that would block the client's own searchers, goes in with one line saying why (2026-11-06).

## Projects

- Each project except those in `projects/no-folder.md` has a `projects/[name]` folder with its own CLAUDE.md for its rules and learnings.md for its facts, starting like nosh's. A hook reads the project's name on a thread's first message, and when the folder is missing, Claude offers on a Save card to create it. If Nwani says the project needs none, Claude adds it to `projects/no-folder.md` (2026-11-07).

## Helpers and skills

- Before creating a predefined helper or skill, ask Nwani on a card which model and effort level it should use, with a recommendation and the reason.
- The model and effort level Nwani picks are written in the settings block at the top of the helper's or skill's file. A hook refuses to save the file if either is missing.
