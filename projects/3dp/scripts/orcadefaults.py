#!/usr/bin/env python3
"""orcadefaults: my default settings, pulled from OrcaSlicer itself (3dp project, 2026-10-10).

Default settings are Orca's stock presets "Bambu Lab P1S 0.6 nozzle" (printer) and "0.30mm Standard @BBL X1C 0.6
nozzle" (process) in the Orca that orca-setup.sh installs (/opt/orca). The script resolves each preset's inherits
chain from Orca's BBL profiles, has Orca's command-line slicer fill in its built-in values (--export-settings), and
sorts each setting into printer or process with the lists in Orca's own source (Preset.cpp, PrintConfig.cpp, fetched
once per container for the installed version). Checked 2026-10-10 against a stock 3mf saved by Orca 2.4.2: all 494
shared printer and process settings matched; the export lacks 10 (printer connection, thumbnail format, ironing
expansion), which take Orca's built-in values from PrintConfig.cpp.
rows() also gives each setting's place on Orca's settings tabs (tab, section, label, from Tab.cpp, in Orca's English
wording from its i18n/en file) and its value as the tab shows it; shared/scripts/lookup.py shows my settings beside
these (it replaced the screenshot copies p1s-default-settings.json and p1s-default-process-settings.json, 2026-10-10).

  python3 orcadefaults.py [printer|process] TEXT...   every default setting whose name contains TEXT (_ or space)
  python3 orcadefaults.py --diff FILE.3mf             printer and process settings in a 3mf's project settings that
                                                      differ from the defaults (object settings: settingsdiff.py)
Values that repeat once per extruder variant (["30", "30"]) print once.
"""
import gettext, json, os, re, subprocess, sys, urllib.request, zipfile

ORCA = "/opt/orca"
PROFILES = f"{ORCA}/squashfs-root/resources/profiles/BBL"
CACHE = f"{ORCA}/dd/orcadefaults"
EN = f"{ORCA}/squashfs-root/resources/i18n/en/OrcaSlicer.mo"    # Orca's English wording on screen
PRESETS = {"printer": ("machine", "Bambu Lab P1S 0.6 nozzle"),
           "process": ("process", "0.30mm Standard @BBL X1C 0.6 nozzle")}
SKIP = {"name", "inherits", "from", "type", "instantiation", "setting_id", "version", "printer_settings_id",
        "print_settings_id", "different_settings_to_system", "inherits_group", "print_compatible_printers"}


def version():
    setup = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orca-setup.sh")
    return re.search(r"V=([\d.]+)", open(setup).read()).group(1)


def resolve(kind, name):
    d = json.load(open(f"{PROFILES}/{kind}/{name}.json", encoding="utf-8"))
    if d.get("inherits"):
        base = resolve(kind, d["inherits"])
        base.update(d)
        d = base
    d.pop("inherits", None)
    return d


def quoted(text, start):
    """Quoted names in the brace block that opens after text[start:], comments removed."""
    j = text.index("{", start)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            break
    return re.findall(r'"([^"]+)"', re.sub(r"//[^\n]*|/\*.*?\*/", "", text[j:k], flags=re.S))


def source(v, name):
    """One of Orca's source files at tag v{v} (cached): Preset.cpp, PrintConfig.cpp or Tab.cpp."""
    path = f"{CACHE}/{v}-{name}"
    if not os.path.exists(path):
        sub = "slic3r/GUI" if name == "Tab.cpp" else "libslic3r"
        url = f"https://raw.githubusercontent.com/SoftFever/OrcaSlicer/v{v}/src/{sub}/{name}"
        os.makedirs(CACHE, exist_ok=True)
        open(path, "w").write(urllib.request.urlopen(url, timeout=60).read().decode())
    return open(path).read()


