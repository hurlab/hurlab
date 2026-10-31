"""Tests for scripts/cv_publish.py (CV incremental update step 2) and the build_data re-apply hook.

Run: python3 -m unittest discover -s tests/unit -v

The real-CV tests use the same frozen dated CVs as test_cv_diff.py (dollar amounts and pending
proposals keep those files outside the repo). State, data and WEB-INF go to temp dirs; PubMed,
Crossref and RePORTER are replaced by fakes, so no test touches the network or the real repo.

Acceptance criteria of scripts/CV_UPDATE_STEP2.md §14, each observed failing on a deliberately
wrong input before it counted (2026-10-31 session):
  1. ground truth  — fails when the base data is built from the WRONG CV (10-30 instead of 10-29),
                     because the review then reports 0 items and the publish applies nothing;
                     observed: publish exit 1 → test_publish_matches_ground_truth fails.
  2. rollback      — fails when the snapshot restore skips grants.json; observed by temporarily
                     removing that file from the restore set → sha mismatch.
  3. memory        — fails when decisions are keyed by run instead of item id (the second review
                     then shows "hold"); observed with a run-scoped decisions dict.
  4. idempotence   — fails when set_pub() also writes tracker-owned fields on an add-found record
                     (the number flips to the server's); observed once before the restriction.
  5. stale refusal — fails when the basis check compares mtimes instead of sha256 (a same-size
                     edit passes); observed with an mtime-based check.
  6. missing ID    — fails when _lookup_meta silently leaves journal None without the flag print;
                     observed by deleting the flag branch.
  7. hygiene       — fails when cvlib.no_em_dash is bypassed by feeding raw CV text; observed by
                     writing the record text without the no_em_dash pass.
"""

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_data  # noqa: E402
import cv_diff  # noqa: E402
import cv_publish  # noqa: E402
from cvlib import award_core, cv_record, norm  # noqa: E402

# Frozen copies of the dated CVs, kept outside the repo (same convention as test_cv_diff.py).
CV_DIR = os.environ.get("CV_FIXTURE_DIR", os.path.expanduser("~/.local/share/hurlab-cv-fixtures"))
CV = {tag: os.environ.get(f"CV_{tag.replace('-', '_')}", f"{CV_DIR}/{tag}_JungukHur-CV.docx")
      for tag in ("2026-10-15", "2026-10-21", "2026-10-29", "2026-10-30")}
FIX = ("2026-10-29", "2026-10-30")

AREAS = ["Cancer Bio", "Ontology", "AI", "Neuro", "HPI", "Pharm"]  # slots for TITLE_RULES indexes

INDEX_TEMPLATE = """<!doctype html><html><body>
<!-- BUILD:active-grants -->0<!-- /BUILD:active-grants -->
<!-- BUILD:publication-count -->0<!-- /BUILD:publication-count -->
<!-- BUILD:publication-breakdown --><!-- /BUILD:publication-breakdown -->
<!-- BUILD:tool-count -->0<!-- /BUILD:tool-count -->
<!-- BUILD:recent-publications --><!-- /BUILD:recent-publications -->
<!-- BUILD:funding --><!-- /BUILD:funding -->
</body></html>
"""


def fake_pubmed(meta):
    return lambda pmids: {pid: dict(meta) for pid in pmids}


def failing(*_a, **_k):
    raise OSError("network down (fake)")


