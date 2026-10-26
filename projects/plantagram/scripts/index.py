#!/usr/bin/env python3
"""Build a project's file index from each content file's header (config redesign, sections 4 to 6).

Run from anywhere in the repo:
  python3 shared/scripts/index.py [project]   one line per file; project defaults to /mnt/project-files/.project
  python3 shared/scripts/index.py --load [project...]   words every thread of each project reads at start (CLAUDE.md,
                                                     the card, this index, every skill's description), then once what
                                                     each skill adds when loaded (refactor-config step 3, Load)

Every content file starts with a header:
  ---
  about: what the file holds
  read-when: when a thread should read it
  readonly: no
  ---
List files add sort, statuses and default (list.py); a file whose short name
isn't its file name adds name; a list file's own rules go in rules (CLAUDE.md,
How the rules load); the index says only that it has them, and a thread reads them when the read-when sends it to the file. A product's state.md (products/[name]/state.md, short name
[name]) may leave out read-when: it's read on "resume" or before work on the
product (product skill). Product logs (products/[name]/log.md) print as one
line, and so do retired product docs.
check.py blocks a commit whose content file has no valid header (no word cap since
2026-10-11); check.py and list.py import from here.
"""
import glob, os, subprocess, sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
CONTENT_GLOBS = ["projects/*/content/*.md", "projects/*/learnings/*.md", "projects/*/products/*/*.md",
                 "projects/*/products/retired/*.md", "projects/*/products/retired/*/*.md", "shared/*.md"]
REQUIRED = ("about", "read-when", "readonly")
LIST_KEYS = ("sort", "statuses", "default")
OPTIONAL = ("name", "rules")  # the short name, only where it isn't the file name; a list file's own rules


def content_files(project=None):
    files = set()
    for g in CONTENT_GLOBS:
        if project and g.startswith("projects/*"):
            g = g.replace("projects/*", f"projects/{project}", 1)
        files.update(glob.glob(g, root_dir=ROOT, recursive=True))
    return sorted(files)


def header(path, text=None):
    """Return (fields, errors) for a file's header."""
    if text is None:
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, ["no header (the first line must be ---)"]
    fields, errors = {}, []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not sep or not key:
            errors.append(f"header line isn't 'key: value': {line!r}")
        elif key not in REQUIRED + LIST_KEYS + OPTIONAL:
            errors.append(f"unknown header field '{key}'")
        elif key in fields:
            errors.append(f"header field '{key}' appears twice")
        else:
            fields[key] = value
    else:
        return fields, errors + ["header never closes with ---"]
    for key in REQUIRED:
        if key == "read-when" and is_product(path):
            continue
        if not fields.get(key):
            errors.append(f"header is missing '{key}'")
    if fields.get("readonly") not in (None, "", "yes", "no"):
        errors.append("readonly must be yes or no")
    present = [k for k in LIST_KEYS if k in fields]
    if present and len(present) < len(LIST_KEYS):
        errors.append("a list header needs all of sort, statuses and default")
    elif present:
        statuses = [s.strip() for s in fields["statuses"].split(",")]
        if fields["default"] not in statuses:
            errors.append(f"default '{fields['default']}' isn't one of the statuses")
    return fields, errors


def is_product(path):
    return "/products/" in path and "/retired/" not in path


def short_name(path, fields=None):
    """Short name (repo-edit skill, Files): the header's name if it has one, else
    products/x/state.md -> x, products/x/log.md -> x.log, retired product.x -> x, else the file name."""
    if fields and fields.get("name"):
        return fields["name"]
    name = os.path.basename(path)[:-3]
    if "/products/" in path and name in ("state", "log"):
        folder = os.path.basename(os.path.dirname(path))
        return folder if name == "state" else folder + ".log"
    if name.startswith("product."):
        return name[len("product."):]
    return name


def line(path):
    fields, errors = header(path)
    if errors:
        return f"- {short_name(path, fields)}: NO VALID HEADER ({errors[0]}). {path}"
    tags = []
    if "/retired/" in path:
        tags.append("retired")
    if fields["readonly"] == "yes":
        tags.append("read-only")
    tag = f" ({', '.join(tags)})" if tags else ""
    about = fields["about"].rstrip(".")
    when = fields.get("read-when", "").rstrip(".")
    text = f"- {short_name(path, fields)}{tag}: {about}."
    if when:
        text += f" Read {when}."
    if fields.get("rules"):
        text += " Rules in its header."
    return f"{text} {path}"


def lines(project):
    """The index lines for a project, in print order."""
    out, logs, retired = [], [], []
    for f in content_files(project):
        if "/retired/" in f:
            if not f.endswith("/log.md"):
                retired.append(short_name(f, header(f)[0]))
        elif f.endswith("/log.md"):
            logs.append(short_name(f)[:-len(".log")])
        else:
            out.append(line(f))
    if logs:
        out.append(f"- logs (product skill): {', '.join(logs)}. projects/{project}/products/[name]/log.md")
    if retired:
        out.append(f"- retired (read-only): {', '.join(retired)}. Read only for a value the current doc lacks. "
                   f"projects/{project}/products/retired/ (product.[name].md or [name]/state.md)")
    return out


def words(path):
    return len(open(os.path.join(ROOT, path), encoding="utf-8").read().split())


def load(projects):
    """Print the words every thread of each project reads at start, then once what each skill adds when loaded."""
    skills = sorted(glob.glob(".claude/skills/*/SKILL.md", root_dir=ROOT))
    desc = {}
    for s in skills:
        for l in open(os.path.join(ROOT, s), encoding="utf-8"):
            if l.startswith("description:"):
                desc[s] = len(l.split()) - 1
                break
    core = words("CLAUDE.md")
    for project in projects:
        card, idx = words(f"projects/{project}/config.{project}.md"), len(" ".join(lines(project)).split())
        print(f"every {project} thread at start: CLAUDE.md {core}, card {card}, index {idx}, "
              f"skill descriptions {sum(desc.values())} ({len(desc)} skills): {core + card + idx + sum(desc.values())} words")
    print("when loaded (description, SKILL.md, other files in its folder):")
    for s in sorted(skills, key=lambda s: -words(s)):
        folder = os.path.dirname(s)
        others = [f for f in glob.glob(f"{folder}/*", root_dir=ROOT) if f != s and os.path.isfile(os.path.join(ROOT, f))]
        extra = ", ".join(f"{os.path.basename(f)} {words(f)}" for f in others)
        print(f"  {os.path.basename(folder)}: {desc.get(s, 0)}, {words(s)}" + (f", {extra}" if extra else ""))


def main(argv):
    show_load = "--load" in argv
    argv = [a for a in argv if a != "--load"]
    project = argv[0] if argv else None
    if show_load and len(argv) > 1:
        for p in argv:
            if not os.path.isdir(os.path.join(ROOT, "projects", p)):
                sys.exit(f"index.py: no folder projects/{p}")
        return load(argv)
    if not project:
        try:
            project = open("/mnt/project-files/.project").read().strip()
        except OSError:
            sys.exit("index.py: name a project, or add /mnt/project-files/.project")
    if not os.path.isdir(os.path.join(ROOT, "projects", project)):
        sys.exit(f"index.py: no folder projects/{project}")
    if show_load:
        return load([project])
    for l in lines(project):
        print(l)


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet when piped to head
    main(sys.argv[1:])
