#!/usr/bin/env python3
"""
Build the site's publication, grant and overview data from two read-only sources:

  1. The publication tracker (Excel, sheet "Publications", one row per publication)
  2. The PI's CV (.docx): Education, Research interests, Professional Experience, Grant

Outputs (all public, under data/):
  - publications.json  peerReviewed[] = every tracker record (key name kept for the existing pages),
                       each with a primary research area; talks/posters/profiles/patent are carried
                       over from the existing file (scripts/parse_cv.py maintains those)
  - grants.json        funded grants only (current + previous); no dollar amounts, no pending proposals
  - overview.json      research interests, career eras and milestones for research-overview.html
  - index.html         static (no-JavaScript) copies of the home page counters, recent publications
                       and funding list, written between <!-- BUILD:... --> markers

Area corrections live in data/area_overrides.json and survive every rebuild.

Usage:
  python3 scripts/build_data.py                 # rebuild only if a source is newer than the outputs
  python3 scripts/build_data.py --force         # rebuild unconditionally
  python3 scripts/build_data.py --if-available  # exit quietly when the sources are not reachable
                                                # (used by parse_cv.py on the server)
Source paths can be overridden with --tracker / --cv or HURLAB_TRACKER / HURLAB_CV.
"""

import argparse
import html
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from cvlib import (authorship, cv_paragraphs, merge_supplements, no_em_dash, norm,
                   parse_cv_publications, parse_grants, ym)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_PUBS = DATA / "publications.json"
OUT_GRANTS = DATA / "grants.json"
OUT_OVERVIEW = DATA / "overview.json"
OVERRIDES = DATA / "area_overrides.json"
RESEARCH = DATA / "research.json"
INDEX = ROOT / "index.html"

DEFAULT_TRACKER = ("/mnt/c/JHCloud/OneDrive - North Dakota University System/!HURLAB/"
                   "9_General - UND Hur Lab/Publications/Hur_Publications_PDF_Tracker.xlsx")
DEFAULT_CV = ("/mnt/c/JHCloud/Dropbox (Personal)/PERSONAL/Career/Career Development/"
              "2_Curriculum Vitae/2026-10-30_JungukHur-CV.docx")

HOME_RECENT_COUNT = 5
HOME_CATEGORIES = ("Article", "Review")  # the home page strip shows research papers only (same rule in index.html)
TODAY = date.today()

# Research areas, in data/research.json order (research-detail.html?area=<index>)
BIO, ONTO, AI, NEURO, HPI, PHARM = range(6)

# Topic subfolder -> area. None = classify by title.
FOLDER_AREA = {
    "1_Diabetes_Metabolic_Neuropathy": NEURO,
    "2_Neurodegeneration_ALS": NEURO,
    "3_SystemsPharm_DrugSafety_Tox": PHARM,
    "4_TextMining_Ontology_AI": "onto-or-ai",
    "5_Infection_Immunity_Vaccines": HPI,
    "6_Epidemiology_PublicHealth": None,
    "7_Genomics_Methods_Other": None,
    "8_Preprints_arXiv_bioRxiv": None,
    "9_Conference_Full_Papers": None,
}

# Title rules for papers without a topic folder that decides the area. Checked in this order: the
# conference papers and preprints are mostly method papers, so the method areas (AI, ontology) win
# over the application topic named in the same title.
TITLE_RULES = [
    (AI, r"machine learning|deep learning|neural network|artificial intelligence|large language|\bllms?\b|"
         r"transformer|chatgpt|\bgpt|predictive model|classifier|\bai\b|fine-tuning|gradient boosting|\bbert\b"),
    (ONTO, r"ontolog|literature mining|text mining|natural language|\bnlp\b|knowledge ?base|semantic|sciminer"),
    (HPI, r"vaccin|infect|viral|virus|bacteri|pathogen|immun|covid|sars-cov|influenza|lyme|borrelia|"
          r"\brsv\b|pneumo|sepsis|t cell|cd8|antibod|microbio"),
    (PHARM, r"\bdrugs?\b|adverse drug|adverse event|pharmac|toxic|\btox21\b|chemical|compound|polypharmacy|"
            r"repurpos|medication"),
    (NEURO, r"neuropath|diabet|\bals\b|amyotrophic|alzheimer|parkinson|epilep|neurodegener|\bnerve|brain|"
            r"neuro|schwann|\bcognit|dementia|autism|hippocamp|microglia|synuclein|obes|prediabet|metabolic"),
    (BIO, r"single-cell|rna-seq|transcriptom|methylation|epigen|proteogenom|genom|pipeline|clustering|"
          r"gene expression|data model|integration"),
]
AI_RULE = dict(TITLE_RULES)[AI]

