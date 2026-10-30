#!/usr/bin/env python3
"""
Compare a new CV (.docx) against what is published (or against an older CV) and classify every
difference for review. Read-only: prints a report and can write it as JSON; it changes nothing.

Usage:
  python3 scripts/cv_diff.py --new-cv NEW.docx                      # vs data/publications.json + grants.json
  python3 scripts/cv_diff.py --old-cv OLD.docx --new-cv NEW.docx    # CV vs CV (used by the tests)
  ... --json out.json                                               # also write the items as JSON

Item kinds (one record or grant can carry several):
  NEW, CHANGED, METADATA (pre-accepted refresh), PREPRINT-NOW-PUBLISHED, SAME-PAPER?,
  CATEGORY-MOVED, AUTHORSHIP-MARK-CHANGED, REMOVED, GRANT-NEW, GRANT-STATUS-CHANGED,
  GRANT-SECTION-MOVED, GRANT-REMOVED, FLAG
Matching: PMID, then DOI, then title similarity >= 0.90 with year +/- 1 and the same first-author
surname; 0.75-0.90 under the same conditions becomes a SAME-PAPER? item instead of NEW + REMOVED.
"""

import argparse
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from cvlib import (award_core, cv_paragraphs, cv_record, merge_supplements, norm,
                   parse_cv_publications, parse_grants, split_citation)

ROOT = Path(__file__).resolve().parent.parent
MATCH, MAYBE = 0.90, 0.75


# ---------------------------------------------------------------- loading

def load_cv(path):
    paras = list(cv_paragraphs(path))
    pubs = [cv_record(e) for e in parse_cv_publications(paras)]
    grants = merge_supplements(parse_grants(paras, include_pending=True))
    return pubs, grants


def load_published(data_dir):
    data = Path(data_dir)
    pubs = []
    for p in json.loads((data / "publications.json").read_text())["peerReviewed"]:
        # The published citation text IS the CV entry; parse it the same way as the new CV so that
        # tracker-side title/year spellings do not show up as changes.
        r = cv_record({"section": p.get("cvSection") or "", "text": p.get("text") or "",
                       "peerReviewed": p.get("isPeerReviewed")})
        r["number"] = p.get("number")
        r["category"] = r["category"] or p.get("category")
        r["isPreprint"] = r["category"] == "Preprint"
        r["pmid"] = r["pmid"] or p.get("pmid")
        r["doi"] = r["doi"] or (p.get("doi") or "").lower() or None
        pubs.append(r)
    g = json.loads((data / "grants.json").read_text())
    grants = [dict(x, status="active") for x in g.get("current", [])] + \
             [dict(x, status="completed") for x in g.get("previous", [])]
    return pubs, grants


# ---------------------------------------------------------------- matching

