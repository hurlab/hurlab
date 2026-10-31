#!/usr/bin/env python3
"""
CV incremental update, step 2: decision memory, publish, rollback, history.

Server-side companion to cv_diff.py (step 1). The PI uploads a CV on the server, reviews the
classified differences, accepts or rejects each one, publishes, and can undo. Review state lives
outside the web root (--state, default /home/hurlab/hurlab-admin-state). Every applied change is
logged to WEB-INF/cv-updates/applied.jsonl (served 403) so build_data.py re-applies it on a local
rebuild. Design and field-ownership rules: scripts/CV_UPDATE_STEP2.md (§12 decisions confirmed by
the user on 2026-10-31: keep date-derived years; new numbers = max + 1; removals only on explicit
accept; rebuild overview.json on publish; server git identity and "CV update: N changes" message).

Usage:
  python3 scripts/cv_publish.py review --new-cv CV.docx [--year N]
  python3 scripts/cv_publish.py decide <run-id> <item-id>... accept|reject|hold
  python3 scripts/cv_publish.py publish <run-id> [--dry-run]
  python3 scripts/cv_publish.py rollback [<snapshot-id>]
  python3 scripts/cv_publish.py history

Exit codes: 0 success; 1 user error (unknown id, nothing accepted); 2 refused for safety (stale
run: the published data changed since the review).
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import date, datetime
from pathlib import Path

import build_data
import cv_diff
from cvlib import award_core, cv_paragraphs, norm, parse_grants

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
WEBINF_LOG = ROOT / "WEB-INF" / "cv-updates" / "applied.jsonl"
DEFAULT_STATE = "/home/hurlab/hurlab-admin-state"

# §8 field ownership. Publish may write CV-owned fields; tracker/build-owned fields are only
# filled when a NEW record is created, never overwritten afterwards.
PUB_CV_OWNED = ("text", "title", "category", "isPreprint", "isPeerReviewed", "cvSection",
                "authorship", "pmid", "doi")
GRANT_CV_OWNED = ("funder", "pis", "role", "title", "period", "start", "end", "type", "status")


def _iso():
    return datetime.now().astimezone().isoformat()


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _fresh_id(parent):
    """A unique YYYYMMDD-HHMMSS id for a child of parent (waits out a same-second collision)."""
    while True:
        cid = datetime.now().strftime("%Y%m%d-%H%M%S")
        if not (Path(parent) / cid).exists():
            return cid
        time.sleep(1)


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _append_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            line = json.dumps(rec, ensure_ascii=False)
            if "—" in line:
                raise SystemExit(f"refusing to write {path.name}: contains an em dash")
            fh.write(line + "\n")


def _load_decisions(state):
    path = Path(state) / "decisions.json"
    return _load_json(path) if path.exists() else {}


def _effective_decision(item, decisions):
    if item.get("preAccepted"):
        return "accept"
    return decisions.get(item["id"], {}).get("decision", "hold")


# ---------------------------------------------------------------- keys and lookups

def _pub_key(rec):
    """The stable identity of a publication record for applied.jsonl (§6): PMID, then DOI, then
    normalized title — never the number (decision b: numbers may differ between server and tracker)."""
    if rec.get("pmid"):
        return {"pmid": rec["pmid"]}
    if rec.get("doi"):
        return {"doi": rec["doi"].lower()}
    return {"title": norm(rec.get("title") or "")}


def _grant_key(rec):
    core = award_core(rec.get("funder") or "")
    if core:
        return {"award": core}
    return {"title": norm(rec.get("title") or "")}


def _find_pub_by_number(pubs, number):
    if number is None:
        return None
    return next((p for p in pubs if p.get("number") == number), None)


def _find_grant_in(grants, key):
    """Match by award core (no renewal prefix / year suffix — same rule as build_data's re-apply),
    then normalized title."""
    if key.get("award"):
        for g in grants:
            if award_core(g.get("funder") or "") == key["award"]:
                return g
    for g in grants:
        if norm(g.get("title") or "") == key.get("title"):
            return g
    return None


def _match_cv_grant(cv_grants, item_new):
    core = award_core(item_new.get("funder") or "")
    for g in cv_grants:
        if core and core in (g.get("funder") or ""):
            return g
    for g in cv_grants:
        if norm(g.get("title") or "") == norm(item_new.get("title") or ""):
            return g
    return None


def _pubmed_link(pmid):
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None


def _doi_link(doi):
    return f"https://doi.org/{doi}" if doi else None


# ---------------------------------------------------------------- record builders (§8)

def _lookup_meta(item_new):
    """(date, precision, journal, source) for a NEW record: PubMed, then Crossref; every call has
    a timeout (30 s inside build_data). Returns Nones when neither answers."""
    if item_new.get("pmid"):
        try:
            meta = build_data.pubmed_meta([item_new["pmid"]]).get(item_new["pmid"])
            if meta and meta.get("date"):
                return meta["date"], meta["precision"], meta.get("journal"), "pubmed"
        except Exception:
            pass
    if item_new.get("doi"):
        try:
            doi_date, prec, journal = build_data.crossref_meta(item_new["doi"])
            if doi_date:
                return doi_date, prec, journal, "crossref"
        except Exception:
            pass
    return None, None, None, None


def _new_pub_record(item, pubs, area_titles):
    """A NEW (or PREPRINT-NOW-PUBLISHED) record per §8: number = max + 1 (decision b), CV-owned
    fields from the CV record, journal/date from PubMed/Crossref with the "missing ID" fallback,
    area from the title rules, topicFolder null, tracker/build-owned leftovers null."""
    n = item["new"]
    number = max([p["number"] for p in pubs if isinstance(p["number"], int)] or [0]) + 1
    rec = {
        "number": number,
        "text": n.get("text"),
        "title": n.get("title"),
        "journal": None,
        "year": n.get("year"),
        "category": n.get("category"),
        "isPreprint": n.get("isPreprint"),
        "isPeerReviewed": n.get("peerReviewed"),
        "cvSection": n.get("cvSection"),
        "authorship": n.get("authorship"),
        "pmid": n.get("pmid"),
        "pmcid": None,
        "doi": n.get("doi"),
        "links": {"pubmed": _pubmed_link(n.get("pmid")), "pmc": None, "doi": _doi_link(n.get("doi"))},
        "topicFolder": None,
    }
    area, source, detail = build_data.classify(n.get("title"), None)
    rec["area"], rec["areaIndex"], rec["areaSource"], rec["areaDetail"] = area_titles[area], area, source, detail
    pub_date, prec, journal, dsrc = _lookup_meta(n)
    if pub_date:
        rec["date"], rec["datePrecision"], rec["dateSource"] = pub_date, prec, dsrc
        if rec["year"] is not None and int(pub_date[:4]) != rec["year"]:
            rec["trackerYear"], rec["year"] = rec["year"], int(pub_date[:4])  # same rule as build_data
        elif rec["year"] is None:
            rec["year"] = int(pub_date[:4])
    if journal:
        rec["journal"] = journal
    if not pub_date:
        print(f"    FLAG: missing ID — neither PubMed nor Crossref answered for {str(n.get('title'))[:60]!r}")
        item.setdefault("flags", []).append("missing ID")
    return rec


def _new_grant_record(item, cv_grants, old_links):
    """A GRANT-NEW record: CV-owned fields (pis/period re-read from the uploaded CV, §11), then
    build-owned award/agency/url/linkLabel via build_data (split_award + add_grant_links)."""
    n = item["new"]
    g = {f: n.get(f) for f in GRANT_CV_OWNED}
    cvg = _match_cv_grant(cv_grants, n)
    g["pis"] = (cvg or {}).get("pis", "")
    g["period"] = (cvg or {}).get("period", "")
    g["note"] = ""
    build_data.add_grant_links([g], old_links)
    return g


def _apply_pub_set(rec, fields):
    """Write a `set` dict onto a publication record; dotted keys go into links{}."""
    for k, v in fields.items():
        if k.startswith("links."):
            rec.setdefault("links", {})[k.split(".", 1)[1]] = v
        else:
            rec[k] = v


def _apply_item(item, pubs, cur, prev, cv_grants, area_titles, old_links, run_id, records):
    """Apply one accepted item per the §7 kind table; append its applied.jsonl record."""
    kinds = item["kinds"]
    for f in item.get("flags") or []:
        print(f"    FLAG: {f}")
    pub_update = any(k in kinds for k in ("METADATA", "CHANGED", "AUTHORSHIP-MARK-CHANGED",
                                          "CATEGORY-MOVED", "SAME-PAPER?"))
    if pub_update:
        rec = _find_pub_by_number(pubs, (item.get("old") or {}).get("number"))
        if rec is None:
            print(f"    record for item {item['id']} not found (number "
                  f"{(item.get('old') or {}).get('number')}) — skipped")
            return
        n = item["new"]
        # §8: title only when the item says the title changed; year only without a date (decision a)
        fields = {}
        for f in PUB_CV_OWNED:
            if f == "title" and norm(item["old"]["title"]) == norm(n["title"]):
                continue
            fields[f] = n.get(f)
        fields["links.pubmed"] = _pubmed_link(n.get("pmid"))
        fields["links.doi"] = _doi_link(n.get("doi"))
        if not rec.get("date") and n.get("year") is not None:
            fields["year"] = n["year"]
        _apply_pub_set(rec, fields)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": _pub_key(item["old"]), "target": "publications",
                        "set": fields, "op": "update"})
        print(f"    applied {item['id']} [{', '.join(kinds)}] -> #{rec['number']}")
    elif "NEW" in kinds or "PREPRINT-NOW-PUBLISHED" in kinds:
        rec = _new_pub_record(item, pubs, area_titles)
        pubs.append(rec)
        pubs.sort(key=build_data.pub_sort_key, reverse=True)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": _pub_key(rec), "target": "publications",
                        "set": rec, "op": "add"})
        print(f"    applied {item['id']} [{', '.join(kinds)}] -> new #{rec['number']}")
    elif "REMOVED" in kinds:
        rec = _find_pub_by_number(pubs, item["old"].get("number"))
        if rec is not None:
            pubs.remove(rec)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": _pub_key(item["old"]), "target": "publications",
                        "set": {}, "op": "remove"})
        print(f"    applied {item['id']} [REMOVED] -> #{item['old'].get('number')} deleted")
    elif "GRANT-NEW" in kinds:
        g = _new_grant_record(item, cv_grants, old_links)
        (cur if g["status"] == "active" else prev).append(g)
        cur.sort(key=lambda x: x.get("start") or "", reverse=True)
        prev.sort(key=lambda x: x.get("end") or "", reverse=True)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": _grant_key(g), "target": "grants", "set": g, "op": "add"})
        print(f"    applied {item['id']} [GRANT-NEW] -> {g['funder']}")
    elif any(k in kinds for k in ("GRANT-STATUS-CHANGED", "GRANT-SECTION-MOVED", "GRANT-CHANGED")):
        key = _grant_key(item["old"])
        g = _find_grant_in(cur + prev, key)
        if g is None:
            print(f"    grant for item {item['id']} not found ({key}) — skipped")
            return
        fields = {f: item["new"].get(f) for f in GRANT_CV_OWNED}
        cvg = _match_cv_grant(cv_grants, item["new"])
        fields["pis"] = (cvg or {}).get("pis", g.get("pis", ""))
        fields["period"] = (cvg or {}).get("period", g.get("period", ""))
        g.update(fields)
        # award/agency follow the (possibly changed) funder; url/linkLabel stay (§8: build keeps old links)
        g["award"], g["agency"], _ = build_data.split_award(g["funder"])
        was_current = g in cur
        now_current = g.get("status") == "active"
        if was_current != now_current:
            (cur if was_current else prev).remove(g)
            (cur if now_current else prev).append(g)
            cur.sort(key=lambda x: x.get("start") or "", reverse=True)
            prev.sort(key=lambda x: x.get("end") or "", reverse=True)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": key, "target": "grants", "set": fields, "op": "update"})
        print(f"    applied {item['id']} [{', '.join(kinds)}] -> {g['funder']}")
    elif "GRANT-REMOVED" in kinds:
        key = _grant_key(item["old"])
        g = _find_grant_in(cur + prev, key)
        if g is not None:
            (cur if g in cur else prev).remove(g)
        records.append({"at": _iso(), "run": run_id, "item": item["id"], "kinds": kinds,
                        "key": key, "target": "grants", "set": {}, "op": "remove"})
        print(f"    applied {item['id']} [GRANT-REMOVED] -> {item['old'].get('funder')} deleted")


# ---------------------------------------------------------------- snapshot / git

def _make_snapshot(state, snapshot_id, run_id, targets):
    """Byte copies of every file publish is about to change, plus a sha256 manifest."""
    snap = Path(state) / "snapshots" / snapshot_id
    snap.mkdir(parents=True, exist_ok=True)
    files = {}
    for i, target in enumerate(targets):
        flat = f"{i:03d}"
        meta = {"path": str(target)}
        if Path(target).exists():
            shutil.copyfile(target, snap / flat)
            meta["sha256"] = _sha(target)
        else:
            meta["sha256"] = None  # absent before the publish (e.g. the first applied.jsonl)
        files[flat] = meta
    manifest = {"snapshot": snapshot_id, "run": run_id, "at": _iso(), "files": files}
    (snap / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return snap, manifest


def _git_commit(paths, message):
    """Commit the given paths on the server repo. Returns 'skip' (no repo / nothing inside the
    repo — tests), True (committed) or False (failed; the caller restores the snapshot)."""
    if not (ROOT / ".git").exists():
        return "skip"
    try:
        inside = [str(p) for p in map(Path, paths)
                  if p.resolve().is_relative_to(ROOT.resolve())]
    except (OSError, ValueError):
        return "skip"
    if not inside:
        return "skip"
    import subprocess
    add = subprocess.run(["git", "add", "--", *inside], cwd=ROOT, capture_output=True, text=True)
    if add.returncode != 0:
        print("    git add failed: " + add.stderr.strip()[:200])
        return False
    commit = subprocess.run(["git", "commit", "-m", message], cwd=ROOT, capture_output=True, text=True)
    if commit.returncode != 0:
        print("    git commit failed: " + commit.stderr.strip()[:200])
        return False
    return True


# ---------------------------------------------------------------- commands

def cmd_review(args, state, data_dir):
    data_dir = Path(data_dir)
    for name in ("publications.json", "grants.json"):
        if not (data_dir / name).exists():
            print(f"cv_publish: {data_dir / name} not found — nothing to compare against")
            return 1
    run_id = _fresh_id(state / "runs")
    new_pubs, new_grants = cv_diff.load_cv(args.new_cv)
    old_pubs, old_grants = cv_diff.load_published(data_dir)
    this_year = args.year or date.today().year
    items = cv_diff.diff(old_pubs, old_grants, new_pubs, new_grants, this_year)
    decisions = _load_decisions(state)
    for it in items:
        it["decision"] = decisions.get(it["id"], {}).get("decision") \
            or ("accept" if it["preAccepted"] else "hold")
    uploads = Path(state) / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    cv_name = f"{run_id}.docx"
    shutil.copyfile(args.new_cv, uploads / cv_name)
    run_dir = Path(state) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    doc = {
        "run": run_id,
        "at": _iso(),
        "cv": cv_name,
        "thisYear": this_year,
        "basis": {"publications.json": _sha(data_dir / "publications.json"),
                  "grants.json": _sha(data_dir / "grants.json")},
        "items": items,
    }
    (run_dir / "items.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"cv_publish: run {run_id} — {len(items)} items "
          f"(decisions remembered from earlier runs are already applied)")
    for it in items:
        rec = it["new"] or it["old"]
        name = rec.get("title") or rec.get("text", "")[:60] or rec.get("funder") or ""
        print(f"- {it['id']}  [{', '.join(it['kinds'])}]  decision={it['decision']}"
              f"{' (pre-accepted)' if it['preAccepted'] else ''}  "
              f"{rec.get('year') or rec.get('start') or ''} {str(name)[:80]}")
        for d in it["details"]:
            print(f"    {d}")
        for f in it["flags"]:
            print(f"    FLAG: {f}")
    return 0


def cmd_decide(args, state):
    state = Path(state)
    doc_path = state / "runs" / args.run / "items.json"
    if not doc_path.exists():
        print(f"cv_publish: unknown run {args.run}")
        return 1
    doc = _load_json(doc_path)
    known = {it["id"] for it in doc["items"]}
    unknown = [i for i in args.ids if i not in known]
    if unknown:
        print("cv_publish: unknown item id(s): " + ", ".join(unknown) + " — nothing written")
        return 1
    decisions_path = state / "decisions.json"
    decisions = _load_json(decisions_path) if decisions_path.exists() else {}
    at = _iso()
    for i in args.ids:
        decisions[i] = {"decision": args.decision, "at": at, "run": args.run}
        print(f"cv_publish: {i} -> {args.decision}")
    decisions_path.write_text(json.dumps(decisions, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


def cmd_publish(args, state, data_dir):
    state = Path(state)
    data_dir = Path(data_dir)
    doc_path = state / "runs" / args.run / "items.json"
    if not doc_path.exists():
        print(f"cv_publish: unknown run {args.run}")
        return 1
    doc = _load_json(doc_path)
    # §7 step 1: refuse when the published data moved since the review
    for name, want in doc["basis"].items():
        got = _sha(data_dir / name)
        if got != want:
            print(f"cv_publish: refusing — {name} changed since the review "
                  f"(reviewed {want[:8]}, now {got[:8]}). Run review again.")
            return 2
    decisions = _load_decisions(state)
    accepted = [it for it in doc["items"] if _effective_decision(it, decisions) == "accept"]
    if not accepted:
        print("cv_publish: nothing accepted — publish refused")
        return 1
    pubs_doc = _load_json(data_dir / "publications.json")
    grants_doc = _load_json(data_dir / "grants.json")
    pubs = pubs_doc["peerReviewed"]
    cur, prev = grants_doc["current"], grants_doc["previous"]
    paras = list(cv_paragraphs(state / "uploads" / doc["cv"]))
    cv_grants = parse_grants(paras, include_pending=False)
    area_titles = pubs_doc["areas"]
    old_links = {g.get("title", "").lower(): (g.get("url"), g.get("linkLabel", ""))
                 for g in cur + prev if g.get("url")}
    records = []
    for it in accepted:
        _apply_item(it, pubs, cur, prev, cv_grants, area_titles, old_links, doc["run"], records)
    if args.dry_run:
        print(f"cv_publish: dry-run — {len(records)} changes would be applied for run {doc['run']}; "
              f"nothing written, no snapshot taken")
        return 0
    # §9 derived outputs, then §7 steps 3-7
    pubs_doc["lastUpdated"] = date.today().isoformat()
    grants_doc["lastUpdated"] = date.today().isoformat()
    interests, education, positions = build_data.parse_profile(paras)
    overview = build_data.build_overview(interests, education, positions, pubs, area_titles)
    overrides = _load_json(data_dir / "area_overrides.json") if (data_dir / "area_overrides.json").exists() else {}
    overview["highlights"] = build_data.pick_highlights(pubs, area_titles, overrides)
    overview["lastUpdated"] = date.today().isoformat()
    snapshot_id = _fresh_id(state / "snapshots")
    targets = [data_dir / "publications.json", data_dir / "grants.json", data_dir / "overview.json",
               INDEX, WEBINF_LOG]
    snap, manifest = _make_snapshot(state, snapshot_id, doc["run"], targets)
    try:
        build_data.write_home_fallback(pubs, {"current": cur, "previous": prev})
        build_data.write_json(data_dir / "publications.json", pubs_doc)
        build_data.write_json(data_dir / "grants.json", grants_doc)
        build_data.write_json(data_dir / "overview.json", overview)
        _append_jsonl(WEBINF_LOG, records)
        _append_jsonl(state / "history.jsonl", [
            {"at": _iso(), "kind": "publish", "run": doc["run"], "snapshot": snapshot_id,
             "changes": len(records), "accepted": len(accepted)}])
    except Exception as exc:
        _restore_snapshot(snap, manifest, targets)
        print(f"cv_publish: writing failed ({exc.__class__.__name__}: {exc}); snapshot restored")
        return 1
    result = _git_commit(targets, f"CV update: {len(records)} changes (run {doc['run']})")
    if result is False:
        _restore_snapshot(snap, manifest, targets)
        print("cv_publish: git commit failed — snapshot restored")
        return 1
    print(f"cv_publish: published {len(records)} changes (run {doc['run']}, "
          f"snapshot {snapshot_id}{', committed' if result is True else ', git skipped'})")
    return 0


def _restore_snapshot(snap, manifest, targets):
    """Copy the snapshot bytes back over every data file. applied.jsonl is deliberately NOT
    restored: the rollback record must be appended to the log so build_data.py can cancel the
    publish's records (CV_UPDATE_STEP2.md §10)."""
    for i, target in enumerate(targets):
        if Path(target) == Path(WEBINF_LOG):
            continue
        flat = f"{i:03d}"
        if (Path(snap) / flat).exists():
            shutil.copyfile(Path(snap) / flat, target)


def cmd_rollback(args, state, data_dir):
    state = Path(state)
    snaps = sorted((state / "snapshots").iterdir()) if (state / "snapshots").exists() else []
    snaps = [s for s in snaps if (s / "manifest.json").exists()]
    if args.snapshot_id:
        snap = state / "snapshots" / args.snapshot_id
        if not (snap / "manifest.json").exists():
            print(f"cv_publish: unknown snapshot {args.snapshot_id}")
            return 1
    elif snaps:
        snap = snaps[-1]
    else:
        print("cv_publish: no snapshots to roll back to")
        return 1
    manifest = _load_json(snap / "manifest.json")
    data_dir = Path(data_dir)
    restored = [data_dir / "publications.json", data_dir / "grants.json",
                data_dir / "overview.json", INDEX]
    for target in restored:
        for flat, meta in manifest["files"].items():
            if meta["path"] == str(target) and (snap / flat).exists():
                shutil.copyfile(snap / flat, target)
    marker = {"at": _iso(), "op": "rollback", "rollbackOf": manifest["run"],
              "snapshot": manifest["snapshot"]}
    _append_jsonl(WEBINF_LOG, [marker])
    _append_jsonl(state / "history.jsonl", [{"at": _iso(), "kind": "rollback",
                                             "rollbackOf": manifest["run"],
                                             "snapshot": manifest["snapshot"]}])
    result = _git_commit(restored + [WEBINF_LOG],
                         f"CV rollback: run {manifest['run']} (snapshot {manifest['snapshot']})")
    print(f"cv_publish: restored {len(restored)} files from snapshot {manifest['snapshot']} "
          f"(run {manifest['run']} rolled back{', committed' if result is True else ''})")
    return 0


def cmd_history(args, state):
    path = Path(state) / "history.jsonl"
    if not path.exists():
        print("cv_publish: no history yet")
        return 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            print(f"{rec.get('at', '')[:19]}  {rec.get('kind'):8}  run {rec.get('run', '-'):15}  "
                  f"snapshot {rec.get('snapshot', '-'):15}  "
                  f"{rec.get('changes', rec.get('rollbackOf', ''))}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--state", default=os.environ.get("HURLAB_ADMIN_STATE", DEFAULT_STATE),
                    help="private state directory (default: $HURLAB_ADMIN_STATE or %s)" % DEFAULT_STATE)
    ap.add_argument("--data", default=str(ROOT / "data"), help="published data directory")
    sub = ap.add_subparsers(dest="command", required=True)
    rev = sub.add_parser("review", help="diff a new CV against the published data")
    rev.add_argument("--new-cv", required=True)
    rev.add_argument("--year", type=int, help="'this year' for the missing-ID flag (default: today)")
    dec = sub.add_parser("decide", help="record accept/reject/hold; the decision is the LAST argument")
    dec.add_argument("run")
    dec.add_argument("items", nargs="+", metavar="item-id|decision")
    pub = sub.add_parser("publish", help="apply the accepted items")
    pub.add_argument("run")
    pub.add_argument("--dry-run", action="store_true")
    rb = sub.add_parser("rollback", help="restore the latest (or named) snapshot")
    rb.add_argument("snapshot_id", nargs="?")
    sub.add_parser("history", help="list publishes and rollbacks")
    args = ap.parse_args(argv)

    state = Path(args.state)
    state.mkdir(parents=True, exist_ok=True)
    if args.command == "review":
        return cmd_review(args, state, args.data)
    if args.command == "decide":
        if args.items[-1] not in ("accept", "reject", "hold"):
            print("cv_publish: the decision must be accept, reject or hold")
            return 1
        args.ids, args.decision = args.items[:-1], args.items[-1]
        return cmd_decide(args, state)
    if args.command == "publish":
        return cmd_publish(args, state, args.data)
    if args.command == "rollback":
        return cmd_rollback(args, state, args.data)
    return cmd_history(args, state)


if __name__ == "__main__":
    sys.exit(main())
