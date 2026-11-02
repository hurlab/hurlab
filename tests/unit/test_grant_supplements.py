"""An administrative supplement is its own grant row: it shares the parent's award core
(U24AI171008), so every matcher must still tell the two apart."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_overview  # noqa: E402
import cv_diff  # noqa: E402
import cv_publish  # noqa: E402
from cvlib import grant_ident, is_supplement  # noqa: E402

PARENT = {"funder": "NIH/NIAID U24 U24AI171008", "pis": "Tao, He, Hur", "role": "MPI",
          "title": "VIOLIN 2.0: Vaccine Information and Ontology LInked kNowledgebase",
          "start": "2022-07", "end": "2027-05", "type": "external", "status": "active",
          "agency": "NIH/NIAID U24"}
SUPP = dict(PARENT, funder="NIH/NIAID U24 3U24AI171008-05S1", start="2026-07",
            title="Administrative Supplement: " + PARENT["title"])


class GrantIdent(unittest.TestCase):
    def test_parent_and_supplement_differ(self):
        self.assertEqual(grant_ident(PARENT["funder"], PARENT["title"]), "U24AI171008")
        self.assertEqual(grant_ident(SUPP["funder"], SUPP["title"]), "U24AI171008-05S1")

    def test_is_supplement(self):
        self.assertTrue(is_supplement(SUPP))
        self.assertFalse(is_supplement(PARENT))


class DiffKeepsBoth(unittest.TestCase):
    def test_unchanged_pair_gives_no_items(self):
        self.assertEqual(cv_diff.diff_grants([PARENT, SUPP], [PARENT, SUPP]), [])

    def test_parent_change_is_seen_next_to_its_supplement(self):
        new = [dict(PARENT, end="2028-05"), SUPP]
        items = cv_diff.diff_grants([PARENT, SUPP], new)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["kinds"], ["GRANT-CHANGED"])
        self.assertEqual(items[0]["new"]["title"], PARENT["title"])

    def test_new_supplement_is_reported_as_new(self):
        items = cv_diff.diff_grants([PARENT], [PARENT, SUPP])
        self.assertEqual([i["kinds"] for i in items], [["GRANT-NEW"]])
        self.assertTrue(items[0]["new"]["title"].startswith("Administrative Supplement"))


class PublishFindsTheRightRow(unittest.TestCase):
    def test_supplement_key_finds_supplement(self):
        key = cv_publish._grant_key(SUPP)
        self.assertIs(cv_publish._find_grant_in([PARENT, SUPP], key), SUPP)

    def test_parent_key_finds_parent(self):
        key = cv_publish._grant_key(PARENT)
        self.assertIs(cv_publish._find_grant_in([SUPP, PARENT], key), PARENT)

    def test_cv_match_keeps_them_apart(self):
        self.assertIs(cv_publish._match_cv_grant([PARENT, SUPP], SUPP), SUPP)
        self.assertIs(cv_publish._match_cv_grant([SUPP, PARENT], PARENT), PARENT)


class OverviewMarksSupplement(unittest.TestCase):
    def test_supplement_flag(self):
        rows = build_overview.build_grants({"current": [PARENT, SUPP], "previous": []})
        flags = {r["t"]: r.get("x", False) for r in rows}
        self.assertTrue(flags[SUPP["title"]])
        self.assertFalse(flags[PARENT["title"]])


if __name__ == "__main__":
    unittest.main()
