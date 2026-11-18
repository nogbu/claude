#!/usr/bin/env python3
"""Has a small model judge each sentence of Nwani's message, reading the whole message (Nwani's
pick on the card, 2026-11-18). lookup.py calls it once per message and answer-only.py reads the
saved verdict, so the model runs once per message, not once per step.

Each sentence is a question, a request or other, read in the light of the rest of the message
and the reply it answers, so "wtf? why is x happening" makes "wtf?" other. A sentence that could
be either a question or a request counts as a question (Nwani, 2026-11-17).

The model learns from examples taken from Nwani's own threads (judge-examples.txt) and from
Nwani's corrections (sentence-examples.txt), read fresh from the repo on each message. If the
model can't be reached, it falls back to Nwani's rule alone: a sentence ending in "?" is a question,
and every other sentence counts as other. A message with no request lets edits through only when it
has no question either, so a message of only reactions or statements doesn't block edits.

Run: python3 judge.py "message"   (prints the verdict, for testing)
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
CACHE = pathlib.Path(os.environ.get("CLAUDE_JUDGE_CACHE") or pathlib.Path.home() / ".claude" / "judge")
SENTENCE_END = re.compile(r"(?<=[.!])\s+|(?<=[^\s?]\?)\s+|\n+")
SCHEMA = json.dumps({
    "type": "object",
    "properties": {"sentences": {"type": "array", "items": {
        "type": "object",
        "properties": {"sentence": {"type": "string"},
                       "kind": {"type": "string", "enum": ["question", "request", "other"]}},
        "required": ["sentence", "kind"]}}},
    "required": ["sentences"]})
INSTRUCTIONS = """You sort the sentences of one message Nwani sent to an assistant. Read the whole message, and the assistant reply it answers, before judging any sentence, because each sentence gives context for the others.

For each sentence, say which kind it is:
- question: asks for information, an explanation or an answer, in any wording, with or without a "?". "explain why you did X" and "quote where I said that" are questions, since they ask only for an answer.
- request: asks the assistant to do, make, change, save or start something.
- other: a reaction, statement, complaint or context that asks for nothing by itself, like "wtf?" right before the real question.

A sentence that ends in "?" is a question unless the rest of the message shows it's only a reaction. A sentence that could be either a question or a request counts as a question.

Learn how Nwani phrases things from these examples, taken from Nwani's own messages. Corrections Nwani made come last and win over everything else.
"""


def examples():
    lines = []
    for name in ("judge-examples.txt", "sentence-examples.txt"):
        for place in places(name):
            try:
                text = place.read_text()
            except OSError:
                continue
            for line in text.splitlines():
                kind, _, said = line.partition("|")
                kind = {"Q": "question", "R": "request", "O": "other"}.get(kind.strip())
                if kind and said.strip():
                    lines.append("%s -> %s" % (said.strip(), kind))
            break
    return "\n".join(lines)


def places(name):
    """The repo's copy first, so a correction works without a new plugin upload, then this folder's."""
    start = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    found = []
    for root in [start] + sorted(p for p in start.iterdir() if p.is_dir()) if start.is_dir() else []:
        if (root / "CLAUDE.md").is_file():
            found.append(root / ".claude" / "hooks" / name)
    return found + [HERE / name]


def split(message):
    """The sentences, split in code so the model labels each one and can't merge them."""
    return [s.strip() for s in SENTENCE_END.split(message) if s and s.strip()]


def fallback(message):
    """Without the model, only Nwani's rule: a sentence ending in "?" is a question. Everything else
    counts as other, so a message with a "?" still gets only an answer."""
    return [{"sentence": s, "kind": "question" if s.endswith("?") else "other"} for s in split(message)]


def key(message, before=""):
    """The message, the reply it answers and the examples, so a new correction changes the verdict."""
    text = "\0".join((message.strip(), (before or "")[-1500:], examples()))
    return hashlib.sha256(text.encode()).hexdigest()[:24]


def saved(message, before=None):
    """The verdict lookup.py saved for this message. Without the reply it answered, the newest one."""
    try:
        if before is not None:
            return json.loads((CACHE / (key(message, before) + ".json")).read_text())
        latest = CACHE / ("latest-" + hashlib.sha256(message.strip().encode()).hexdigest()[:24] + ".json")
        return json.loads(latest.read_text())
    except (OSError, ValueError):
        return None


def last_reply(path):
    """The text of Claude's last reply in the thread, so the model knows what the message answers."""
    last = ""
    try:
        with open(path) as f:
            for line in f:
                if "post_message" not in line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                for block in (entry.get("message") or {}).get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and \
                            block.get("name", "").endswith("post_message"):
                        last = (block.get("input") or {}).get("text") or last
    except OSError:
        pass
    return last


def judge(message, before=""):
    """The verdict for each sentence, saved so answer-only.py can read it."""
    if not message.strip() or message.startswith("Chose "):
        return {"sentences": [{"sentence": message, "kind": "request"}], "model": False}
    found = saved(message, before)
    if found:
        return found
    parts = split(message)
    prompt = ("%s\nExamples:\n%s\n\nThe assistant reply this answers:\n%s\n\nNwani's whole message:\n%s\n\n"
              "Label each of these sentences of it, in order, keeping each sentence exactly as given:\n%s") % (
        INSTRUCTIONS, examples(), (before or "(none)")[-1500:], message,
        "\n".join("%d. %s" % (n + 1, p) for n, p in enumerate(parts)))
    verdict = {"sentences": fallback(message), "model": False}
    try:
        if os.environ.get("CLAUDE_JUDGE_CHILD") or os.environ.get("CLAUDE_JUDGE_OFFLINE"):
            raise OSError("no model in tests or inside the judge itself")
        with tempfile.TemporaryDirectory() as folder:
            out = subprocess.run(
                ["claude", "-p", "--model", "haiku", "--output-format", "json", "--json-schema", SCHEMA,
                 "--setting-sources", "", "--tools", "", "--no-session-persistence"],
                input=prompt, capture_output=True, text=True, timeout=40, cwd=folder,
                env=dict(os.environ, CLAUDE_JUDGE_CHILD="1"))
        result = json.loads(out.stdout)
        answer = result.get("structured_output") or json.loads(result.get("result") or "{}")
        labels = answer.get("sentences") or []
        if len(labels) == len(parts):
            sentences = []
            for part, label in zip(parts, labels):
                kind = label.get("kind")
                # Nwani's rule: a "?" sentence is never a request, only a question or a reaction.
                if part.endswith("?") and kind == "request":
                    kind = "question"
                sentences.append({"sentence": part, "kind": kind})
            verdict = {"sentences": sentences, "model": True,
                       "cost_usd": result.get("total_cost_usd"), "ms": result.get("duration_ms")}
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / (key(message, before) + ".json")).write_text(json.dumps(verdict))
        latest = "latest-" + hashlib.sha256(message.strip().encode()).hexdigest()[:24] + ".json"
        (CACHE / latest).write_text(json.dumps(verdict))
    except OSError:
        pass
    return verdict


def asks_only(verdict):
    """True when nothing in the message asks for a step, so it gets only an answer."""
    kinds = [s.get("kind") for s in verdict.get("sentences", [])]
    return "question" in kinds and "request" not in kinds


if __name__ == "__main__":
    print(json.dumps(judge(" ".join(sys.argv[1:])), indent=1))