report = []  # lines for the end-of-run review list


def note(msg):
    report.append(msg)


def clean(value):
    """Normalize a cell value: None for blanks, strip text, no em dashes."""
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    if text in ("", "None", "nan", "NaN", "-"):
        return None
    return no_em_dash(text)


# ---------------------------------------------------------------- freshness check

def is_up_to_date(sources):
    outputs = [OUT_PUBS, OUT_GRANTS, OUT_OVERVIEW]
    if not all(p.exists() for p in outputs):
        return False
    inputs = [p for p in sources + [Path(__file__), OVERRIDES, RESEARCH] if p.exists()]
    return min(p.stat().st_mtime for p in outputs) >= max(p.stat().st_mtime for p in inputs)


# ---------------------------------------------------------------- publications

def load_tracker(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Publications"].iter_rows(values_only=True))
    header = [str(h).strip() if h is not None else "" for h in rows[0]]
    return [dict(zip(header, r)) for r in rows[1:] if any(v is not None for v in r)]


def classify(title, folder):
    """Return (area index, source, detail). source: folder | folder+title | title | default."""
    t = (title or "").lower()
    hint = FOLDER_AREA.get(folder, None)
    if isinstance(hint, int):
        return hint, "folder", folder
    if hint == "onto-or-ai":
        if re.search(AI_RULE, t):
            return AI, "folder+title", "AI terms in title"
        return ONTO, "folder+title", "no AI terms in title"
    hits = [(area, re.search(rule, t).group(0)) for area, rule in TITLE_RULES if re.search(rule, t)]
    if not hits:
        return BIO, "default", "no title rule matched"
    detail = "; ".join(f"{a}:{kw}" for a, kw in hits)
    return hits[0][0], "title", detail


def match_cv_entry(entries, pmid, doi, title, is_preprint):
    """The CV entry for a tracker row: by PMID, then DOI, then title text. A title shared by a
    preprint and its published version is resolved by the CV subsection (Preprint or not)."""
    tests = []
    if pmid:
        tests.append(lambda e: re.search(rf"\b{re.escape(pmid)}\b", e["text"]))
    if doi:
        tests.append(lambda e: doi.lower() in e["text"].lower())
    if title and len(norm(title)) > 8:
        tests.append(lambda e: norm(title) in norm(e["text"]))
        bare = norm(re.sub(r"\(.*?\)", "", title))  # tracker titles can carry a "(series, vol)" suffix
        if bare != norm(title) and len(bare) > 8:
            tests.append(lambda e: bare in norm(e["text"]))
    for test in tests:
        hits = [e for e in entries if not e["used"] and test(e)]
        if len(hits) > 1:
            hits = [e for e in hits if e["section"].startswith("Preprint") == is_preprint]
        if len(hits) == 1:
            hits[0]["used"] = True
            return hits[0]
    return None


def build_publications(rows, area_titles, overrides, cv_entries):
    area_override = {str(k): v for k, v in overrides.get("areas", {}).items()}
    pubs = []
    for row in rows:
        num = clean(row.get("#"))
        title = clean(row.get("Title"))
        folder = clean(row.get("Topic subfolder (OneDrive)"))
        area, source, detail = classify(title, folder)
        if num in area_override:
            wanted = area_override[num]
            if wanted in area_titles:
                area, source, detail = area_titles.index(wanted), "override", "data/area_overrides.json"
            else:
                note(f"OVERRIDE IGNORED: #{num} names unknown area {wanted!r}")
        category = clean(row.get("Category"))
        year = clean(row.get("Year"))
        pmid, pmcid, doi = clean(row.get("PMID")), clean(row.get("PMCID")), clean(row.get("DOI"))
        # Author string and marks come from the CV (the tracker's citation column can lag behind it)
        entry = match_cv_entry(cv_entries, pmid, doi, title, category == "Preprint")
        if entry:
            text = entry["text"]
        else:
            text = clean(row.get("CV citation"))
            note(f"NOT FOUND IN CV (tracker citation used): #{num} ({category}) {title}")
            if text and re.search(r"\(NOT IN CV\)", text, re.I):
                text = re.sub(r"\s*\(NOT IN CV\)", "", text, flags=re.I)
        pub = {
            "number": int(num) if num and num.isdigit() else num,
            "text": text,
            "title": title,
            "journal": clean(row.get("Journal / Venue")),
            "year": int(year) if year and str(year).isdigit() else None,
            "category": category,
            "isPreprint": category == "Preprint",
            "isPeerReviewed": entry["peerReviewed"] if entry else None,
            "cvSection": entry["section"] if entry else None,
            "authorship": authorship(text, category),
            "pmid": pmid,
            "pmcid": pmcid,
            "doi": doi,
            "links": {
                "pubmed": clean(row.get("PubMed link")) or (f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None),
                "pmc": clean(row.get("PMC link")) or (f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else None),
                "doi": clean(row.get("DOI / full-text link")) or (f"https://doi.org/{doi}" if doi else None),
            },
            "area": area_titles[area],
            "areaIndex": area,
            "areaSource": source,
            "areaDetail": detail,
            "topicFolder": folder,
        }
        if not pub["text"] or "Hur J" not in pub["text"]:
            note(f"NO 'Hur J' IN AUTHORS: #{num} ({category}) {title}")
        if pub["year"] is None:
            note(f"NO YEAR: #{num} {title}")
        if source == "default":
            note(f"AREA DEFAULTED to {area_titles[area]}: #{num} [{folder}] {title}")
        elif source == "title" and len(set(d.split(':')[0] for d in detail.split('; '))) > 1:
            note(f"AREA AMBIGUOUS (picked {area_titles[area]}; matches {detail}): #{num} [{folder}] {title}")
        pubs.append(pub)
    for e in cv_entries:
        if not e["used"]:
            note(f"CV ENTRY WITHOUT TRACKER ROW ({e['section'][:30]}): {e['text'][:110]}")
    pubs.sort(key=lambda p: (-(p["year"] or 0), -(p["number"] if isinstance(p["number"], int) else 0)))
    return pubs


def pick_highlights(pubs, area_titles, overrides):
    """Up to 3 highlight papers per area: override list, else newest articles where Hur J is corresponding or last."""
    chosen = {}
    by_num = {str(p["number"]): p for p in pubs}
    for idx, title in enumerate(area_titles):
        manual = overrides.get("highlights", {}).get(title)
        if manual:
            chosen[title] = [str(n) for n in manual if str(n) in by_num][:3]
            continue
        pool = [p for p in pubs if p["areaIndex"] == idx and p["category"] in ("Article", "Review")
                and p["text"] and p["areaSource"] != "default"]
        lead = [p for p in pool if re.search(r"Hur J\$|Hur J\.?\s*$|and Hur J\b", p["text"].rstrip(". "))]
        picks = (lead + [p for p in pool if p not in lead])[:3]
        chosen[title] = [str(p["number"]) for p in picks]
    return chosen


# ---------------------------------------------------------------- CV

def parse_profile(paras):
    """Education + appointments + professional positions -> entries with start/end, and research interests."""
    lines = [t.strip() for t, _ in paras if t.strip()]
    def block(start, stops):
        if start not in lines:
            note(f"CV SECTION NOT FOUND: {start}")
            return []
        out = []
        for t in lines[lines.index(start) + 1:]:
            if t in stops:
                break
            out.append(t)
        return out

    interests = block("Research interests", {"Professional Experience"})
    education = []
    edu = block("Education", {"Research interests"})
    for i, t in enumerate(edu):
        m = re.match(r"(Ph\.D\.|M\.S\.|B\.S\.|Post-doc):\s*(.+)", t)
        if m and i + 1 < len(edu):
            yrs = re.search(r"(\d{4})\s*~\s*(\d{4})", edu[i + 1])
            if yrs:
                education.append({"kind": m.group(1), "what": m.group(2).strip(),
                                  "start": f"{yrs.group(1)}-01", "end": f"{yrs.group(2)}-12"})
    positions = []
    for t in block("Professional Experience", {"Honors and Awards"}):
        m = re.match(r"([A-Za-z]{3}\.?\s*\d{4})\s*~\s*([A-Za-z]{3}\.?\s*\d{4})?\s*(.+)", t)
        if not m and positions and positions[-1]["what"].endswith(","):
            positions[-1]["what"] += " " + t  # entry continued on the next line
            continue
        if m:
            positions.append({"start": ym(m.group(1)), "end": ym(m.group(2)) if m.group(2) else None,
                              "what": m.group(3).strip()})
    for p in positions:
        p["what"] = p["what"].rstrip(",")
    return interests, education, positions


def build_overview(interests, education, positions, pubs, area_titles):
    """Career eras (main training/appointment line) with the dominant areas of each era's papers."""
    def find(entries, pattern):
        return next((e for e in entries if re.search(pattern, e["what"])), None)
    era_specs = [
        ("M.S., Indiana University", find(education, r"Indiana")),
        ("Ph.D., University of Michigan", next((e for e in education if e["kind"] == "Ph.D."), None)),
        ("Postdoc, University of Michigan", next((e for e in education if e["kind"] == "Post-doc"), None)),
        ("Assistant Professor, UND", find(positions, r"Assistant Professor, University of North Dakota")),
        ("Associate Professor, UND", find(positions, r"Associate Professor, University of North Dakota")),
    ]
    eras = []
    for label, e in era_specs:
        if not e:
            note(f"ERA NOT FOUND IN CV: {label}")
            continue
        eras.append({"label": label, "start": e["start"], "end": e["end"]})
    # A paper belongs to the latest era that has started by its year
    for i, era in enumerate(eras):
        y0 = int(era["start"][:4])
        y1 = int(eras[i + 1]["start"][:4]) - 1 if i + 1 < len(eras) else TODAY.year
        if i + 1 < len(eras) and eras[i + 1]["start"][5:] == "01":
            y1 = int(eras[i + 1]["start"][:4]) - 1
        mine = [p for p in pubs if p["year"] and y0 <= p["year"] <= y1]
        counts = {}
        for p in mine:
            counts[p["area"]] = counts.get(p["area"], 0) + 1
        era["pubYears"] = [y0, y1]
        era["publications"] = len(mine)
        era["themes"] = [a for a, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:3]]
        era["areaCounts"] = counts
    milestones = [p for p in positions if not re.search(r"(Assistant|Associate) Professor, University of North Dakota", p["what"])
                  and p["start"] and p["start"] >= "2004"]
    return {"researchInterests": interests, "eras": eras, "milestones": milestones, "areas": area_titles}


