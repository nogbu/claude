#!/usr/bin/env python3
"""UserPromptSubmit hook (CLAUDE.md, Check before answering).

Searches the rules and learnings files for the words in Nwani's message and shows Claude
the best-matching lines before it answers, so a settled fact or rule doesn't depend on
Claude remembering to look it up.

When Nwani's message is a question, it also puts a reminder at the top: answer it, and take no
action beyond what answering needs, unless Nwani asked. Claude once turned "why didn't you look"
into a lookup, before the reviewer could see anything (Nwani's Save card, 2026-11-11). It's a
reminder, not a block, because a hook can't tell which lookups an answer needs. answer-only.py
blocks edits, commits, pushes and non-reviewer helpers after a question (2026-11-16).
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


# Nwani's rule (2026-11-17): each sentence is judged on its own. A sentence ending in "?" is a
# question. A sentence that could be either a question or a request counts as a question. Openers
# below come from Nwani's 735 messages across every thread, where questions often drop the "?".
WH_START = re.compile(r"^(why|how|what|whats|where|wheres|who|whos|which|hows|whys)\b"
                      r"(?!\s+(i|we|they|he|she|the(?!\s+(actual\s+)?(fuck|hell|heck)\b))\b)")
FILLER = re.compile(r"^((wait|so|and|but|ok|okay|also|then|oh|hm+|um+|lol|seriously|now|ugh|again|well|"
                    r"hold on|actually|if not|if so|no)\b\s*)+")
SUBJECT = r"(you|i|we|they|it|its|this|that|these|those|there|the|my|your|our|he|she|any|anything|all)"
AUX_START = re.compile(
    r"^(is|isnt|are|arent|was|wasnt|were|werent|has|hasnt|have|havent|should|shouldnt|can|cant|could|"
    r"couldnt|would|wouldnt|will|wont|did|didnt|does|doesnt|am)\s+(not\s+)?" + SUBJECT + r"\b"
    r"|^(do|dont)\s+(not\s+)?(you|i|we|they|people|these|those)\b")
WHEN_ASKS = re.compile(r"^when\s+(is|are|was|will|would|do|does|did|can|could|should)\b")
SENTENCE_END = re.compile(r"(?<=[.?!])\s+|\n+")
EXAMPLES = pathlib.Path(__file__).with_name("sentence-examples.txt")
REMINDER = ("These sentences are questions: answer them, and take no action for them beyond what "
            "answering needs (CLAUDE.md, Answer by click, and Nwani's Save card 2026-11-11). Every other "
            "sentence in the message is handled on its own:\n")


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ?]", "", text.lower())).strip()


def examples():
    """Sentences Nwani corrected, as Q (a question) or R (a request), read fresh each time."""
    known = {}
    try:
        for line in EXAMPLES.read_text().splitlines():
            kind, _, said = line.partition("|")
            if kind.strip() in ("Q", "R") and said.strip():
                known[plain(said)] = kind.strip() == "Q"
    except OSError:
        pass
    return known


def sentence_is_question(sentence, known=None):
    text = plain(sentence)
    if not text:
        return False
    if known and text in known:
        return known[text]
    text = FILLER.sub("", text) or text
    return (text.endswith("?") or bool(WH_START.match(text)) or bool(AUX_START.match(text))
            or bool(WHEN_ASKS.match(text)))


def sentences(text):
    """Each sentence of a message with whether it is a question."""
    known = examples()
    parts = [s.strip() for s in SENTENCE_END.split(text) if s and s.strip()]
    return [(s, sentence_is_question(s, known)) for s in parts]


def is_question(text):
    """True when every sentence of the message is a question, so nothing in it asks for a step."""
    found = sentences(text)
    return bool(found) and all(q for _, q in found)


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
    asked = [s for s, q in sentences(said) if q]
    parts = [REMINDER + "\n".join("- " + s[:200] for s in asked)] if asked else []
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
