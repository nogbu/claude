#!/usr/bin/env python3
"""PreToolUse hook on thread replies (CLAUDE.md, Review before answering).

Refuses a reply, edit or widget longer than a short acknowledgment unless the reviewer helper ran and finished
since Nwani's last message. Text copied unchanged from a doc in Project Files' views folder doesn't count toward
the length, since it was checked when it was written (my words 2026-11-10). Source tags that the unit check asks
for don't count either.
"""
import glob
import json
import os
import re
import sys

from nwani import queued_message
from shown_text import shown

SHORT = 40  # words; a reply this long or shorter is an acknowledgment and skips review
AGENT_ID = re.compile(r"agentId: (\w+)")
RUN = 6  # a run of this many words in a row, in the same order as a doc, counts as copied from it
TOKEN = re.compile(r"[\w½⅓⅔¼¾]+")
SOURCE_TAG = re.compile(r"\(?\bsource:[^)\n]*\)?", re.I)


def result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content or ""


def reviewed_this_turn(transcript_path):
    """True once a reviewer's report exists since Nwani's last message. A reviewer that runs in the
    background returns right away, so it only counts once its report comes back."""
    asked, waiting, done = set(), set(), False
    with open(transcript_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "user" and entry.get("isMeta"):
                # Harness notes, like a helper's report coming back, aren't Nwani's messages.
                origin = entry.get("origin") or {}
                if origin.get("handback") and (origin.get("senderTaskId") or origin.get("from")) in waiting:
                    done = True
            elif (entry.get("type") == "user" and isinstance(content, str)) or queued_message(entry):
                asked, waiting, done = set(), set(), False
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    # The repo's own helper is "reviewer"; the plugin's copy is "kernel:reviewer".
                    kind = str((block.get("input") or {}).get("subagent_type") or "")
                    if block.get("type") == "tool_use" and block.get("name") == "Agent" \
                            and kind.split(":")[-1] == "reviewer":
                        asked.add(block.get("id"))
            elif entry.get("type") == "user" and isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_result" and block.get("tool_use_id") in asked \
                            and not block.get("is_error"):
                        text = result_text(block)
                        if text.lstrip().startswith("Async agent launched"):
                            waiting.update(AGENT_ID.findall(text))
                        else:
                            done = True
    return done


def words(text):
    """The words Nwani reads: a table's | and --- marks only draw the grid, so they don't count (my words 2026-10-27)."""
    return [w for w in text.split() if not re.fullmatch(r"[|:\-]+", w)]


def tokens(text):
    """Words without their punctuation or case, so a copy whose semicolons became periods still matches."""
    return TOKEN.findall(text.lower())


def doc_runs():
    """Every run of RUN words in a row from the docs in Project Files' views folder."""
    root = os.environ.get("PROJECT_FILES", "/mnt/project-files")
    runs = set()
    for path in glob.glob(os.path.join(root, "views", "**", "*.md"), recursive=True):
        try:
            words_ = tokens(open(path, encoding="utf-8").read())
        except OSError:
            continue
        runs.update(tuple(words_[i:i + RUN]) for i in range(len(words_) - RUN + 1))
    return runs


def new_words(text):
    """The number of words Claude wrote itself: not inside a run copied from a doc, and not a source tag."""
    words_ = tokens(SOURCE_TAG.sub(" ", text))
    runs = doc_runs() if len(words_) > SHORT else set()
    copied = [False] * len(words_)
    for i in range(len(words_) - RUN + 1):
        if tuple(words_[i:i + RUN]) in runs:
            copied[i:i + RUN] = [True] * RUN
    return copied.count(False)


def main():
    hook = json.load(sys.stdin)
    text = "\n".join(part for part, _ in shown(hook)[0])
    if len(words(text)) <= SHORT or new_words(text) <= SHORT or not hook.get("transcript_path"):
        return
    if not reviewed_this_turn(hook["transcript_path"]):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "This reply needs review first (CLAUDE.md, Review before answering). Run the reviewer "
                "helper (subagent_type \"kernel:reviewer\", or \"reviewer\" where the repo's own "
                "helper loads) with Nwani's message, the "
                "conversation around it and this draft, and wait for its report. Fix what it finds, or say it in "
                "the reply."),
        }}))


if __name__ == "__main__":
    main()