# ---------------------------------------------------------------- home page static fallback

def esc(s):
    return html.escape(s or "", quote=True)


def bold_hur(citation):
    return re.sub(r"(Hur J)(?=[\s,.*$]|$)", r"<strong>\1</strong>", esc(citation))


def write_home_fallback(pubs, grants):
    if not INDEX.exists():
        return
    recent = [p for p in pubs if p["category"] in HOME_CATEGORIES][:HOME_RECENT_COUNT]
    pub_items = "\n".join(
        f'                    <li class="text-sm text-gray-700">{bold_hur(p["text"])}'
        + (f' <a class="text-indigo-700 underline" href="{esc(p["links"]["pubmed"])}">PubMed</a>' if p["links"]["pubmed"] else "")
        + "</li>" for p in recent)
    grant_items = "\n".join(
        f'                    <li class="text-sm text-gray-700"><strong>{esc(g["funder"])}</strong>: {esc(g["title"])} '
        f'({esc(g["role"])}, {g["start"][:4]}-{g["end"][:4]})</li>' for g in grants["current"])
    tools_file = DATA / "tools.json"
    blocks = {
        "active-grants": str(len(grants["current"])),
        "publication-count": str(len(pubs)),
        "tool-count": str(len(json.loads(tools_file.read_text()))) if tools_file.exists() else "...",
        "recent-publications": f'\n            <ol class="nojs-fallback max-w-3xl mx-auto list-decimal pl-6 space-y-2">\n{pub_items}\n            </ol>\n            ',
        "funding": f'\n            <ul class="nojs-fallback max-w-3xl mx-auto list-disc pl-6 space-y-1">\n{grant_items}\n            </ul>\n            ',
    }
    page = INDEX.read_text(encoding="utf-8")
    for name, content in blocks.items():
        pattern = re.compile(rf"(<!-- BUILD:{name} -->).*?(<!-- /BUILD:{name} -->)", re.S)
        if not pattern.search(page):
            note(f"INDEX MARKER MISSING: BUILD:{name}")
            continue
        page = pattern.sub(lambda m: m.group(1) + content + m.group(2), page)
    INDEX.write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- main

