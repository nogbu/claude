#!/usr/bin/env python3
"""Look up and increment plants in collection.md (plantagram, 2026-10-14; collection.md since 2026-10-25).

  python3 projects/plantagram/scripts/plant.py show NAME        print that plant's row
  python3 projects/plantagram/scripts/plant.py increment NAME   add 1 to its Inflos, set As Of to today (US Eastern),
                                                                 print the new row as show does; collection.md is in Project Files, so nothing to commit
  python3 projects/plantagram/scripts/plant.py confirm NAME...  set each unconfirmed one's Confirmed to today (US Eastern), one quoted NAME per plant
  python3 projects/plantagram/scripts/plant.py hook            UserPromptSubmit hook (prompt-submit.sh), hook JSON on stdin

NAME matches a row's Name ignoring case and trailing punctuation. The hook acts only in plantagram threads
(the file PLANT_PROJECT_FILE names, default /mnt/project-files/.project, reads plantagram), on my message (2026-10-14):
  headcount, /headcount prints the number of rows for the thread to reply with, in any thread (2026-10-17)
  /increment [plant]   tells the thread to run increment and reply with the new row
  /increment           the same for the plant named in the newest message of this thread (mine or a reply) that
                       names one; if that message names several, or none does, it tells the thread to ask which
  /[plant]             prints that row for the thread to reply with; text that isn't a command or skill name
                       (/rules-check) and matches no row prints the no-match note instead
  /confirm [plants]    (one, or several split by commas, "and" or lines) tells the thread to run confirm (Confirmed = today unless already set) and reply only "[names] confirmed" plus any already confirmed
                       (2026-10-14)
  /print [plant]       writes a one-plant list and tells the thread to run plantTags' tags.py on it
  /print list          my next message is a list of plants, one per line (or the lines after /print list in the
                       same message): the same, for the whole list
In a /print, each line that is a Name or alias becomes that Name; anything else ("name / species", a plant not in
collection.md) goes to tags.py as I typed it, and a bare name that matches no row also gets the no-match note. The 3mf is plantTags_[name in camelCase], or plantTags_batch[YYYY-MM-DD]
for a list.
"""
import html, json, os, re, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
PLANTS = os.environ.get("COLLECTION_FILE", "/mnt/project-files/views/collection.md")
LIST = os.path.join(HERE, "list.py")
TAGS = os.path.join(HERE, "../tags/tags.py")
NOMENCLATURE = os.path.join(HERE, "../nomenclature.md")
SKILLS = os.path.join(HERE, "../../../.claude/skills")
PROJECT = os.environ.get("PLANT_PROJECT_FILE", "/mnt/project-files/.project")
MISS = ("Match it yourself with projects/plantagram/nomenclature.md (common short names, typos; abbreviations and dropped prefixes were tried): when only one row "
        "can be meant, act on that row and name it in the reply; ask only when two or more rows fit, or none does "
        "(CLAUDE.md, Questions; 2026-10-14).")
ALIASES = {  # my short names for a plant (lowercase): its Name
    "rlfs": "Fort Sherman x Ralph Lynam",  # Ralph Lynam x Fort Sherman's usual abbreviation (2026-10-14)
}


def table():
    lines = open(PLANTS, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("| Name"))
    cols = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    rows = []
    for l in lines[start + 2:]:
        if not l.startswith("|"):
            break
        rows.append([c.strip() for c in l.strip().strip("|").split("|")])
    return cols, rows


def key(name):
    """Lowercase, trailing punctuation dropped, hyphens and runs of spaces read as one space ("krs one" is KRS-One)."""
    return re.sub(r"[\s-]+", " ", re.sub(r"[\s.!,;:]+$", "", name.strip())).lower()


