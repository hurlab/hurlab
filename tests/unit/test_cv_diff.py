"""Tests for scripts/cv_diff.py.

Run: python3 -m unittest discover -s tests/unit -v

The real-CV tests compare two dated CVs whose differences were established independently
(a plain difflib comparison of the entry lists, 2026-10-30). They are skipped where the CV files
are not reachable (e.g. on the web server). The paths can be overridden with environment
variables, which is also how a deliberately wrong pair is fed in to see the tests fail.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import cv_diff  # noqa: E402
from cvlib import cv_record  # noqa: E402

# Frozen copies of the dated CVs, kept outside the repo because they hold dollar amounts and pending
# proposals. Frozen because a dated CV file can be edited in place later (the 2026-10-30 file was,
# for the Rumora R01 title), which silently moves the ground truth.
CV_DIR = os.environ.get("CV_FIXTURE_DIR", os.path.expanduser("~/.local/share/hurlab-cv-fixtures"))
CV = {tag: os.environ.get(f"CV_{tag.replace('-', '_')}", f"{CV_DIR}/{tag}_JungukHur-CV.docx")
      for tag in ("2026-10-15", "2026-10-21", "2026-10-29", "2026-10-30")}


def run_pair(old_tag, new_tag):
    old = cv_diff.load_cv(CV[old_tag])
    new = cv_diff.load_cv(CV[new_tag])
    return cv_diff.diff(old[0], old[1], new[0], new[1], this_year=2026)


def by_kind(items, kind):
    return [it for it in items if kind in it["kinds"]]


def title(it):
    rec = it["new"] or it["old"]
    return (rec.get("title") or rec.get("text") or "").lower()


@unittest.skipUnless(all(os.path.exists(CV[t]) for t in ("2026-10-29", "2026-10-30")), "CV files not reachable")
class PairA_1029_to_1030(unittest.TestCase):
    """9 Hur J marks changed, Combs also Auerbach, Nutr J author list, Khan R01 internal -> external,
    and the Rumora R01 title (edited in the 10-30 file at 17:33 to match NIH RePORTER)."""

    @classmethod
    def setUpClass(cls):
        cls.items = run_pair("2026-10-29", "2026-10-30")

    def test_exactly_the_known_items(self):
        self.assertEqual(len(self.items), 12, [i["kinds"] for i in self.items])

    def test_rumora_title(self):
        changed = by_kind(self.items, "GRANT-CHANGED")
        self.assertEqual(len(changed), 1)
        self.assertIn("TNF-alpha", changed[0]["new"]["title"])

    def test_nine_authorship_marks(self):
        marks = by_kind(self.items, "AUTHORSHIP-MARK-CHANGED")
        expected = ["methylation", "tox21enricher-shiny", "adverse childhood", "nested named entity",
                    "adjuvant name extraction", "adjuvant name recognition", "ignet 2.0", "gbmpso", "chatgpt"]
        self.assertEqual(len(marks), 9)
        for word in expected:
            self.assertTrue(any(word in title(it) for it in marks), word)
        for it in marks:
            self.assertEqual(it["new"]["authorship"], "corresponding", title(it))

    def test_combs_also_auerbach(self):
        combs = [it for it in self.items if "tox21enricher-shiny" in title(it)][0]
        self.assertIn("Auerbach S: '*' -> '$'", " ".join(combs["details"]))

    def test_nutr_j_authors(self):
        changed = by_kind(self.items, "CHANGED")
        self.assertEqual(len(changed), 1)
        self.assertIn("metabolite", title(changed[0]))
        self.assertIn("Kim M, Lee S, Hur J, Shin D", " ".join(changed[0]["details"]))

    def test_khan_moved_external(self):
        moved = by_kind(self.items, "GRANT-SECTION-MOVED")
        self.assertEqual(len(moved), 1)
        self.assertIn("Completed - Internal -> Completed - External", moved[0]["details"][0])

    def test_nothing_new_or_removed(self):
        self.assertEqual(by_kind(self.items, "NEW") + by_kind(self.items, "REMOVED"), [])


@unittest.skipUnless(all(os.path.exists(CV[t]) for t in ("2026-10-15", "2026-10-21")), "CV files not reachable")
class PairB_1015_to_1021(unittest.TestCase):
    """Neuroglia retitle + move to Reviews; EBioMedicine to Group Authorship; Editorial in press ->
    published; new edited book; PMIDs added to two papers."""

    @classmethod
    def setUpClass(cls):
        cls.items = run_pair("2026-10-15", "2026-10-21")

    def test_exactly_the_known_items(self):
        self.assertEqual(len(self.items), 6, [i["kinds"] for i in self.items])

    def test_neuroglia(self):
        it = [i for i in self.items if "microglial calcium" in title(i)][0]
        self.assertEqual(it["kinds"], ["CATEGORY-MOVED", "CHANGED"])
        self.assertEqual(it["new"]["category"], "Review")
        self.assertTrue(it["new"]["title"].startswith("The Alteration"))

    def test_ebiomedicine(self):
        it = [i for i in self.items if (i["new"] or {}).get("pmid") == "39321500"][0]
        self.assertEqual(it["kinds"], ["CATEGORY-MOVED"])
        self.assertEqual(it["new"]["category"], "Group authorship")
        self.assertIn("Hur J not in the byline", it["flags"])

    def test_metadata_refreshes_are_pre_accepted(self):
        meta = by_kind(self.items, "METADATA")
        self.assertEqual(len(meta), 3)
        self.assertTrue(all(i["preAccepted"] for i in meta))
        self.assertTrue(any("editorial" in title(i) for i in meta))

    def test_new_book(self):
        new = by_kind(self.items, "NEW")
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0]["new"]["category"], "Book")


# ---------------------------------------------------------------- synthetic cases

def rec(text, section="Original Papers – Peer-reviewed (*: equal contribution, $: co-corresponding authorship)"):
    return cv_record({"section": section, "text": text, "peerReviewed": "Not" not in section})


PREPRINT = "Preprint (BioRxived) – Not peer-reviewed"


def grant(title, status, section, funder="NIH R01 1R01DK000001"):
    return {"funder": funder, "role": "MPI", "title": title, "start": "2026-07", "end": "2030-06",
            "type": "external", "status": status, "cvSection": section, "note": ""}


class Synthetic(unittest.TestCase):

    def test_possible_match_band_asks_same_paper(self):
        old = [rec("Kim A, and Hur J$. Network analysis of sciatic nerve transcriptomes in obese mice. J Test. 2025.")]
        new = [rec("Kim A, and Hur J$. Network analyses of the sciatic nerve transcriptome in diet-induced obese mice. J Test. 2025.")]
        items = cv_diff.diff(old, [], new, [], 2026)
        self.assertEqual(len(items), 1, items)
        self.assertEqual(items[0]["kinds"][0], "SAME-PAPER?")

    def test_unrelated_title_is_new_plus_removed(self):
        old = [rec("Kim A, and Hur J$. Network analysis of sciatic nerve transcriptomes. J Test. 2025.")]
        new = [rec("Kim A, and Hur J$. A completely different study of vaccine adverse events. J Test. 2025.")]
        kinds = sorted(k for it in cv_diff.diff(old, [], new, [], 2026) for k in it["kinds"])
        self.assertEqual(kinds, ["NEW", "REMOVED"])

    def test_preprint_now_published(self):
        old = [rec("Lee B, and Hur J$. Single-cell atlas of diabetic nerve. bioRxiv. 2025. doi: 10.1101/2025.01.01.000001", PREPRINT)]
        new = old + [rec("Lee B, and Hur J$. A single-cell atlas of the diabetic nerve. Nature Test. 2026;1:1. [PMID: 40000001]")]
        items = cv_diff.diff(old, [], new, [], 2026)
        self.assertEqual([i["kinds"] for i in items], [["PREPRINT-NOW-PUBLISHED"]])

    def test_pending_to_active_and_active_to_completed(self):
        old = [grant("Grant A", "pending", "Pending - External"),
               grant("Grant B", "active", "Current - External", funder="NIH R01 1R01DK000002")]
        new = [grant("Grant A", "active", "Current - External"),
               grant("Grant B", "completed", "Completed - External", funder="NIH R01 1R01DK000002")]
        items = cv_diff.diff([], old, [], new, 2026)
        changes = sorted(i["details"][0] for i in items if "GRANT-STATUS-CHANGED" in i["kinds"])
        self.assertEqual(changes, ["active -> completed", "pending -> active"])
        for it in items:
            self.assertNotIn("Total", str(it))

    def test_grant_title_change(self):
        # found by using the tool: the Rumora R01 title was edited in the CV and nothing was reported
        old = [grant("Lipids and inflammation in peripheral neuropathy", "active", "Current - External")]
        new = [grant("The impact of dietary fatty acids and TNF-alpha on neuropathy", "active", "Current - External")]
        items = cv_diff.diff([], old, [], new, 2026)
        self.assertEqual([i["kinds"] for i in items], [["GRANT-CHANGED"]])
        self.assertTrue(items[0]["details"][0].startswith("title "))

    def test_pending_never_reported_on_its_own(self):
        items = cv_diff.diff([], [], [], [grant("Proposal", "pending", "Pending - External")], 2026)
        self.assertEqual(items, [])

    def test_abstract_flag(self):
        new = [rec("Kim A, and Hur J. A poster abstract. Diabetes. 2025;74(Suppl 1):S112.")]
        items = cv_diff.diff([], [], new, [], 2026)
        self.assertIn("listed as peer-reviewed but looks like an abstract or supplement", items[0]["flags"])


if __name__ == "__main__":
    unittest.main()
