#!/usr/bin/env python3
"""
Build the internal Hur Lab Research Overview page from the website data.

Fills scripts/templates/overview_template.html (version 2 design, November 2026: section navigator,
co-author network, NIH iCite figures, honors, idea cards) with data/publications.json, grants.json,
tools.json, overview.json, honors.json, coauthors.json, metrics.json and the internal-only
overview_internal.json (page wording, project ideas, era narratives, pilot-award sentence), and
writes the result to the lab OneDrive Publications folder as Hur_Lab_Research_Overview.html. The page
is NOT published under the web root.

Differences from the public page, by decision of Dr. Hur: the idea cards and the pilot-award sentence
are internal only, and the VIOLIN 2.0 administrative supplement is merged into its parent award here
(the public page lists it as its own row under the parent).

Spec: OVERVIEW_BUILD_SPEC.md in the OneDrive Publications/_overview_build folder.

overview_internal.json lives outside the repo and the web root, in the OneDrive folder next to the
spec (Publications/_overview_build/), so every build machine reads the same copy; override with
--internal or $HURLAB_OVERVIEW_INTERNAL. Dr. Hur edits it by hand.

Called at the end of build_data.py (also when build_data finds nothing to rebuild, so a server
CV publish pulled in with git is picked up). Runs only on the build machine: when the OneDrive
folder is not mounted (e.g. on the web server) it skips quietly.

Usage:
  python3 scripts/build_overview.py            # build and write the page
  python3 scripts/build_overview.py --stdout   # print the page instead of writing it
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from cvlib import is_supplement, norm
from pubmeta import CACHE as PUBMED_CACHE, cv_authors

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "scripts" / "templates" / "overview_template.html"
WEBINF_LOG = ROOT / "WEB-INF" / "cv-updates" / "applied.jsonl"  # server CV publishes (cv_publish.py)
DEFAULT_OUT = Path("/mnt/c/JHCloud/OneDrive - North Dakota University System/!HURLAB/"
                   "9_General - UND Hur Lab/Publications/Hur_Lab_Research_Overview.html")
DEFAULT_INTERNAL = Path(os.environ.get("HURLAB_OVERVIEW_INTERNAL",
                                       DEFAULT_OUT.parent / "_overview_build" / "overview_internal.json"))

INJECT = "/*__OVERVIEW_DATA__*/"
FIRST_YEAR = 2004  # first publication year; YEARS_SPAN counts from here
ROLE = {"first": "F", "corresponding": "C"}  # coauthor / None -> ""
SELF_SHORT, SELF_FULL = "Hur J", "Junguk Hur"  # the template drops "et al." only for SELF_FULL
EM_DASH = "—"


def no_em_dash(value):
    """Recursively replace em dashes in every string (same rule as cvlib.no_em_dash)."""
    if isinstance(value, str):
        return value.replace(f" {EM_DASH} ", ", ").replace(EM_DASH, "-")
    if isinstance(value, list):
        return [no_em_dash(v) for v in value]
    if isinstance(value, dict):
        return {k: no_em_dash(v) for k, v in value.items()}
    return value


def first_author(text):
    """'*Huang F, Hur J$, ...' -> 'Huang F'; 'Bai JPF and Hur J. ...' -> 'Bai JPF'."""
    head = re.split(r",| and |\. ", text or "", maxsplit=1)[0]
    name = head.replace("*", "").replace("$", "").strip()
    return SELF_FULL if name == SELF_SHORT else name


def page_title(title):
    """Drop one trailing period (the website titles carry it; the page shows titles without it,
    and the cite line already ends the venue with '. '). An ellipsis is left alone."""
    return title[:-1] if title.endswith(".") and not title.endswith("..") else title


def decimal_year(ym):
    """'2022-07' -> 2022.5 (year + (month-1)/12, 2 decimals)."""
    year, month = (int(x) for x in ym.split("-")[:2])
    return round(year + (month - 1) / 12, 2)


def build_pubs(pubs_doc, pubmed=None):
    """pubmed: {pmid: [authors]} (scripts/cache/pubmed_authors.json); the CV list is the fallback."""
    pubmed = pubmed or {}
    out = []
    for p in sorted(pubs_doc["peerReviewed"], key=lambda r: r["number"]):
        rec = {
            "id": p["number"],
            "cat": p["category"],
            "year": p["year"],
            "venue": p.get("journal") or "",
            "title": page_title(p["title"]),
            "first": first_author(p["text"]),
            "theme": p["areaIndex"] + 1,
            "pmid": p.get("pmid") or "",
            "doi": p.get("doi") or "",
            "r": ROLE.get(p.get("authorship"), ""),
            "solo": len(pubmed.get(p.get("pmid") or "") or cv_authors(p["text"])) == 1,
        }
        if p.get("topicFolder"):
            rec["folder"] = p["topicFolder"]
        out.append(rec)
    return out


def build_themes(pubs_doc):
    return {str(i + 1): name for i, name in enumerate(pubs_doc["areas"])}


def build_key(pubs_doc, overview_doc):
    index = {name: i + 1 for i, name in enumerate(pubs_doc["areas"])}
    key = {str(t): [] for t in index.values()}
    for area, numbers in overview_doc.get("highlights", {}).items():
        if area in index:
            key[str(index[area])] = [int(n) for n in numbers]
    return key


def build_grants(grants_doc):
    grants = grants_doc["current"] + grants_doc["previous"]
    # a supplement is merged into its parent award: the parent title names it, the row is dropped
    sup_years = {}
    for g in grants:
        if is_supplement(g):
            parent = norm(re.sub(r"^administrative supplement:\s*", "", g["title"], flags=re.I))
            sup_years[parent] = f'{g["start"][:4]} to {g["end"][:4]}'
    out = []
    for g in grants:
        title = g["title"]
        if norm(title) in sup_years:
            title += f" (includes the {sup_years[norm(title)]} administrative supplement)"
        rec = {"t": title, "f": g["agency"], "r": g["role"],
               "s": decimal_year(g["start"]), "e": decimal_year(g["end"]),
               "a": g["status"] == "active"}
        if g.get("type") == "internal":
            rec["i"] = True
        if not is_supplement(g):  # a supplement is merged into its parent award on this page
            out.append(rec)
    # active first, then newest start first (the template groups external and internal itself)
    out.sort(key=lambda r: (not r["a"], -r["s"]))
    return out


def build_tools(tools_doc):
    tools = tools_doc if isinstance(tools_doc, list) else tools_doc.get("tools", [])
    return [[t["name"], t.get("description", ""), t.get("url") or t.get("github") or ""] for t in tools]


def last_publish_date(log_path=WEBINF_LOG):
    """Date of the newest server CV publish that was not rolled back (applied.jsonl), or None."""
    path = Path(log_path)
    if not path.exists():
        return None
    runs, rolled_back = {}, set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("op") == "rollback":
            rolled_back.add(rec.get("rollbackOf"))
        elif rec.get("run") and rec.get("at"):
            runs[rec["run"]] = max(runs.get(rec["run"], ""), rec["at"])
    live = [at for run, at in runs.items() if run not in rolled_back]
    return date.fromisoformat(max(live)[:10]) if live else None


def cv_date(pubs_doc, grants_doc, log_path=WEBINF_LOG):
    """The CV date: the newer of the date in the CV filename (grants.json source) and the
    newest live server publish. publications.json lastUpdated is only the fallback: it is the
    build date and moves on every rebuild, even when nothing in the CV changed."""
    dates = []
    m = re.match(r"(\d{4}-\d{2}-\d{2})", grants_doc.get("source", ""))
    if m:
        dates.append(date.fromisoformat(m.group(1)))
    published = last_publish_date(log_path)
    if published:
        dates.append(published)
    if not dates and pubs_doc.get("lastUpdated"):
        dates.append(date.fromisoformat(pubs_doc["lastUpdated"]))
    d = max(dates) if dates else date.today()
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def long_date(iso):
    """'2026-11-22' -> 'November 22, 2026'; '' when unknown."""
    if not iso:
        return ""
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def js_const(name, value):
    # "</" would end the <script> block early; JSON allows the "\/" escape.
    literal = json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"const {name}={literal};"


def render(data_dir=DATA, internal_path=DEFAULT_INTERNAL, template_path=TEMPLATE, today=None):
    data_dir = Path(data_dir)
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    pubs_doc = load(data_dir / "publications.json")
    grants_doc = load(data_dir / "grants.json")
    tools_doc = load(data_dir / "tools.json")
    overview_doc = load(data_dir / "overview.json")

    def optional(name, default):
        return load(data_dir / name) if (data_dir / name).exists() else default
    honors = optional("honors.json", [])
    coauthors = optional("coauthors.json", {})
    metrics = optional("metrics.json", {})
    internal = load(internal_path)
    today = today or date.today()

    pubmed = load(PUBMED_CACHE) if Path(PUBMED_CACHE).exists() else {}
    pubs = build_pubs(pubs_doc, pubmed)
    tools = build_tools(tools_doc)
    consts = [
        ("PUBS", pubs),
        ("THEMES", build_themes(pubs_doc)),
        ("KEY", build_key(pubs_doc, overview_doc)),
        ("GRANTS", build_grants(grants_doc)),
        ("PILOTS", internal["pilotsNote"]),
        ("ERAS", internal["eras"]),
        ("TOOLS", tools),
        ("IDEAS", internal["ideas"]),
        ("HONORS", honors),
        ("COAUTH_DATA", {int(k): v for k, v in coauthors.items()}),
        ("METRICS", metrics.get("by_pmid", {})),
    ]
    block = "\n".join(js_const(n, no_em_dash(v)) for n, v in consts)

    page = Path(template_path).read_text(encoding="utf-8")
    if page.count(INJECT) != 1:
        raise SystemExit(f"build_overview: template must contain {INJECT} exactly once")
    page = page.replace(INJECT, block)
    for key, text in internal["text"].items():  # page wording first: it carries the computed fields below
        page = page.replace("{{" + key + "}}", no_em_dash(text))
    page = (page.replace("{{YEARS_SPAN}}", str(today.year - FIRST_YEAR))
                .replace("{{CV_DATE}}", no_em_dash(cv_date(pubs_doc, grants_doc)))
                .replace("{{N_TOOLS}}", str(len(tools)))
                .replace("{{METRICS_DATE}}", long_date(metrics.get("retrieved"))))
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", page)
    if leftover:
        raise SystemExit(f"build_overview: unfilled placeholders {sorted(set(leftover))}")
    if EM_DASH in page:
        raise SystemExit("build_overview: refusing to write, the page contains an em dash")
    return page


def run(out=DEFAULT_OUT, internal=DEFAULT_INTERNAL, data_dir=DATA, quiet_if_unmounted=True):
    """Build and write the page. Returns 0 on success or a quiet skip; raises on a real error."""
    out = Path(out)
    if not out.parent.is_dir():
        if quiet_if_unmounted:
            print(f"build_overview: {out.parent} not reachable (OneDrive not mounted here); skipped")
            return 0
        raise SystemExit(f"build_overview: output folder not found: {out.parent}")
    if not Path(internal).exists():
        raise SystemExit(f"build_overview: internal file not found: {internal} "
                         "(keep it outside the web root; see --internal)")
    page = render(data_dir, internal)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(page, encoding="utf-8")
    os.replace(tmp, out)
    print(f"build_overview: wrote {out} ({len(page):,} bytes)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output HTML (default: OneDrive Publications)")
    ap.add_argument("--internal", default=str(DEFAULT_INTERNAL), help="overview_internal.json")
    ap.add_argument("--data", default=str(DATA), help="website data directory")
    ap.add_argument("--stdout", action="store_true", help="print the page instead of writing it")
    args = ap.parse_args(argv)
    if args.stdout:
        sys.stdout.write(render(args.data, args.internal))
        return 0
    return run(args.out, args.internal, args.data, quiet_if_unmounted=False)


if __name__ == "__main__":
    sys.exit(main())