def abbreviations():
    """{short (lowercase): what it means} from the Abbreviations table in learnings/nomenclature.md, one-word shorts only;
    a meaning stops at its first "(" or ","."""
    out, on = {}, False
    for l in open(NOMENCLATURE, encoding="utf-8"):
        on = l.startswith("## Abbreviations") or (on and not l.startswith("## "))
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if on and l.startswith("|") and len(c) >= 2 and c[0] not in ("Short", "—") and not c[0].startswith(":"):
            means = re.split(r"[(,]", c[1])[0].strip()
            for s in re.split(r"[/,()]", c[0]):
                if re.fullmatch(r"[A-Za-z]+", s.strip()):
                    out[s.strip().lower()] = means
    return out


def prefixes():
    """The breeder and clone prefixes (lowercase) bolded in learnings/nomenclature.md's "Clone codes and breeder
    prefixes" section, numbered codes (RA1, Wu1–Wu9) left out: "doc block", "nse", "skg"..."""
    out, on = set(), False
    for l in open(NOMENCLATURE, encoding="utf-8"):
        on = l.startswith("## Clone codes") or (on and not l.startswith("## "))
        if on:
            out |= {b.strip().lower() for b in re.findall(r"\*\*([^*]+?)\*\*", l) if not re.search(r"[\d…–]", b)}
    return out


def find(name):
    """The row whose Name is name (or its alias); else the one row whose whole Name or Species matches name with
    its abbreviations and the table's expanded alike ("dp x mag" is Tomax: Dark Phoenix x Magnificum); else the one
    row that matches once a breeder or clone prefix (prefixes()) is dropped from the start of each of its cross's
    parts ("kos x michelle" is Invader Zim: King of Spades x Doc Block Michelle; my words 2026-10-14), or None. Parts
    are never reordered, so a reversed cross matches nothing."""
    cols, rows = table()
    name = ALIASES.get(key(name), name)
    hits = [r for r in rows if key(r[0]) == key(name)]
    if not hits:
        ab = abbreviations()
        full = lambda t: key(re.sub(r"[A-Za-z]+", lambda m: ab.get(m.group(0).lower(), m.group(0)), t))
        hits = [r for r in rows if full(name) in (full(r[0]), full(r[2]))]  # the table's own shorthand expands too
        hits = hits if len(hits) == 1 else []
        if not hits:
            pre = sorted(prefixes(), key=len, reverse=True)
            bare = lambda t: " x ".join(next((p[len(q) + 1:] for q in pre if p.startswith(q + " ")), p)
                                        for p in re.split(r"\s+x\s+", full(t)))
            hits = [r for r in rows if full(name) in (bare(r[0]), bare(r[2]))]  # only my words drop the prefix
            hits = hits if len(hits) == 1 else []
    return cols, (hits[0] if hits else None)


def fmt(cols, row):
    return "| " + " | ".join(cols) + " |\n|" + " --- |" * len(cols) + "\n| " + " | ".join(row) + " |"


def increment(name):
    cols, row = find(name)
    if not row:
        sys.exit(f"plant.py: no plant named '{name}' in collection.md")
    n = int(row[cols.index("Inflos")] or 0) + 1
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    subprocess.run([sys.executable, LIST, "set", PLANTS, row[0], f"Inflos={n}", f"As Of={today}"], check=True)
    print(fmt(*find(row[0])))  # with its column names, so the reply needs no read of the table


def confirm(name):
    cols, row = find(name)
    if not row:
        sys.exit(f"plant.py: no plant named '{name}' in collection.md")
    done = row[cols.index("Confirmed")]
    if done:  # a plant is confirmed once (my words 2026-10-14)
        print(f"already confirmed: {row[0]} ({done})")
        return
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    subprocess.run([sys.executable, LIST, "set", PLANTS, row[0], f"Confirmed={today}"], check=True)


def message(prompt):
    """The text of my message: the triggering human message in a project wake, my newest message in a relay
    from the project chat, else the whole prompt."""
    m = re.search(r'<message trigger="true"[^>]*from="human"[^>]*>(.*?)</message>', prompt, re.S)
    cited = re.findall(r'<cited [^>]*author="user"[^>]*>(.*?)</cited>', prompt, re.S)
    text = m.group(1) if m else cited[-1] if cited else prompt
    return html.unescape(text).strip()


