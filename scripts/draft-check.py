#!/usr/bin/env python3
"""Checks a draft reply before it goes to the reviewer (CLAUDE.md, Lists are bulleted).

Usage: python3 scripts/draft-check.py draft.txt   (or the draft on stdin)

Runs the reply hook's own checks, then stricter list checks the hook leaves out because they
would refuse some ordinary sentences. Here a false alarm only costs a look, so they flag:
- "a, b and c": three items with no comma before "and"/"or"
- steps joined by "then": "do a, then b, then c", "a, then b and c" or "a, b, then c"
- lists of long clauses: "a, b, and c" where an item runs up to 12 words
It also flags sweeping claims like "no record shows" or "was never" in a sentence that doesn't
say what was searched, since such a claim usually covers only what Claude looked at (2026-11-18).
Prints each finding and exits 1, or prints nothing and exits 0.
"""
import importlib.util
import os
import re
import sys

HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "hooks")
sys.path.insert(0, HOOKS)
spec = importlib.util.spec_from_file_location("reply_check", os.path.join(HOOKS, "reply-check.py"))
reply_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reply_check)

WORD = reply_check.WORD
JOINER = reply_check.JOINER
# A first item that is really a sentence opener, like "Yes, merged and uploaded".
OPENER = r"(?:yes|no|ok|okay|so|well|also|now|still|sure|thanks|right|first|next|then|here|again|instead)\b"
ITEM = r"(?!%s)%s" % (JOINER, WORD)
# A second part that starts like this is a clause, not a list item: "requested, with the card and notes".
SUBORD = r"(?:with|without|since|as|though|although|when|if|unless|after|before|until|for|from|by|in|on|at|to|where|whose|whom|even|just|only|not|plus)\b"
STRICT = [
    ("three items with no comma before and/or",
     re.compile(r"(?<![\w,-])(?!%s|[^,\n]*\d)%s(?:\s+%s){0,3},\s+(?!%s|%s|%s)%s(?:\s+%s){0,3}\s+(?:and|or)\s+%s"
                % (OPENER, WORD, ITEM, JOINER, reply_check.PRONOUN, SUBORD, WORD, ITEM, WORD), re.I)),
    ("steps joined by then",
     re.compile(r"\bthen\b[^.\n]{1,80}?,\s+(?:and\s+)?then\b|,\s+then\b[^.\n]{1,80}?(?:,\s+|\s+and\s+)(?:and\s+|then\s+)?\w"
                r"|\w,\s+(?!%s)[^,.\n]{1,40},\s+then\s+\w" % SUBORD, re.I)),
    ("a list of long clauses",
     re.compile(r"%s,\s+(?!%s)%s(?:\s+%s){0,11},\s+(?:and|or)\s+%s" % (WORD, SUBORD, ITEM, ITEM, WORD), re.I)),
]
# Sweeping claims, and the words that show a sentence already names what was searched.
ABSOLUTE = re.compile(
    r"\b(?:no (?:record|sign|trace|evidence|case|instance|example)s?\b|nothing (?:shows|showed|in)\b"
    r"|none of\b|not once\b|(?:has|have|had|was|were|is|are|did)\s+never\b"
    r"|never (?:happened|ran|runs|shows|showed|appears|appeared|came|comes|fired|fires)\b"
    r"|every (?:record|thread|session|time)\b|all (?:records|threads|sessions)\b)", re.I)
SCOPE = re.compile(
    r"\b(?:this|that|the) (?:thread|session|record|file|test|repo|folder|chat)\b|\bthis thread's\b|\bsearched\b"
    r"|\bchecked\b|\bI (?:looked|read|listed)\b|\bin [\w./-]+\.(?:md|py|jsonl|txt|json)\b|\bsource:", re.I)
SENTENCE = re.compile(r"[^.!\n]+[.!]?")
CONDITION = re.compile(r"(?:^|[.!:]\s+|\W)(?:if|once|when|whenever|after|before|unless|since)\b[^.,\n]*$", re.I)


def findings(text):
    found = []
    hook = reply_check.problem(text)
    if hook:
        found.append(hook)
    plain = text
    for pattern in reply_check.IGNORED:
        plain = pattern.sub(" ", plain)
    for line in plain.splitlines():
        if reply_check.BULLET.match(line) and len(line) < 60:
            continue
        for name, pattern in STRICT:
            m = pattern.search(line)
            if (m and name == "steps joined by then" and CONDITION.search(line[:m.start()])
                    and len(re.findall(r"\bthen\b", m.group(0), re.I)) < 2):
                m = None  # "If it passes, then I merge it and tell you" is one step after a condition
            if m:
                found.append("Possible list strung through a sentence (%s): \"%s\". Put it on bullets "
                             "or reword, unless it isn't a list." % (name, m.group(0)[:120]))
                break
    for sentence in SENTENCE.findall(plain):
        m = ABSOLUTE.search(sentence)
        if m and not SCOPE.search(sentence):
            found.append("Sweeping claim (\"%s\"): \"%s\". Name what was searched in the same sentence, "
                         "or narrow the claim." % (m.group(0), sentence.strip()[:120]))
    return found


def main():
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    out = findings(text)
    for f in out:
        print(f)
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
