#!/usr/bin/env python3
"""UserPromptSubmit hook (CLAUDE.md, Check before answering).

Searches the rules and learnings files for the words in Nwani's message and shows Claude
the best-matching lines before it answers, so a settled fact or rule doesn't depend on
Claude remembering to look it up.

When Nwani's message is a question, it also puts a reminder at the top: answer it, and take no
action beyond what answering needs, unless Nwani asked. Claude once turned "why didn't you look"
into a lookup, before the reviewer could see anything (Nwani's Save card, 2026-11-11). It's a
reminder, not a block, because a hook can't tell which lookups an answer needs.
"""
import html
import json
import os
import pathlib
import re
import sys

FILES = ["CLAUDE.md", "learnings.md", "projects/*/CLAUDE.md", "projects/*/learnings.md"]
MAX_LINES = 8
STOP = set("""about after again also and any are because been before being but can cant could did didnt
does doesnt dont each even for from get had has have how into its just like make more most much need
not now off one only other our out over said same should some still such than that thats the their them
then there these they this those through too under use very want was way were what when where which
while who why will with would yes you your youre the card decision asking chose option""".split())


def message(prompt):
    m = re.search(r'<message[^>]*trigger="true"[^>]*>(.*?)</message>', prompt, re.S)
    return html.unescape(m.group(1) if m else prompt)


def words(text):
    return {w.rstrip("s") if len(w) > 4 else w for w in re.findall(r"[a-z0-9]+", text.lower())
            if len(w) >= 3 and w not in STOP}


QUESTION_START = re.compile(
    r"^(why|how|what|whats|when|where|who|which|did|didnt|do|does|doesnt|dont|is|isnt|are|arent|was|wasnt|"
    r"were|werent|has|hasnt|have|havent|should|shouldnt)\b")
ASKS_FOR_ACTION = re.compile(r"\bplease\b")
REMINDER = ("This is a question. Answer it, and take no action beyond what answering needs, and change "
            "nothing, unless Nwani asked (CLAUDE.md, Answer by click, and Nwani's Save card 2026-11-11).")


def is_question(text):
    """A message that asks something rather than asking for something to be done."""
    plain = re.sub(r"[^a-z0-9 ?]", "", text.lower()).strip()
    if not plain or ASKS_FOR_ACTION.search(plain):
        return False
    return plain.endswith("?") or bool(QUESTION_START.match(plain))


def folders(start):
    """The folder the thread started in, plus each repo right under it, since a project with
    several repos starts in the folder above them."""
    return [start] + sorted(p for p in start.iterdir() if p.is_dir() and (p / "CLAUDE.md").is_file())


def matches(start, text):
    terms = words(text)
    lines = []
    for root in folders(start):
        for pattern in FILES:
            for path in sorted(root.glob(pattern)):
                for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                    if line.strip() and not line.startswith("#"):
                        lines.append((path.relative_to(start), n, line.strip(), words(line)))
    # A word found on few lines counts for more than one found on many.
    spread = {t: sum(1 for l in lines if t in l[3]) for t in terms}
    scored = []
    for path, n, line, found in lines:
        score = sum(1 / spread[t] for t in terms & found)
        if score:
            scored.append((score, path, n, line))
    scored.sort(key=lambda s: -s[0])
    return scored[:MAX_LINES]


def main():
    hook = json.load(sys.stdin)
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or hook.get("cwd") or ".")
    said = message(hook.get("prompt") or "")
    found = matches(root, said)
    parts = [REMINDER] if is_question(said) else []
    if found:
        text = "\n".join("%s:%d: %s" % (path, n, line[:300]) for _, path, n, line in found)
        parts.append("Rules and learnings that match this message. Check them before "
                     "answering (CLAUDE.md, Check before answering):\n" + text)
    if parts:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n\n".join(parts),
        }}))


if __name__ == "__main__":
    main()