def said(transcript):
    """Each message of this thread, newest first: my messages and the thread's replies (not tool output)."""
    try:
        lines = open(transcript, encoding="utf-8").read().splitlines()
    except OSError:
        return
    for l in reversed(lines):
        try:
            d = json.loads(l)
        except ValueError:
            continue
        c = d.get("message", {}).get("content") if d.get("type") in ("user", "assistant") else None
        if isinstance(c, str):
            yield message(c)
        elif isinstance(c, list):
            for x in c:
                if x.get("type") == "text" and d["type"] == "user":
                    yield message(x["text"])
                elif x.get("type") == "tool_use" and x.get("name", "").endswith("__reply"):
                    yield x.get("input", {}).get("text", "")


def named(text, names):
    """The plant names in text, whole words, ignoring case; a name inside a longer one ("Acme" in "Acme 2") is dropped."""
    said = lambda n: re.search(r"(?<!\w)" + re.escape(n.lower()) + r"(?!\w)", text.lower())
    hits = {n for n in names if said(n)} | {n for a, n in ALIASES.items() if said(a)}
    return {n for n in hits if not any(n != h and n.lower() in h.lower() for h in hits)}


def skills(transcript):
    """The skill names this thread can run, as key() reads them: the repo's .claude/skills folders, plus the names in
    the transcript's skill listings, which add the built-in and plugin skills ("simplify", "anthropic-skills:pdf")."""
    names = set(os.listdir(SKILLS)) if os.path.isdir(SKILLS) else set()
    try:
        for l in open(transcript, encoding="utf-8"):
            a = json.loads(l).get("attachment") if '"skill_listing"' in l else None
            if isinstance(a, dict) and a.get("type") == "skill_listing":
                names.update(a.get("names", []))
    except (OSError, ValueError):
        pass
    return {key(n) for n in names}


def pending():
    """The file marking that my next message is a /print list, per thread."""
    sid = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID") or "local"
    return f"/tmp/print-list-{sid}"


def print_run(lines, label):
    """Write the tags.py list for these lines and say how to run it. A line tags.py would look up by name (no tab,
    " / " or ":", not "blank"; its to_tags) that matches no row gets the no-match note first, as /confirm's does, and
    still goes to tags.py as typed, so a new plant reaches its species question (nomenclature.md: when it finds no
    single row, the hook's note says what to do)."""
    out, miss = [], []
    for ln in (l.strip() for l in lines):
        if ln:
            cols, row = find(ln)
            out.append(row[0] if row else ln)
            if not row and not re.search(r"\t| / |:", ln) and ln.lower() != "blank":
                miss.append(ln)
    if not out:
        print("Hook (collection.md rules): /print with no plants; ask which plants.")
        return
    if miss:
        print(f"Hook (collection.md rules): {', '.join(repr(m) for m in miss)} matched no row exactly. {MISS}")
    path = f"/tmp/print-{label}.txt"
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"Hook (collection.md rules): /print. Follow the docstring of {os.path.relpath(TAGS, os.path.join(HERE, "../../.."))} "
          f"(card, Collection thread): run python3 {os.path.relpath(TAGS, os.path.join(HERE, "../../.."))} {path} {label}, then attach the 3mfs. "
          "Plants: " + "; ".join(out))


HEADCOUNT = "Hook (collection.md rules): headcount. "
ROUTE = ("Hook (collection.md rules): if this thread isn't the collection thread the project instructions link, "
         "skip the step below: send my message word for word to that thread's session (list_threads) "
         "with message_thread, and reply only 'Sent to [collection](#[its thread id])'.\n")


