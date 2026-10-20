#!/usr/bin/env python3
"""Reports how long a thread took and how much it used, from the thread's own record.

Run: python3 scripts/usage.py [record.jsonl]
With no file, it reads the record of the thread it runs in.
Every speed or usage recommendation cites these numbers (CLAUDE.md, Optimize).
"""
import glob
import json
import os
import re
import sys
from datetime import datetime


def when(entry):
    return datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))


def this_thread():
    paths = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % os.environ.get("CLAUDE_CODE_SESSION_ID", "")))
    return paths[0] if paths else None


def minutes(seconds):
    return "%d min %02d s" % divmod(round(seconds), 60) if seconds >= 60 else "%.1f s" % seconds


def label(block):
    args = block.get("input") or {}
    name = block.get("name", "").replace("mcp__hearthbot__", "").replace("mcp__", "")
    detail = args.get("description") or args.get("question") or args.get("file_path") or args.get("text") or ""
    return "%s: %s" % (name, " ".join(str(detail).split())[:60])


def read(path):
    entries = []
    with open(path) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except ValueError:
                pass
    calls, turns, starts, results, cost = {}, [], {}, [], None
    stamps = [when(e) for e in entries if "timestamp" in e and e.get("type") in ("user", "assistant")]
    last_time = None
    for e in entries:
        content = (e.get("message") or {}).get("content")
        if "timestamp" in e:
            last_time = when(e)
        if e.get("type") == "cost-state":
            cost = dict(e, recorded=last_time)
        elif e.get("type") == "user" and isinstance(content, str) and "timestamp" in e:
            m = re.search(r'<wake reason="([^"]+)"', content)
            turns.append({"start": when(e), "end": when(e), "reason": m.group(1) if m else "message",
                          "calls": set(), "read": 0})
        elif e.get("type") == "assistant" and "timestamp" in e:
            msg = e["message"]
            usage = msg.get("usage") or {}
            if msg.get("id") not in calls:
                calls[msg.get("id")] = {"usage": usage, "tools": 0}
                if turns:
                    turns[-1]["read"] += sum(usage.get(k, 0) for k in
                                             ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            for block in content or []:
                if block.get("type") == "tool_use":
                    calls[msg.get("id")]["tools"] += 1
                    starts[block["id"]] = (when(e), block)
            if turns:
                turns[-1]["calls"].add(msg.get("id"))
                turns[-1]["end"] = when(e)
        elif e.get("type") == "user" and isinstance(content, list) and "timestamp" in e:
            for block in content:
                if block.get("type") == "tool_result" and block.get("tool_use_id") in starts:
                    began, tool = starts[block["tool_use_id"]]
                    results.append(((when(e) - began).total_seconds(), tool))
            if turns:
                turns[-1]["end"] = when(e)
    span = (stamps[-1] - stamps[0]).total_seconds() if stamps else 0
    return calls, turns, results, cost, span


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else this_thread()
    if not path:
        sys.exit("No thread record found. Pass the path to a .jsonl record.")
    calls, turns, results, cost, span = read(path)
    usage = [c["usage"] for c in calls.values()]
    total = lambda key: sum(u.get(key, 0) for u in usage)
    fresh = total("input_tokens") + total("cache_creation_input_tokens")
    cached = total("cache_read_input_tokens")
    sizes = [u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
             for u in usage]
    one_tool = sum(1 for c in calls.values() if c["tools"] == 1)
    several = sum(1 for c in calls.values() if c["tools"] > 1)

    print("WHOLE THREAD")
    print("  Time from start to now: %s" % minutes(span))
    print("  Model calls: %d" % len(calls))
    print("  Tokens read: %s (%s new, %s from cache, %d%% cached)" % (
        f"{fresh + cached:,}", f"{fresh:,}", f"{cached:,}", 100 * cached // max(fresh + cached, 1)))
    print("  Tokens written: %s" % f"{total('output_tokens'):,}")
    if sizes:
        print("  Size of each model call: %s now, %s at its largest" % (f"{sizes[-1]:,}", f"{max(sizes):,}"))
    if cost:
        print("  The app's own totals, last recorded %s (it records them only now and then):" % (
            cost["recorded"].strftime("%H:%M UTC") if cost.get("recorded") else "at an unknown time"))
        print("  Cost (the app's estimate): $%.2f" % cost.get("totalCostUSD", 0))
        print("  Time spent waiting on the model: %s" % minutes(cost.get("totalAPIDuration", 0) / 1000))
        print("  Time spent running tools: %s" % minutes(cost.get("totalToolDuration", 0) / 1000))
    print("  Model calls that ran one tool: %d. Calls that ran several at once: %d." % (one_tool, several))

    print("\nEACH TURN (time from the message to the turn's last step)")
    for t in turns:
        print("  %s  %-16s %9s  %3d calls  %s tokens read" % (
            t["start"].strftime("%H:%M UTC"), t["reason"], minutes((t["end"] - t["start"]).total_seconds()),
            len(t["calls"]), f"{t['read']:,}"))

    print("\nSLOWEST STEPS")
    for seconds, tool in sorted(results, key=lambda r: -r[0])[:5]:
        print("  %9s  %s" % (minutes(seconds), label(tool)))

    helpers = sorted(glob.glob(os.path.join(path[:-len(".jsonl")], "subagents", "*.jsonl")))
    if helpers:
        print("\nHELPERS (not counted above)")
    for helper in helpers:
        h_calls, _, _, _, h_span = read(helper)
        h_usage = [c["usage"] for c in h_calls.values()]
        h_read = sum(u.get(k, 0) for u in h_usage
                     for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        meta = helper[:-len(".jsonl")] + ".meta.json"
        name = json.load(open(meta)).get("description", "") if os.path.exists(meta) else ""
        print("  %-36s %9s  %3d calls  %s tokens read" % (
            (name or os.path.basename(helper))[:36], minutes(h_span), len(h_calls), f"{h_read:,}"))


if __name__ == "__main__":
    main()