class Base(unittest.TestCase):
    """Temp state/data/WEB-INF/index plus fakes for every network touchpoint."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cvpub-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.state = self.tmp / "state"
        self.data = self.tmp / "data"
        self.webinf = self.tmp / "WEB-INF" / "cv-updates" / "applied.jsonl"
        self.index = self.tmp / "index.html"
        self.data.mkdir()
        self._patch(cv_publish, "WEBINF_LOG", self.webinf)
        self._patch(cv_publish, "INDEX", self.index)
        self._patch(build_data, "INDEX", self.index)
        self._patch(build_data, "GRANT_LINKS", self.tmp / "grant_links.json")
        self._patch(build_data, "OVERRIDES", self.tmp / "area_overrides.json")
        self._patch(build_data, "report", [])
        self._patch(build_data, "reporter_records", lambda cores: {})
        self._patch(build_data, "pubmed_meta",
                    fake_pubmed({"date": "2026-05-01", "precision": "day", "journal": "J Fake"}))
        self._patch(build_data, "crossref_meta", lambda doi: ("2026-05-01", "day", "J Fake"))
        self.index.write_text(INDEX_TEMPLATE)

    def _patch(self, obj, name, value):
        old = getattr(obj, name)
        setattr(obj, name, value)
        self.addCleanup(setattr, obj, name, old)

    # ------------------------------------------------------------- helpers

    def build_base(self, tag="2026-10-29", dated=True):
        """Write data/*.json as if build_data.py had run on the given CV (no tracker)."""
        pubs, grants = cv_diff.load_cv(CV[tag])
        out = []
        for i, r in enumerate(pubs, 1):
            rec = {
                "number": i, "text": r["text"], "title": r["title"], "journal": "J Prev",
                "year": r["year"], "category": r["category"], "isPreprint": r["isPreprint"],
                "isPeerReviewed": r["peerReviewed"], "cvSection": r["section"],
                "authorship": r["authorship"], "pmid": r["pmid"], "pmcid": None, "doi": r["doi"],
                "links": {"pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/" if r["pmid"] else None,
                          "pmc": None, "doi": f"https://doi.org/{r['doi']}" if r["doi"] else None},
                "area": AREAS[0], "areaIndex": 0, "areaSource": "title", "areaDetail": "",
                "topicFolder": None,
            }
            if dated and r["pmid"]:
                rec["date"], rec["datePrecision"], rec["dateSource"] = f"{r['year']}-06-01", "month", "pubmed"
            out.append(rec)
        out.sort(key=build_data.pub_sort_key, reverse=True)
        cur, prev = [], []
        for g in grants:
            if g["status"] == "pending":
                continue
            g = {k: v for k, v in g.items() if k != "cvSection"}
            g["note"] = ""
            g["award"], g["agency"], _ = build_data.split_award(g["funder"])
            (cur if g["status"] == "active" else prev).append(g)
        cur.sort(key=lambda g: g["start"] or "", reverse=True)
        prev.sort(key=lambda g: g["end"] or "", reverse=True)
        (self.data / "publications.json").write_text(json.dumps(
            {"peerReviewed": out, "areas": AREAS, "lastUpdated": "2026-10-29",
             "source": f"{tag}_JungukHur-CV.docx"}, indent=2, ensure_ascii=False) + "\n")
        (self.data / "grants.json").write_text(json.dumps(
            {"current": cur, "previous": prev, "lastUpdated": "2026-10-29",
             "source": f"{tag}_JungukHur-CV.docx"}, indent=2, ensure_ascii=False) + "\n")
        (self.data / "overview.json").write_text(json.dumps(
            {"eras": [], "areas": AREAS, "lastUpdated": "2026-10-29"}, indent=2) + "\n")
        return out, cur, prev

    def cli(self, *argv):
        """Run cv_publish.main in-process so the fakes above apply; returns (exit code, stdout)."""
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out):
            try:
                code = cv_publish.main(["--state", str(self.state), "--data", str(self.data), *argv]) or 0
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 0
        return code, out.getvalue()

    def review(self, new_tag="2026-10-30"):
        code, out = self.cli("review", "--new-cv", CV[new_tag])
        self.assertEqual(code, 0, out)
        run_id = max((self.state / "runs").iterdir()).name
        doc = json.loads((self.state / "runs" / run_id / "items.json").read_text())
        return run_id, doc

    def accept_all(self, run_id, decision="accept", except_ids=()):
        doc = json.loads((self.state / "runs" / run_id / "items.json").read_text())
        ids = [it["id"] for it in doc["items"] if it["id"] not in except_ids]
        code, out = self.cli("decide", run_id, *ids, decision)
        self.assertEqual(code, 0, out)

    def sha(self, path):
        path = Path(path)
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

    def pubs(self):
        return json.loads((self.data / "publications.json").read_text())["peerReviewed"]

    def grants(self):
        doc = json.loads((self.data / "grants.json").read_text())
        return doc["current"] + doc["previous"]


# ---------------------------------------------------------------- review / decide (§5, §6)

@unittest.skipUnless(all(os.path.exists(CV[t]) for t in FIX), "CV files not reachable")
class ReviewAndDecide(Base):

    def setUp(self):
        super().setUp()
        self.build_base("2026-10-29")

    def test_review_writes_state_and_report(self):
        run_id, doc = self.review()
        self.assertTrue((self.state / "uploads" / f"{run_id}.docx").exists())
        # 11 items vs the published data: 9 authorship marks, the Nutr J author list and the
        # Rumora R01 title. The Khan internal->external move is NOT among them: the published
        # file already carries type external (the build normalizes it) and published grants
        # carry no cvSection, so nothing is visible to change (design §14 ground truth is CV-vs-CV).
        self.assertEqual(len(doc["items"]), 11, [i["kinds"] for i in doc["items"]])
        self.assertEqual(doc["basis"]["publications.json"], self.sha(self.data / "publications.json"))
        self.assertEqual(doc["basis"]["grants.json"], self.sha(self.data / "grants.json"))
        for it in doc["items"]:
            self.assertEqual(it["decision"], "accept" if it["preAccepted"] else "hold")
        self.assertTrue(all(it["id"] for it in doc["items"]))

    def test_decision_memory_across_runs(self):
        # acceptance 3: rejected stays rejected; a changed version gets a new id
        run1, doc = self.review()
        target = [it for it in doc["items"] if "AUTHORSHIP-MARK-CHANGED" in it["kinds"]][0]
        code, out = self.cli("decide", run1, target["id"], "reject")
        self.assertEqual(code, 0, out)
        stored = json.loads((self.state / "decisions.json").read_text())
        self.assertEqual(stored[target["id"]]["decision"], "reject")
        run2, doc2 = self.review()
        again = [it for it in doc2["items"] if it["id"] == target["id"]]
        self.assertEqual(len(again), 1)
        self.assertEqual(again[0]["decision"], "reject")
        self.accept_all(run2, except_ids={target["id"]})  # everything else; the rejection is remembered
        code, out = self.cli("publish", run2)
        self.assertEqual(code, 0, out)
        self.assertIn(target["old"]["text"], [p["text"] for p in self.pubs()])
        applied = [json.loads(line) for line in self.webinf.read_text().splitlines() if line.strip()]
        self.assertFalse(any(r["item"] == target["id"] for r in applied))
        variant = dict(target["new"], text=target["new"]["text"] + " Erratum notice added.")
        new_id = cv_diff.item_id(",".join(target["kinds"]), target["new"].get("pmid")
                                 or target["new"].get("doi") or target["new"]["title"],
                                 json.dumps(variant, sort_keys=True))
        self.assertNotEqual(new_id, target["id"])

    def test_decide_unknown_id_is_exit1_and_writes_nothing(self):
        run_id, _ = self.review()
        had_decisions = (self.state / "decisions.json").exists()
        code, out = self.cli("decide", run_id, "deadbeef0000", "accept")
        self.assertEqual(code, 1, out)
        self.assertIn("unknown", out)
        self.assertEqual(had_decisions, (self.state / "decisions.json").exists())

    def test_decide_bad_decision_word_is_exit1(self):
        run_id, _ = self.review()
        code, out = self.cli("decide", run_id, "accept-ish")
        self.assertEqual(code, 1, out)


# ---------------------------------------------------------------- publish / rollback (§7, §8)

@unittest.skipUnless(all(os.path.exists(CV[t]) for t in FIX), "CV files not reachable")
class PublishRollback(Base):

    def setUp(self):
        super().setUp()
        self.build_base("2026-10-29")
        self.run_id, self.doc = self.review("2026-10-30")

    def test_publish_matches_ground_truth(self):
        # acceptance 1: every accepted item lands; a re-diff against the new CV is empty
        self.accept_all(self.run_id)
        before = {p["number"]: json.dumps(p, sort_keys=True) for p in self.pubs()}
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        items = cv_diff.diff(*cv_diff.load_published(self.data), *cv_diff.load_cv(CV["2026-10-30"]),
                             this_year=2026)
        self.assertEqual(items, [], [i["kinds"] for i in items])
        after = {p["number"]: json.dumps(p, sort_keys=True) for p in self.pubs()}
        expected = {it["old"]["number"] for it in self.doc["items"]
                    if it.get("old") and "number" in it["old"]}
        self.assertEqual({n for n in before if before[n] != after.get(n)}, expected)
        # the Rumora R01 title really landed, and no pending proposal or dollar amount leaked
        rumora = [it for it in self.doc["items"] if "GRANT-CHANGED" in it["kinds"]][0]
        g = [x for x in self.grants() if award_core(x["funder"] or "")
             == award_core(rumora["old"]["funder"])]
        self.assertEqual(len(g), 1)
        self.assertEqual(g[0]["title"], rumora["new"]["title"])
        applied = [json.loads(line) for line in self.webinf.read_text().splitlines() if line.strip()]
        self.assertEqual(len(applied), len(self.doc["items"]))
        history = [json.loads(line) for line in
                   (self.state / "history.jsonl").read_text().splitlines() if line.strip()]
        self.assertEqual(history[0]["kind"], "publish")

    def test_rollback_restores_bytes(self):
        # acceptance 2: publish then rollback restores every data file byte-for-byte
        self.accept_all(self.run_id)
        targets = [self.data / "publications.json", self.data / "grants.json",
                   self.data / "overview.json", self.index]
        before = {t: self.sha(t) for t in targets}
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        self.assertNotEqual({t: self.sha(t) for t in targets}, before)
        code, out = self.cli("rollback")
        self.assertEqual(code, 0, out)
        self.assertEqual({t: self.sha(t) for t in targets}, before, "files must match pre-publish bytes")
        log_lines = [line for line in self.webinf.read_text().splitlines() if line.strip()]
        marker = json.loads(log_lines[-1])
        self.assertEqual(marker["op"], "rollback")
        self.assertEqual(marker["rollbackOf"], self.run_id)
        items = cv_diff.diff(*cv_diff.load_published(self.data), *cv_diff.load_cv(CV["2026-10-29"]),
                             this_year=2026)
        self.assertEqual(items, [], "after rollback the published data must match the old CV again")

    def test_publish_refuses_stale_run(self):
        # acceptance 5: data changed after the review -> exit 2, nothing written
        self.accept_all(self.run_id)
        path = self.data / "publications.json"
        doc = json.loads(path.read_text())
        doc["peerReviewed"][0]["title"] += " (edited elsewhere after review)"
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        index_before = self.sha(self.index)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 2, out)
        self.assertIn("changed since the review", out)
        self.assertEqual(self.sha(self.index), index_before)
        self.assertFalse(self.webinf.exists())

    def test_publish_without_accepts_is_exit1(self):
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 1, out)
        self.assertFalse(self.webinf.exists())

    def test_dry_run_writes_nothing(self):
        self.accept_all(self.run_id)
        targets = [self.data / "publications.json", self.data / "grants.json",
                   self.data / "overview.json", self.index]
        before = {t: self.sha(t) for t in targets}
        code, out = self.cli("publish", self.run_id, "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertIn("dry-run", out)
        self.assertEqual({t: self.sha(t) for t in targets}, before)
        self.assertFalse(self.webinf.exists())
        self.assertFalse((self.state / "snapshots").exists())

    def test_written_files_have_no_dollar_amount_em_dash_or_pending(self):
        # acceptance 7
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        files = [self.data / "publications.json", self.data / "grants.json",
                 self.data / "overview.json", self.index, self.webinf,
                 self.state / "history.jsonl"]
        for f in files:
            text = f.read_text()
            self.assertNotIn("—", text, f.name)
            self.assertIsNone(re.search(r"\$\s*\d", text), f.name)  # "$," is an author mark, not an amount
        grants_doc = json.loads((self.data / "grants.json").read_text())
        for g in grants_doc["current"] + grants_doc["previous"]:
            self.assertIn(g["status"], ("active", "completed"))
        self.assertNotIn("Pending", json.dumps(grants_doc))

    def test_publish_updates_derived_outputs(self):
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        overview = json.loads((self.data / "overview.json").read_text())
        self.assertTrue(overview["eras"], "overview.json must be rebuilt from the uploaded CV")
        self.assertNotEqual(overview["lastUpdated"], "2026-10-29", "lastUpdated must move to today")
        pubs = self.pubs()
        self.assertIn(f"<!-- BUILD:publication-count -->{len(pubs)}<!-- /BUILD:publication-count -->",
                      self.index.read_text())

    def test_new_record_and_missing_id_flag(self):
        # acceptance 6: journal/date from the fake PubMed; both fakes failing -> "missing ID"
        new_item = [it for it in self.doc["items"] if "NEW" in it["kinds"]]
        self.assertEqual(new_item, [], "pair 10-29 -> 10-30 has no NEW records (ground truth)")
        # unit path: a synthetic NEW record with a PMID gets journal/date from the fakes
        synthetic = cv_diff.diff([], [], [cv_record({
            "section": "Original Papers – Peer-reviewed", "text":
            "Kim A, and Hur J$. A brand new synthetic study of diabetic nerve. J Fake. 2026;1:1. [PMID: 49999999]",
            "peerReviewed": True})], [], 2026)
        self.assertEqual(len(synthetic), 1)
        rec = cv_publish._new_pub_record(synthetic[0], self.pubs(), AREAS)
        self.assertEqual(rec["journal"], "J Fake")
        self.assertEqual(rec["date"], "2026-05-01")
        self.assertEqual(rec["dateSource"], "pubmed")
        self.assertEqual(rec["number"], max(p["number"] for p in self.pubs()) + 1)
        self.assertEqual(rec["areaSource"], "title")
        self.assertEqual(rec["topicFolder"], None)
        self.assertEqual(rec["links"]["pubmed"], "https://pubmed.ncbi.nlm.nih.gov/49999999/")
        # both fakes failing -> no date, CV year kept, "missing ID" printed
        self._patch(build_data, "pubmed_meta", failing)
        self._patch(build_data, "crossref_meta", failing)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rec2 = cv_publish._new_pub_record(synthetic[0], self.pubs(), AREAS)
        self.assertIsNone(rec2.get("date"))
        self.assertIn("missing ID", out.getvalue())
        self.assertEqual(rec2["year"], synthetic[0]["new"]["year"])


# ---------------------------------------------------------------- re-apply hook (§10)

class Reapply(Base):

    def setUp(self):
        super().setUp()
        self.base, self.cur, self.prev = self.build_base("2026-10-29")

    def write_log(self, records):
        self.webinf.parent.mkdir(parents=True, exist_ok=True)
        self.webinf.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))

    def run_apply(self, pubs, grants):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            build_data.apply_cv_updates(pubs, grants, self.webinf)
        return out.getvalue()

    def test_idempotent_second_run_is_silent(self):
        # acceptance 4
        target = next(p for p in self.base if p["pmid"])
        add = dict(self.base[0], title="A re-applied brand new paper", pmid=None, doi=None,
                   number=999, text="Kim A, and Hur J. A re-applied brand new paper. J Fake. 2026.")
        gone = self.base[-1]
        self.write_log([
            {"at": "2026-10-31T00:00:00", "run": "R1", "item": "upd1", "kinds": ["CHANGED"],
             "key": {"pmid": target["pmid"]}, "target": "publications", "op": "update",
             "set": {"title": target["title"] + " (edited on the server)"}},
            {"at": "2026-10-31T00:00:01", "run": "R1", "item": "add1", "kinds": ["NEW"],
             "key": {"title": norm(add["title"])}, "target": "publications", "op": "add",
             "set": add},
            {"at": "2026-10-31T00:00:02", "run": "R1", "item": "rem1", "kinds": ["REMOVED"],
             "key": {"title": norm(gone["title"])}, "target": "publications", "op": "remove",
             "set": {}},
        ])
        pubs = [dict(p) for p in self.base]
        out1 = self.run_apply(pubs, self.cur)
        self.assertIn("RE-APPLIED", out1)
        self.assertIn("RE-ADDED (add to the tracker)", out1)
        self.assertIn("RE-REMOVED", out1)
        snapshot = json.dumps(pubs, sort_keys=True)
        out2 = self.run_apply(pubs, self.cur)
        self.assertEqual(json.dumps(pubs, sort_keys=True), snapshot, "second run must not change bytes")
        self.assertNotIn("RE-", out2, "second run must be silent")
        self.assertFalse(any(p["title"] == gone["title"] for p in pubs))
        self.assertTrue(any(p["title"] == add["title"] for p in pubs))

    def test_rollback_marker_cancels_its_publish(self):
        target = next(p for p in self.base if p["pmid"])
        self.write_log([
            {"at": "2026-10-31T00:00:00", "run": "R1", "item": "upd1", "kinds": ["CHANGED"],
             "key": {"pmid": target["pmid"]}, "target": "publications", "op": "update",
             "set": {"authorship": "coauthor"}},
            {"at": "2026-10-31T00:01:00", "op": "rollback", "rollbackOf": "R1"},
        ])
        pubs = [dict(p) for p in self.base]
        out = self.run_apply(pubs, self.cur)
        self.assertNotIn("RE-", out)
        self.assertEqual(json.dumps(pubs, sort_keys=True), json.dumps(self.base, sort_keys=True))

    def test_year_rule_survives_reapply(self):
        dated = next(p for p in self.base if p.get("date"))
        bare = next(p for p in self.base if not p.get("date"))
        self.write_log([
            {"at": "2026-10-31T00:00:00", "run": "R1", "item": "u1", "kinds": ["CHANGED"],
             "key": {"pmid": dated["pmid"]}, "target": "publications", "op": "update",
             "set": {"year": 2099}},
            {"at": "2026-10-31T00:00:01", "run": "R1", "item": "u2", "kinds": ["CHANGED"],
             "key": {"title": norm(bare["title"])}, "target": "publications", "op": "update",
             "set": {"year": 2099}},
        ])
        pubs = [dict(p) for p in self.base]
        out = self.run_apply(pubs, self.cur)
        after = {p["title"]: p["year"] for p in pubs}
        self.assertEqual(after[dated["title"]], dated["year"], "decision (a): dated record keeps its year")
        self.assertEqual(after[bare["title"]], 2099, "decision (a): bare record takes the CV year")
        self.assertEqual(out.count("RE-APPLIED"), 1)

    def test_grant_update_and_add(self):
        # a grant with an NIH award number: the award-core key must match it
        g = next(x for x in self.cur if award_core(x["funder"] or ""))
        new_grant = dict(g, funder="NIH R01 1R01XX999999A", title="A re-applied brand new grant",
                         pis="Hur J", role="PI", period="1/2026-12/2030", start="2026-01",
                         end="2030-12", type="external", status="active", note="",
                         award="1R01XX999999A", agency="NIH R01")
        self.write_log([
            {"at": "2026-10-31T00:00:00", "run": "R1", "item": "g1", "kinds": ["GRANT-CHANGED"],
             "key": {"award": award_core(g["funder"])}, "target": "grants",
             "op": "update", "set": {"role": g["role"] + " (edited on the server)"}},
            {"at": "2026-10-31T00:00:01", "run": "R1", "item": "g2", "kinds": ["GRANT-NEW"],
             "key": {"award": award_core(new_grant["funder"])}, "target": "grants",
             "op": "add", "set": new_grant},
        ])
        grants = [dict(x) for x in self.cur] + [dict(x) for x in self.prev]
        out = self.run_apply(self.base, grants)
        self.assertIn("RE-APPLIED", out)
        self.assertIn("RE-ADDED", out)
        updated = next(x for x in grants if award_core(x["funder"])
                       == award_core(g["funder"]))
        self.assertEqual(updated["role"], g["role"] + " (edited on the server)")
        self.assertTrue(any(x["title"] == "A re-applied brand new grant" for x in grants))
        snapshot = json.dumps(grants, sort_keys=True)
        out2 = self.run_apply(self.base, grants)
        self.assertEqual(json.dumps(grants, sort_keys=True), snapshot)
        self.assertNotIn("RE-", out2)

    def test_local_reapply_of_a_server_publish_is_silent(self):
        # the bridge case: publish on the server, then rebuild locally — everything already equal
        run_id, _ = self.review("2026-10-30")
        self.accept_all(run_id)
        code, out = self.cli("publish", run_id)
        self.assertEqual(code, 0, out)
        pubs = self.pubs()
        grants = self.grants()
        out2 = self.run_apply(pubs, grants)
        self.assertNotIn("RE-", out2, json.loads(self.webinf.read_text().splitlines()[-1]))


# ---------------------------------------------------------------- step 4: push to GitHub

class GitPushUnit(Base):
    """_git_push() in isolation: subprocess faked, no CV fixtures needed."""

    def _fake_run(self, calls, result_code=0, stderr="", timeout=False):
        import subprocess as subprocess_mod

        def run(argv, **kwargs):
            calls.append(list(argv))
            if timeout:
                raise subprocess_mod.TimeoutExpired(argv[0], kwargs.get("timeout", 60))
            return subprocess_mod.CompletedProcess(argv, result_code, "", stderr)

        return run

    def test_push_ok(self):
        calls = []
        with mock.patch("subprocess.run", self._fake_run(calls)):
            self.assertTrue(cv_publish._git_push())
        self.assertEqual(calls, [["git", "push", "origin", "main"]])

    def test_push_nonzero_returns_false_and_shows_stderr(self):
        calls = []
        fake = self._fake_run(calls, result_code=128, stderr="remote: permission denied")
        with mock.patch("subprocess.run", fake), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertFalse(cv_publish._git_push())
        self.assertIn("permission denied", out.getvalue())

    def test_push_timeout_returns_false(self):
        calls = []
        with mock.patch("subprocess.run", self._fake_run(calls, timeout=True)):
            self.assertFalse(cv_publish._git_push())

    def test_push_without_repo_is_false(self):
        fake_root = self.tmp / "not-a-repo"
        fake_root.mkdir()
        self._patch(cv_publish, "ROOT", fake_root)
        self.assertFalse(cv_publish._git_push())


@unittest.skipUnless(all(os.path.exists(CV[t]) for t in FIX), "CV files not reachable")
class PushHook(Base):
    """Step 4: publish and rollback push to GitHub; a failed push is non-fatal.

    Same fixtures as PublishRollback. Where the hook itself is under test, _git_commit is faked
    to True — the real one skips in unit tests (the written files live outside the repo) and its
    own behavior is covered by PublishRollback."""

    def setUp(self):
        super().setUp()
        self.build_base("2026-10-29")
        self.run_id, self.doc = self.review("2026-10-30")

    def test_publish_pushes_once(self):
        calls = []
        self._patch(cv_publish, "_git_commit", lambda *a: True)
        self._patch(cv_publish, "_git_push", lambda: calls.append(1) or True)
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        self.assertEqual(len(calls), 1)
        self.assertIn("committed, pushed", out)

    def test_publish_push_failure_is_non_fatal(self):
        self._patch(cv_publish, "_git_commit", lambda *a: True)
        self._patch(cv_publish, "_git_push", lambda: False)
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)  # the site data is already live — push failure must not fail
        self.assertIn("PUSH FAILED (GitHub behind)", out)
        self.assertIn("WARNING", out)
        items = cv_diff.diff(*cv_diff.load_published(self.data), *cv_diff.load_cv(CV["2026-10-30"]),
                             this_year=2026)
        self.assertEqual(items, [], "the accepted changes must still be applied")

    def test_skipped_commit_attempts_no_push(self):
        calls = []
        self._patch(cv_publish, "_git_push", lambda: calls.append(1) or True)
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)  # real _git_commit: skip (no repo path)
        self.assertEqual(code, 0, out)
        self.assertIn("git skipped", out)
        self.assertEqual(calls, [], "no repo — no push may be attempted")

    def test_rollback_pushes(self):
        calls = []
        self._patch(cv_publish, "_git_commit", lambda *a: True)
        self._patch(cv_publish, "_git_push", lambda: calls.append(1) or True)
        self.accept_all(self.run_id)
        code, out = self.cli("publish", self.run_id)
        self.assertEqual(code, 0, out)
        code, out = self.cli("rollback")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(calls), 2, "publish and rollback each push once")
        self.assertIn("rolled back, committed, pushed", out)


if __name__ == "__main__":
    unittest.main()