def key_lists(v):
    """{"printer": set, "process": set} from Orca's source at tag v{v}."""
    p, c = source(v, "Preset.cpp"), source(v, "PrintConfig.cpp")
    printer = (quoted(p, p.index("s_Preset_printer_options")) + quoted(p, p.index("s_Preset_machine_limits_options"))
               + quoted(c, c.index("m_extruder_option_keys =")))
    return {"printer": set(printer), "process": set(quoted(p, p.index("s_Preset_print_options")))}


def tr(text):
    """Text as Orca's English screens show it (e.g. "Bed exclude area" shows as "Excluded bed area")."""
    if not hasattr(tr, "cat"):
        tr.cat = gettext.GNUTranslations(open(EN, "rb")) if os.path.exists(EN) else gettext.NullTranslations()
    return tr.cat.gettext(text) if text else text


def literal(s):
    """The text of a C++ string expression: L("a" "b"), u8"x" or "x"."""
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', s)) if s else ""


def defs(v):
    """{key: {type, label, full_label, sidetext, enum_values, enum_labels}} from PrintConfig.cpp."""
    text = source(v, "PrintConfig.cpp")
    out = {}
    starts = list(re.finditer(r'def\s*=\s*this->add(?:_nullable)?\("(\w+)"(?:\s*\+\s*axis\.name)?,\s*(co\w+)\)', text))
    for i, m in enumerate(starts):
        body = text[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        field = lambda f: literal((re.search(rf'def->{f}\s*=\s*(.*?);\s*(?://.*)?$', body, re.M) or [None, ""])[1])
        d = {"type": m.group(2), "label": field("label"), "full_label": field("full_label"), "sidetext": field("sidetext"),
             "enum_values": re.findall(r'enum_values\.(?:push|emplace)_back\(\s*"([^"]*)"', body),
             "enum_labels": [literal(x) for x in re.findall(r'enum_labels\.(?:push|emplace)_back\((.*?)\);', body)]}
        m2 = re.search(r'set_default_value\(new ConfigOption(Bool|Int|Float|String|Percent)s?(?:Nullable)?\s*\(\s*\{?\s*'
                       r'([^)}]*?)\s*\}?\s*\)\s*\)', body)
        if m2:    # Orca's built-in value, for the few settings its export leaves out
            x = m2.group(2).strip().strip('"').rstrip(".")
            d["builtin"] = {"true": "1", "false": "0"}.get(x, x if m2.group(1) != "Float" or x else "0")
        if m.group(1).endswith("_") and "axis.name" in m.group(0):    # machine limits, one per axis
            for axis in "xyze":
                out[m.group(1) + axis] = dict(d, full_label=re.sub(r"%1%", axis.upper(), re.search(
                    r'boost::format\("([^"]+)"\)', body).group(1)))
        else:
            out[m.group(1)] = d
    out["infill_anchor_max"]["sidetext"] = out["infill_anchor"]["sidetext"]    # copied from infill_anchor in the source
    for k in ("support_filament", "support_interface_filament", "wipe_tower_filament", "wall_filament", "solid_infill_filament",
              "sparse_infill_filament"):
        out.get(k, {})["filament"] = True
    for k, d in out.items():
        if k.endswith("_filament_id"):
            d["filament"] = True
    return out


def layout(v):
    """Orca's settings tabs as [(tab, section, label, [keys])], read from Tab.cpp: the process tab
    (TabPrint::build), then the printer tab (build_fff, the Motion ability, Multimaterial and Extruder pages).
    A row holding several keys (e.g. Overhang speed's four) is also listed once per key under its own label;
    a G-code box (an option group with no label column) is the tab's own table, labeled by the group's title."""
    text = source(v, "Tab.cpp").split("\n")
    d = defs(v)
    ranges = [("process", "void TabPrint::build()", "void TabPrint::reload_config()"),
              ("printer", "void TabPrinter::build_fff()", "void TabPrinter::build_sla()"),
              ("printer", "PageShp TabPrinter::build_kinematics_page()", "void TabPrinter::build_unregular_pages("),
              ("printer", "void TabPrinter::build_unregular_pages(", "void TabPrinter::on_preset_loaded()")]
    rows = []
    for group, start, end in ranges:
        a = next(i for i, l in enumerate(text) if l.startswith(start))
        b = next(i for i, l in enumerate(text) if i > a and l.startswith(end))
        page = section = line_label = None
        bare = skip = False
        line_keys = []
        for raw in text[a:b]:
            s = raw.split("//")[0].strip()
            if raw.startswith("#if 0"):
                skip = True
            elif raw.startswith(("#endif", "#else")):
                skip = False
            if skip or not s:
                continue
            m = re.search(r'add_options_page\((?:L\("([^"]+)"\)|page_name)', s)
            if m:
                page = m.group(1) or "Extruder"
                continue
            m = re.search(r'new_optgroup\((?:L\()?"([^"]*)"\)?(.*)', s)
            if m:
                section, bare = m.group(1), bool(re.match(r'\s*,\s*L?"[^"]*"\s*,\s*0\s*\)', m.group(2)))
                continue
            m = re.search(r'\w*[lL]ine\s*=\s*(?:Line\s*)?\{\s*L\("([^"]+)"\)', s)
            if m:
                line_label, line_keys = m.group(1), []
                continue
            keys = []
            m = re.search(r'append_single_option_line\("(\w+)"', s) or re.search(
                r'(?:Option\s+)?option\s*=\s*optgroup->get_option\("(\w+)"', s) or re.search(
                r'create_line_with_widget\(optgroup\.get\(\),\s*"(\w+)"', s)
            if m:
                keys = [(m.group(1), "label")]
            if 'Option option(def, "extruders_count")' in s:
                rows.append((group, page, section, "Extruders", ["extruders_count"]))
                continue
            m = re.search(r'append_option_line\(optgroup,\s*(?:"(\w+)"\s*(\+\s*axis)?|speed_axis)', s)
            if m:
                stem = m.group(1) or "machine_max_speed_"
                keys = [((stem + a) if (m.group(2) or not m.group(1)) else stem, "full_label")
                        for a in ("xyze" if (m.group(2) or not m.group(1)) else [""])]
            m = re.search(r'line\.append_option\(optgroup->get_option\("(\w+)"', s)
            if m and line_label:
                line_keys.append(m.group(1))
                own = d.get(m.group(1), {}).get("label") or line_label
                rows.append((group, page, section, f"{line_label} {own}" if len(own) <= 4 else own, [m.group(1)]))
                continue
            if re.search(r'append_line\(\s*\w*line\s*\)', s) and line_label:
                rows.append((group, page, section, line_label, line_keys))
                line_label = None
                continue
            for k, which in keys:
                if k not in d:
                    continue
                if bare:
                    rows.append((group, page, "", section, [k]))
                else:
                    rows.append((group, page, section, d[k][which] or d[k]["label"] or d[k]["full_label"], [k]))
    return rows


def display(dfn, value):
    """A raw Orca value as the settings tab shows it: On/Off, enum labels, units."""
    t, side = dfn.get("type", ""), dfn.get("sidetext", "")
    vals = (value or [""]) if isinstance(value, list) else [value]
    if t not in ("coPoints", "coStrings"):    # the tab shows the first entry (machine limits: normal mode)
        vals = vals[:1]
    out = []
    for x in vals:
        x = str(x)
        if dfn.get("filament") and t.startswith("coInt"):    # filament pickers: 0 is Default
            x = tr("Default") if x == "0" else f"Filament {x}"
        elif t.startswith("coBool"):
            x = "On" if x in ("1", "true") else "Off"
        elif t.startswith("coEnum") and x in dfn["enum_values"] and dfn["enum_labels"]:
            x = tr(dfn["enum_labels"][dfn["enum_values"].index(x)])
        elif t.startswith("coString") and x in ("", "[]"):
            x = "Empty"
        elif t.startswith("coPercent"):
            x = x if x.endswith("%") else x + "%"
        elif side and re.fullmatch(r"-?[\d.]+", x):
            unit = tr(side).replace(" or %", "")
            x = x + ("" if unit in ("°", "%") else " ") + unit
        out.append(x)
    return ", ".join(out)


def rows():
    """[{group, tab, section, label, keys, value}] for every default setting Orca shows, values as displayed."""
    d, dfs = defaults(), defs(version())
    out = []
    for group, tab, section, label, keys in layout(version()):
        vals = [str(len(d[group]["nozzle_diameter"])) if k == "extruders_count" else
                display(dfs.get(k, {}), d[group][k]) if k in d[group] else
                display(dfs[k], dfs[k]["builtin"]) if "builtin" in dfs.get(k, {}) else "(not in Orca's export)"
                for k in keys]
        out.append({"group": group, "tab": tr(tab), "section": tr(section), "label": tr(label), "keys": keys,
                    "value": vals[0] if len(vals) == 1 else ", ".join(vals)})
    organic = {r["keys"][0] for r in out if r["keys"] and r["keys"][0].endswith("_organic")}
    for r in out:    # Tree supports: Orca shows the _organic twin for the Default and Organic styles
        if len(r["keys"]) == 1 and r["keys"][0] + "_organic" in organic:
            r["label"] += " (other tree styles)"
    return out


def defaults():
    """{"printer": {key: value}, "process": {key: value}} from Orca's export of the two presets (cached)."""
    v = version()
    os.makedirs(CACHE, exist_ok=True)
    out = f"{CACHE}/defaults-{v}.json"
    if not os.path.exists(out):
        files = []
        for group, (kind, name) in PRESETS.items():
            files.append(f"{CACHE}/{group}.json")
            json.dump(resolve(kind, name), open(files[-1], "w"), indent=1)
        env = dict(os.environ, LD_LIBRARY_PATH=f"{ORCA}/stubs:{ORCA}/squashfs-root/bin")
        subprocess.run([f"{ORCA}/squashfs-root/bin/orca-slicer", "--datadir", f"{ORCA}/dd", "--load-settings",
                        ";".join(files), "--export-settings", f"{CACHE}/export.json"],
                       cwd=CACHE, env=env, capture_output=True, timeout=300)
        full = json.load(open(f"{CACHE}/export.json"))
        lists = key_lists(v)
        json.dump({g: {k: full[k] for k in sorted(lists[g]) if k in full} for g in PRESETS}
                  | {"missing": {g: sorted(k for k in lists[g] - SKIP - {"compatible_printers"} if k not in full) for g in PRESETS}},
                  open(out, "w"), indent=1)
    return json.load(open(out))


def show(value):
    if isinstance(value, list) and value and all(x == value[0] for x in value):
        value = value[0]
    return value if isinstance(value, str) else json.dumps(value)


def main(argv):
    if not argv:
        print(__doc__.strip().split("\n\n")[1])
        return 1
    d = defaults()
    if argv[0] == "--diff":
        with zipfile.ZipFile(argv[1]) as z:
            proj = json.loads(z.read("Metadata/project_settings.config"))
        print(f"settings: printer {proj.get('printer_settings_id')}, process {proj.get('print_settings_id')}")
        n = 0
        for g in PRESETS:
            for k, v in proj.items():
                if k in SKIP or k not in d[g] or show(v) == show(d[g][k]):
                    continue
                n += 1
                print(f"{g}: {k}: file {show(v)}; default {show(d[g][k])}")
        print(f"{n} differ")
        return 0
    groups = [a for a in argv if a in PRESETS] or list(PRESETS)
    query = " ".join(a for a in argv if a not in PRESETS).lower().replace(" ", "_")
    found = 0
    for g in groups:
        for k, v in d[g].items():
            if query in k:
                found += 1
                print(f"{g}: {k}: {show(v)}")
        for k in d["missing"][g]:
            if query in k:
                found += 1
                b = defs(version()).get(k, {}).get("builtin")
                print(f"{g}: {k}: " + (f"{b!r} (built-in)" if b is not None else "(not in Orca's export)"))
    if not found:
        print(f"orcadefaults: no default setting matches '{query}'")
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