def write_json(path, obj):
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if "—" in text:
        raise SystemExit(f"refusing to write {path.name}: contains an em dash")
    path.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tracker", default=os.environ.get("HURLAB_TRACKER", DEFAULT_TRACKER))
    ap.add_argument("--cv", default=os.environ.get("HURLAB_CV", DEFAULT_CV))
    ap.add_argument("--force", action="store_true", help="rebuild even if outputs are newer than the sources")
    ap.add_argument("--if-available", action="store_true", help="exit 0 quietly when a source is missing")
    args = ap.parse_args()

    sources = [Path(args.tracker), Path(args.cv)]
    missing = [str(p) for p in sources if not p.exists()]
    if missing:
        msg = "source not found: " + ", ".join(missing)
        if args.if_available:
            print(f"build_data: {msg}; outputs left unchanged")
            return 0
        raise SystemExit(f"build_data: {msg}")
    if not args.force and is_up_to_date(sources):
        print("build_data: outputs are newer than the sources; nothing to do (use --force to rebuild)")
        return 0

    area_titles = [a["title"] for a in json.loads(RESEARCH.read_text())["areas"]]
    overrides = json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    old = json.loads(OUT_PUBS.read_text()) if OUT_PUBS.exists() else {}
    old_grants = json.loads(OUT_GRANTS.read_text()) if OUT_GRANTS.exists() else {}

    paras = list(cv_paragraphs(args.cv))
    pubs = build_publications(load_tracker(args.tracker), area_titles, overrides, parse_cv_publications(paras))
    grants = merge_supplements(parse_grants(paras, note, TODAY), note)
    for g in grants:
        g.pop("cvSection", None)
    # Keep hand-added links (e.g. NIH RePORTER) from the previous file, matched by title
    old_urls = {g.get("title", "").lower(): g["url"] for k in ("current", "previous")
                for g in old_grants.get(k, []) if g.get("url")}
    for g in grants:
        if g["title"].lower() in old_urls:
            g["url"] = old_urls[g["title"].lower()]
    grants_out = {
        "current": sorted([g for g in grants if g["status"] == "active"], key=lambda g: g["start"] or "", reverse=True),
        "previous": sorted([g for g in grants if g["status"] == "completed"], key=lambda g: g["end"] or "", reverse=True),
        "lastUpdated": TODAY.isoformat(),
        "source": Path(args.cv).name,
    }
    interests, education, positions = parse_profile(paras)
    overview = build_overview(interests, education, positions, pubs, area_titles)
    overview["highlights"] = pick_highlights(pubs, area_titles, overrides)
    overview["lastUpdated"] = TODAY.isoformat()

    pubs_out = {
        "profiles": old.get("profiles", {}),
        "peerReviewed": pubs,
        "talks": old.get("talks", []),
        "posters": old.get("posters", []),
        "patent": old.get("patent", {}),
        "areas": area_titles,
        "lastUpdated": TODAY.isoformat(),
        "source": Path(args.tracker).name,
    }
    write_json(OUT_PUBS, pubs_out)
    write_json(OUT_GRANTS, grants_out)
    write_json(OUT_OVERVIEW, overview)
    write_home_fallback(pubs, grants_out)

    by_area = {}
    for p in pubs:
        by_area.setdefault(p["area"], {}).setdefault(p["areaSource"], 0)
        by_area[p["area"]][p["areaSource"]] += 1
    print(f"build_data: {len(pubs)} publications, {len(grants_out['current'])} active + "
          f"{len(grants_out['previous'])} completed grants, {len(overview['eras'])} eras")
    for area in area_titles:
        print(f"  {area}: {sum(by_area.get(area, {}).values())} {by_area.get(area, {})}")
    if report:
        print(f"\nREVIEW ({len(report)} items):")
        for line in report:
            print("  - " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
