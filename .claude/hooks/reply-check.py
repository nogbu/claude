#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Answer by click, Lists are bulleted and
Check before answering). Widgets are checked too, by the words they show (shown_text.py).

After code, quoted lines, text in quotation marks and links are set aside, a reply is refused when:
- a line has a "?" and doesn't start with "Typed answer:" (message drafts for other people may ask)
- in a widget, a source in its stand-in line, title or summary covers every number in it, like a chart's labels
- it has a semicolon
- a "Still open:" line isn't followed by bullets
- a line states a number with a unit but names no source: a link, a file:line, "source:" or "unverified"
- it cites a file:line from a file that wasn't opened in this turn
"""
import json
import re
import sys

from shown_text import shown

IGNORED = [
    re.compile(r"```.*?```", re.S),          # code blocks
    re.compile(r"`[^`\n]*`"),                # inline code
    re.compile(r"^\s*>.*$", re.M),           # quoted lines
    re.compile(r'"[^"\n]*"'),                # "straight quotes"
    re.compile(r"“[^”\n]*”"),                # “curly quotes”
    re.compile(r"\]\([^)\s]*\)"),            # markdown link targets
    re.compile(r"https?://\S+"),             # bare links
]
QUOTED = IGNORED[:5]  # code and quotes, but not links: links count as sources
UNIT = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|°\s?[CF]\b|(?:ml|l|liters?|litres?|tsp|tbsp|teaspoons?|tablespoons?|"
                  r"cups?|gallons?|gal|oz|ounces?|g|grams?|kg|mg|lbs?|pounds?|ppm|mm|cm|inch(?:es)?|ft|feet|kb|mb|gb|"
                  r"degrees?|sec(?:ond)?s?|min(?:ute)?s?|hrs?|hours?|days?|weeks?|months?)\b)", re.I)
SOURCE = re.compile(r"\]\(|https?://|[\w./-]+\.\w+:\d+|\bsource:|\bunverified\b", re.I)
CITATION = re.compile(r"([\w./-]+\.\w+):\d+")
TYPED = re.compile(r"^[\s*_]*Typed answer:")
STILL_OPEN = re.compile(r"^[\s*_]*Still open:[*_]*(.*)$")
BULLET = re.compile(r"^\s*[-*•]\s")


def opened_this_turn(transcript_path):
    """Everything Read, Grep, Glob or Bash were pointed at since Nwani's last message."""
    seen = []
    try:
        with open(transcript_path) as f:
            for line in f:
                entry = json.loads(line)
                content = (entry.get("message") or {}).get("content")
                if entry.get("type") == "user" and entry.get("isMeta"):
                    continue  # harness notes, like a helper's report, aren't Nwani's messages
                if entry.get("type") == "user" and isinstance(content, str):
                    seen = []
                elif entry.get("type") == "assistant" and isinstance(content, list):
                    for block in content:
                        if block.get("type") == "tool_use" and block.get("name") in ("Read", "Grep", "Glob", "Bash"):
                            seen.append(json.dumps(block.get("input")))
    except (OSError, ValueError):
        pass
    return " ".join(seen)


def problem(text, transcript_path=None, questions_ok=False, sourced=False):
    plain = text
    for pattern in QUOTED:
        plain = pattern.sub(" ", plain)
    for line in plain.splitlines():
        if UNIT.search(line) and not SOURCE.search(line) and not sourced:
            return ("A number with a unit names its source on the same line: a learnings line, a link, "
                    "a file:line, \"source:\" or \"unverified\" (CLAUDE.md, Check before answering). Found: "
                    "\"%s\"." % line.strip()[:120])
    cited = set(CITATION.findall(plain))
    if cited and transcript_path:
        opened = opened_this_turn(transcript_path)
        for path in sorted(cited):
            if path.split("/")[-1] not in opened:
                return ("You cited %s but didn't open it in this turn. Open it and check the line "
                        "before citing it (CLAUDE.md, Check before answering)." % path)
    for pattern in IGNORED:
        text = pattern.sub(" ", text)
    lines = text.splitlines()
    for line in lines:
        if "?" in line and not TYPED.match(line) and not questions_ok:
            return ("Questions go on a decision card, not in a reply (CLAUDE.md, Answer by click). "
                    "Found: \"%s\". If only Nwani's own words can answer it, put it on its own line "
                    "starting \"Typed answer:\"." % line.strip()[:120])
    for line in lines:
        if ";" in line:
            return ("No semicolons in replies (CLAUDE.md, Lists are bulleted). Found: \"%s\". "
                    "Put a list of three or more items on bullets, or split the sentence." % line.strip()[:120])
    for i, line in enumerate(lines):
        m = STILL_OPEN.match(line)
        if m:
            rest = [l for l in lines[i + 1:] if l.strip()]
            if m.group(1).strip() or not rest or not BULLET.match(rest[0]):
                return ("Put each item after \"Still open:\" on its own bullet line (CLAUDE.md, "
                        "Lists are bulleted).")
    return None


def main():
    hook = json.load(sys.stdin)
    parts, heading = shown(hook)
    sourced = bool(SOURCE.search(heading))
    reason = next(filter(None, (problem(text, hook.get("transcript_path"), ok, sourced) for text, ok in parts)), None)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))


if __name__ == "__main__":
    main()