def hook():
    try:
        if open(PROJECT).read().strip() != "plantagram":
            return
        data = json.load(sys.stdin)
    except (OSError, ValueError):
        return
    text = message(data.get("prompt", ""))
    if os.path.exists(pending()) and not text.startswith("/"):
        os.remove(pending())
        print_run(text.splitlines(), "batch" + datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d"))
        return
    if re.fullmatch(r"/?headcount\W*", text, re.I):   # counted here (/headcount too, my words 2026-10-25), so the thread needn't read the table (2026-10-17)
        print(f"{HEADCOUNT}collection.md has {len(table()[1])} rows; reply with that number.")
        return
    if not text.startswith("/"):
        return
    m = re.fullmatch(r"/print\s+list\b\s*(.*)", text, re.I | re.S)
    if m:
        if m.group(1).strip():
            print_run(m.group(1).splitlines(), "batch" + datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d"))
        else:
            open(pending(), "w").write("")
            print("Hook (collection.md rules): /print list. Ask me for the list of plants, one per line; "
                  "the hook reads my next message as that list.")
        return
    m = re.fullmatch(r"/confirm\s+(.+)", text, re.I | re.S)
    if m:  # one plant, or several split by commas, "and" or lines
        cols, row = find(m.group(1))
        parts = [m.group(1)] if row else [p for p in re.split(r"\s*(?:,|\band\b|\n)\s*", m.group(1)) if p.strip()]
        rows = [find(p)[1] for p in parts]
        if all(rows):
            names = " ".join(f'"{r[0]}"' for r in rows)
            print(f"Hook (collection.md rules): run python3 projects/plantagram/scripts/plant.py confirm {names}, "
                  "and reply only '[Names] confirmed', e.g. 'Wack Magic and Madripoor confirmed', adding any it prints as already confirmed and when.")
        else:
            bad = [p.strip() for p, r in zip(parts, rows) if not r]
            print(f"Hook (collection.md rules): {', '.join(repr(b) for b in bad)} matched no row exactly. {MISS}")
        return
    m = re.fullmatch(r"/print\s+(.+)", text, re.I | re.S)
    if m:
        cols, row = find(m.group(1))
        name = row[0] if row else m.group(1).strip()
        words = re.findall(r"[a-z0-9]+", name.lower())
        print_run([name], words[0] + "".join(w.capitalize() for w in words[1:]) if words else "tag")
        return
    m = re.fullmatch(r"/increment(?:\s+(.+))?", text, re.I | re.S)
    if m:
        name = m.group(1)
        if not name:
            names, hits = [r[0] for r in table()[1]], set()
            for t in said(data.get("transcript_path", "")):
                hits = named(t, names) if t.strip() != text else set()
                if hits:
                    break
            if len(hits) != 1:
                print("Hook (collection.md rules): /increment with no name, and the newest message naming a plant names "
                      + (", ".join(sorted(hits)) if hits else "none") + "; ask which plant.")
                return
            name = hits.pop()
        cols, row = find(name)
        if row:
            print(f'Hook (collection.md rules): run python3 projects/plantagram/scripts/plant.py increment "{row[0]}", '
                  "and reply with the new row as the table it prints.")
        else:
            print(f"Hook (collection.md rules): '{name.strip()}' matched no row exactly. {MISS}")
        return
    cols, row = find(text[1:])
    words = key(text[1:]) + " "  # a skill name can be followed by its arguments ("/code-review high")
    if row:
        print("Hook (collection.md rules): my message is a plant name; reply with its collection.md row as this table:\n"
              + fmt(cols, row))
    elif words.strip() and words.split()[0] not in ("increment", "confirm", "print", "headcount") \
            and not any(words.startswith(s + " ") for s in skills(data.get("transcript_path", ""))):
        print(f"Hook (collection.md rules): '{text[1:].strip()}' matched no row exactly. {MISS}")


if __name__ == "__main__":
    cmd, args = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
    if cmd == "hook":
        import contextlib, io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            hook()
        if out.getvalue():  # every plants command belongs to the collection thread; a headcount is answered where asked
            print(("" if out.getvalue().startswith(HEADCOUNT) else ROUTE) + out.getvalue(), end="")
    elif cmd == "show" and args:
        cols, row = find(" ".join(args))
        print(fmt(cols, row) if row else f"no plant named '{' '.join(args)}'")
    elif cmd == "increment" and args:
        increment(" ".join(args))
    elif cmd == "confirm" and args:
        for a in args:  # each argument is one plant (quote multi-word names)
            confirm(a)
    else:
        sys.exit(__doc__)