def similarity(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def same_author(a, b):
    return norm(a["firstAuthor"]) == norm(b["firstAuthor"]) and bool(a["firstAuthor"])


def near_year(a, b):
    return a["year"] is None or b["year"] is None or abs(a["year"] - b["year"]) <= 1


def match_records(old, new):
    """Pairs (o, n, how) plus the unmatched leftovers on each side."""
    pairs, free_old, free_new = [], list(old), list(new)

    def take(o, n, how):
        pairs.append((o, n, how))
        free_old.remove(o)
        free_new.remove(n)

    for key in ("pmid", "doi"):
        for n in list(free_new):
            if n[key]:
                hits = [o for o in free_old if o[key] == n[key]]
                if len(hits) > 1:  # a preprint and its published version can share a DOI
                    hits = [o for o in hits if o["isPreprint"] == n["isPreprint"]]
                if len(hits) == 1:
                    take(hits[0], n, key)
    scored = sorted(((similarity(o["title"], n["title"]), id(o), id(n), o, n)
                     for o in free_old for n in free_new
                     if same_author(o, n) and near_year(o, n) and o["isPreprint"] == n["isPreprint"]),
                    key=lambda t: -t[0])
    for score, _, _, o, n in scored:
        if score >= MATCH and o in free_old and n in free_new:
            take(o, n, f"title {score:.2f}")
    return pairs, free_old, free_new


# ---------------------------------------------------------------- classification

def marks(rec):
    return {name: m for name, m in rec["authors"]}


def venue(rec):
    _, _, rest = split_citation(rec["text"])
    return norm(re.split(r"[.]\s", rest)[0]) if rest else ""


def item_id(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def label(rec):
    return {k: rec.get(k) for k in ("number", "year", "category", "pmid", "doi", "title", "text", "authorship")}


def flags_for(rec, this_year):
    out = []
    if rec["peerReviewed"] and re.search(r"\bSuppl\b|:\s*S\d+\b|\babstract\b", rec["text"], re.I):
        out.append("listed as peer-reviewed but looks like an abstract or supplement")
    if rec["category"] in ("Article", "Review") and not rec["pmid"] and not rec["doi"] \
            and rec["year"] and rec["year"] < this_year:
        out.append("article without PMID or DOI")
    if rec["category"] != "Book" and not re.search(r"Hur J", rec["text"]):
        out.append("Hur J not in the byline")
    if "—" in rec["text"]:
        out.append("em dash in text")
    return out


def compare_pair(o, n):
    kinds, details = [], []
    if o["category"] != n["category"]:
        kinds.append("CATEGORY-MOVED")
        details.append(f"category {o['category']} -> {n['category']}")
    om, nm = marks(o), marks(n)
    if [a for a, _ in o["authors"]] != [a for a, _ in n["authors"]]:
        kinds.append("CHANGED")
        details.append("authors " + ", ".join(a for a, _ in o["authors"][:4]) + " ... -> "
                       + ", ".join(a for a, _ in n["authors"][:4]) + " ...")
    changed_marks = [f"{a}: '{om[a]}' -> '{nm[a]}'" for a in nm if a in om and om[a] != nm[a]]
    if changed_marks:
        kinds.append("AUTHORSHIP-MARK-CHANGED")
        details.append("marks " + "; ".join(changed_marks))
        if o.get("authorship") != n.get("authorship"):
            details.append(f"Dr. Hur's role {o.get('authorship')} -> {n.get('authorship')}")
    if similarity(o["title"], n["title"]) < 0.97:
        kinds.append("CHANGED")
        details.append(f"title {o['title'][:60]!r} -> {n['title'][:60]!r}")
    if o["year"] != n["year"]:
        if o["year"] is not None:  # None -> a year is an in-press paper getting its citation (metadata)
            kinds.append("CHANGED")
        details.append(f"year {o['year']} -> {n['year']}")
    if not kinds and norm(o["text"]) != norm(n["text"]):
        # same authors, title, year and category: only the citation tail moved
        kinds.append("CHANGED" if venue(o) and venue(n) and venue(o) != venue(n) and o["year"] is not None
                     else "METADATA")
        details.append("citation details: " + _tail_change(o["text"], n["text"]))
    return sorted(set(kinds)), details


def _tail_change(a, b):
    sm = SequenceMatcher(None, a, b)
    parts = [f"{a[i1:i2]!r} -> {b[j1:j2]!r}" for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    return "; ".join(parts)[:240]


def diff_publications(old, new, this_year):
    pairs, gone, added = match_records(old, new)
    items = []
    for o, n, how in pairs:
        kinds, details = compare_pair(o, n)
        if kinds:
            items.append({"kinds": kinds, "matchedBy": how, "old": label(o), "new": label(n),
                          "details": details, "preAccepted": kinds == ["METADATA"],
                          "flags": flags_for(n, this_year) if kinds != ["METADATA"] else []})
    # a published version of a preprint that stays on the site: offer to link the two
    for n in [x for x in added if not x["isPreprint"]]:
        best = max(((similarity(o["title"], n["title"]), o) for o in old
                    if o["isPreprint"] and same_author(o, n)), default=(0, None), key=lambda t: t[0])
        if best[0] >= MAYBE:
            items.append({"kinds": ["PREPRINT-NOW-PUBLISHED"], "matchedBy": f"title {best[0]:.2f}",
                          "old": label(best[1]), "new": label(n), "details": [],
                          "preAccepted": False, "flags": flags_for(n, this_year)})
            added.remove(n)
    # near misses: one "Same paper?" question instead of NEW + REMOVED
    for n in list(added):
        cands = [(similarity(o["title"], n["title"]), o) for o in gone if same_author(o, n) and near_year(o, n)]
        score, o = max(cands, default=(0, None), key=lambda t: t[0])
        if MAYBE <= score < MATCH:
            kinds, details = compare_pair(o, n)
            items.append({"kinds": ["SAME-PAPER?"] + kinds, "matchedBy": f"title {score:.2f}",
                          "old": label(o), "new": label(n), "details": details,
                          "preAccepted": False, "flags": flags_for(n, this_year)})
            added.remove(n)
            gone.remove(o)
    for n in added:
        items.append({"kinds": ["NEW"], "old": None, "new": label(n), "details": [],
                      "preAccepted": False, "flags": flags_for(n, this_year)})
    for o in gone:
        items.append({"kinds": ["REMOVED"], "old": label(o), "new": None,
                      "details": ["removals are never applied automatically"], "preAccepted": False, "flags": []})
    return items


def grant_key(g):
    return award_core(g["funder"]) or norm(g["title"])[:60]


def diff_grants(old, new):
    items = []
    old_by = {grant_key(g): g for g in old}
    new_by = {grant_key(g): g for g in new}
    for k, n in new_by.items():
        o = old_by.get(k)
        public = {f: n[f] for f in ("funder", "role", "title", "start", "end", "type", "status")}
        if o is None:
            if n["status"] != "pending":
                items.append({"kinds": ["GRANT-NEW"], "old": None, "new": public,
                              "details": [f"now {n['status']}"], "preAccepted": False, "flags": []})
            continue
        details, kinds = [], []
        if o["status"] != n["status"]:
            kinds.append("GRANT-STATUS-CHANGED")
            details.append(f"{o['status']} -> {n['status']}")
        if o.get("cvSection") and n.get("cvSection") and o["cvSection"] != n["cvSection"]:
            kinds.append("GRANT-SECTION-MOVED")
            details.append(f"CV section {o['cvSection']} -> {n['cvSection']}")
        for field in ("title", "role", "start", "end"):
            if norm(o.get(field)) != norm(n.get(field)):
                kinds.append("GRANT-CHANGED")
                details.append(f"{field} {o.get(field)!r} -> {n.get(field)!r}")
        if kinds and n["status"] != "pending":
            kinds = sorted(set(kinds))
            items.append({"kinds": kinds, "old": {f: o.get(f) for f in public}, "new": public,
                          "details": details, "preAccepted": False, "flags": []})
    for k, o in old_by.items():
        if k not in new_by and o["status"] != "pending":
            items.append({"kinds": ["GRANT-REMOVED"], "old": {f: o.get(f) for f in ("funder", "title", "status")},
                          "new": None, "details": ["removals are never applied automatically"],
                          "preAccepted": False, "flags": []})
    return items


def diff(old_pubs, old_grants, new_pubs, new_grants, this_year):
    items = diff_publications(old_pubs, new_pubs, this_year) + diff_grants(old_grants, new_grants)
    for it in items:
        key = (it["new"] or it["old"])
        it["id"] = item_id(",".join(it["kinds"]), key.get("pmid") or key.get("doi") or key.get("title") or key.get("funder"),
                           json.dumps(it["new"], sort_keys=True))
    return items


# ---------------------------------------------------------------- report

def summary(items):
    counts = {}
    for it in items:
        for k in it["kinds"]:
            counts[k] = counts.get(k, 0) + 1
    counts["FLAG"] = sum(1 for it in items if it["flags"])
    counts["preAccepted"] = sum(1 for it in items if it["preAccepted"])
    return counts


def print_report(items):
    print(f"cv_diff: {len(items)} items  {json.dumps(summary(items))}")
    for it in items:
        rec = it["new"] or it["old"]
        name = rec.get("title") or rec.get("text", "")[:60]
        print(f"- [{', '.join(it['kinds'])}]{' (pre-accepted)' if it['preAccepted'] else ''} "
              f"{rec.get('year') or rec.get('start') or ''} {str(name)[:80]}")
        for d in it["details"]:
            print(f"    {d}")
        for f in it["flags"]:
            print(f"    FLAG: {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--new-cv", required=True)
    ap.add_argument("--old-cv", help="compare against an older CV instead of the published data")
    ap.add_argument("--data", default=str(ROOT / "data"), help="published data directory")
    ap.add_argument("--json", help="write the items here")
    ap.add_argument("--year", type=int, help="'this year' for the missing-ID flag (default: today)")
    args = ap.parse_args()
    from datetime import date
    this_year = args.year or date.today().year

    new_pubs, new_grants = load_cv(args.new_cv)
    old_pubs, old_grants = load_cv(args.old_cv) if args.old_cv else load_published(args.data)
    items = diff(old_pubs, old_grants, new_pubs, new_grants, this_year)
    print_report(items)
    if args.json:
        Path(args.json).write_text(json.dumps({"summary": summary(items), "items": items}, indent=2,
                                              ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
