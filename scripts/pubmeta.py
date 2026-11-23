#!/usr/bin/env python3
"""
Co-author lists and citation figures for the Research Overview pages (public and internal).

Writes two public files under data/:
  - coauthors.json  {record number: [co-author names]}, Dr. Hur left out. Author lists come from
                    PubMed for records with a PMID and from the CV text for the rest. Preprints and
                    the group-authorship paper are left out, so a study with a preprint and a journal
                    paper is counted once. Name variants of one person (same last name and first
                    initial) are merged, except for the surname/initial pairs in DISTINCT_PEOPLE.
  - metrics.json    {"source", "retrieved", "by_pmid": {pmid: {c, rcr, pct, cpy}}} from NIH iCite
                    (citations, Relative Citation Ratio, NIH percentile, citations per year).

Network use is cached and never fatal:
  - PubMed author lists are kept in scripts/cache/pubmed_authors.json (committed); only PMIDs
    missing from it are fetched. Offline, a missing PMID falls back to the CV author list.
  - iCite is refreshed when metrics.json is older than METRICS_MAX_AGE_DAYS or lacks a PMID.
    Offline, the previous metrics.json is kept.

Called by build_data.py. Usage on its own:
  python3 scripts/pubmeta.py              # update both files (uses the network when needed)
  python3 scripts/pubmeta.py --offline    # no network: cache and CV text only
  python3 scripts/pubmeta.py --refresh    # refetch iCite even if metrics.json is recent
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / "scripts" / "cache" / "pubmed_authors.json"
OUT_COAUTHORS = DATA / "coauthors.json"
OUT_METRICS = DATA / "metrics.json"

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&tool=hurlab-site&id="
ICITE = ("https://icite.od.nih.gov/api/pubs?fl=pmid,citation_count,citations_per_year,"
         "relative_citation_ratio,nih_percentile&pmids=")
TIMEOUT = 60
METRICS_MAX_AGE_DAYS = 7
SELF_NAMES = {"Hur J", "Hur JU", "Junguk Hur"}
NOT_IN_NETWORK = {"Preprint", "Group authorship"}
# Same last name and first initial but different people: never merged.
DISTINCT_PEOPLE = {("guo", "A"), ("huang", "H"), ("kim", "M"), ("kim", "Y"), ("lee", "K"), ("lee", "S"),
                   ("lin", "Y"), ("park", "S")}
SPELLING = {"Ozgur A": "Özgür A", "Ozgür A": "Özgür A"}  # CV spells the name without diacritics


def log(msg):
    print(f"pubmeta: {msg}")


def cv_authors(text):
    """Author list at the head of a CV citation: 'Huang F*, Hu D*, ..., Hur J$, and Guo K$. Title...'."""
    text = re.sub(r"\s*\((?:Eds?|eds?)\.\)", "", text or "")  # edited book: 'Petrovsky N (Eds.). Title'
    m = re.match(r"(.+?(?:\b[A-Z][A-Za-z'’-]*[*$†#]*|et al))\.\s", text)
    if not m:
        return []
    head = re.sub(r",?\s+and\s+", ", ", m.group(1))
    names = [re.sub(r"[*$†#]", "", a).strip() for a in head.split(",")]
    return [SPELLING.get(n, n) for n in names if n and n != "et al"]


def fetch_pubmed_authors(pmids):
    """{pmid: ['Last Initials', ...]} from PubMed efetch (collective names are skipped)."""
    out = {}
    for i in range(0, len(pmids), 150):
        batch = pmids[i:i + 150]
        xml = urllib.request.urlopen(EFETCH + ",".join(batch), timeout=TIMEOUT).read()
        for art in ET.fromstring(xml).iter("PubmedArticle"):
            pmid = art.findtext("MedlineCitation/PMID")
            names = []
            for a in art.iter("Author"):
                last, ini = a.findtext("LastName"), a.findtext("Initials") or ""
                if last:
                    names.append(f"{last} {ini}".strip())
            out[pmid] = names
        time.sleep(0.4)  # NCBI asks for at most 3 requests per second without an API key
    return out


def author_lists(pubs, cache, offline=False):
    """{record number: [authors]}; fills the PubMed cache for missing PMIDs unless offline."""
    want = sorted({p["pmid"] for p in pubs if p.get("pmid") and p["pmid"] not in cache})
    if want and not offline:
        try:
            got = fetch_pubmed_authors(want)
            cache.update(got)
            log(f"PubMed author lists fetched for {len(got)} of {len(want)} new PMIDs")
        except Exception as e:  # network or parse failure: keep going with the CV lists
            log(f"PubMed not reachable ({e.__class__.__name__}); using CV author lists for {len(want)} PMIDs")
    return {p["number"]: (cache.get(p.get("pmid") or "") or cv_authors(p["text"])) for p in pubs}


def name_key(name):
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    last, _, initials = plain.rpartition(" ")
    return (last or initials).lower().replace("-", ""), (initials[:1] if last else "")


def build_coauthors(pubs, raw):
    """{record number: [co-authors]} for the records Dr. Hur is on, variants merged (most used spelling)."""
    count = Counter(n for v in raw.values() for n in v)
    groups = defaultdict(list)
    for n in count:
        groups[name_key(n)].append(n)
    canon = {}
    for k, names in groups.items():
        if len(names) > 1 and k not in DISTINCT_PEOPLE:
            best = sorted(names, key=lambda n: (-count[n], -len(n)))[0]
            canon.update({n: best for n in names})
    out = {}
    for p in sorted(pubs, key=lambda p: p["number"]):
        names = raw.get(p["number"], [])
        if p["category"] in NOT_IN_NETWORK or not any(n in SELF_NAMES for n in names):
            continue
        out[str(p["number"])] = list(dict.fromkeys(canon.get(n, n) for n in names if n not in SELF_NAMES))
    return out


def fetch_icite(pmids):
    out = {}
    for i in range(0, len(pmids), 300):
        data = json.loads(urllib.request.urlopen(ICITE + ",".join(pmids[i:i + 300]), timeout=TIMEOUT).read())
        for r in data.get("data", []):
            rcr, pct = r.get("relative_citation_ratio"), r.get("nih_percentile")
            out[str(r["pmid"])] = {"c": r.get("citation_count") or 0,
                                   "rcr": round(rcr, 2) if rcr else None,
                                   "pct": round(pct, 1) if pct is not None else None,
                                   "cpy": round(r.get("citations_per_year") or 0, 1)}
        time.sleep(0.5)
    return out


def update_metrics(pubs, old, offline=False, refresh=False, today=None):
    """New metrics document, or the old one when it is recent and complete (or the fetch fails)."""
    today = today or date.today()
    pmids = sorted({p["pmid"] for p in pubs if p.get("pmid")})
    have = old.get("by_pmid", {})
    age = (today - date.fromisoformat(old["retrieved"])).days if old.get("retrieved") else None
    stale = refresh or age is None or age > METRICS_MAX_AGE_DAYS or any(p not in have for p in pmids)
    if not stale or offline:
        return old
    try:
        got = fetch_icite(pmids)
    except Exception as e:
        log(f"iCite not reachable ({e.__class__.__name__}); kept metrics from {old.get('retrieved', 'never')}")
        return old
    log(f"iCite figures for {len(got)} of {len(pmids)} PMIDs, {sum(v['c'] for v in got.values()):,} citations")
    return {"source": "NIH iCite", "retrieved": today.isoformat(), "by_pmid": got}


def write_if_changed(path, obj, compact=False):
    text = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact
            else json.dumps(obj, ensure_ascii=False, indent=1)) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return True
    return False


def update(data_dir=DATA, cache_path=CACHE, offline=False, refresh=False):
    data_dir, cache_path = Path(data_dir), Path(cache_path)
    pubs = json.loads((data_dir / "publications.json").read_text(encoding="utf-8"))["peerReviewed"]
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    raw = author_lists(pubs, cache, offline)
    write_if_changed(cache_path, dict(sorted(cache.items())), compact=True)
    co = build_coauthors(pubs, raw)
    changed = write_if_changed(data_dir / "coauthors.json", co, compact=True)
    metrics_path = data_dir / "metrics.json"
    old = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    changed |= write_if_changed(metrics_path, update_metrics(pubs, old, offline, refresh), compact=True)
    log(f"{len(co)} records in the co-author network, "
        f"{len({n for v in co.values() for n in v})} co-authors{'' if changed else ' (unchanged)'}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--offline", action="store_true", help="no network: cache and CV text only")
    ap.add_argument("--refresh", action="store_true", help="refetch iCite figures now")
    args = ap.parse_args(argv)
    return update(offline=args.offline, refresh=args.refresh)


if __name__ == "__main__":
    sys.exit(main())
