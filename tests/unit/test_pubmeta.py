"""Tests for scripts/pubmeta.py (co-author lists, iCite figures) and build_data.parse_honors.

Run: python3 -m unittest discover -s tests/unit -v
No network: the PubMed and iCite fetchers are replaced in every test that could reach them.
"""

import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_data  # noqa: E402
import pubmeta as pm  # noqa: E402


def pub(number, text, cat="Article", pmid=""):
    return {"number": number, "text": text, "category": cat, "pmid": pmid}


class CvAuthors(unittest.TestCase):
    def test_marks_and_final_and(self):
        self.assertEqual(pm.cv_authors("Huang F*, Hu D*, Hur J$, and Guo K$. scGEN: a method. J. 2026."),
                         ["Huang F", "Hu D", "Hur J", "Guo K"])

    def test_two_authors(self):
        self.assertEqual(pm.cv_authors("Bai JPF and Hur J. Systems Medicine. 2020."), ["Bai JPF", "Hur J"])

    def test_edited_book(self):
        self.assertEqual(pm.cv_authors("He YO, Hur J, and Petrovsky N (Eds.). Vaccine Informatics. 2026."),
                         ["He YO", "Hur J", "Petrovsky N"])

    def test_et_al_is_dropped_and_spelling_fixed(self):
        self.assertEqual(pm.cv_authors("Ozgur A, Hur J, et al. Title here. 2015."), ["Özgür A", "Hur J"])


class Coauthors(unittest.TestCase):
    def test_variants_merge_but_known_distinct_people_do_not(self):
        pubs = [pub(1, ""), pub(2, ""), pub(3, ""), pub(4, "", cat="Preprint"), pub(5, "")]
        raw = {1: ["McGregor BA", "Hur J", "Lee S"], 2: ["McGregor B", "Hur J", "Lee SG"],
               3: ["McGregor BA", "Hur JU"], 4: ["Preprint Author", "Hur J"], 5: ["No Hur"]}
        co = pm.build_coauthors(pubs, raw)
        self.assertEqual(co, {"1": ["McGregor BA", "Lee S"], "2": ["McGregor BA", "Lee SG"], "3": ["McGregor BA"]})

    def test_pubmed_first_then_cv_and_offline_never_fetches(self):
        pubs = [pub(1, "Cv A, Hur J. T. J.", pmid="11"), pub(2, "Cv B, Hur J. T. J.", pmid="22")]
        with mock.patch.object(pm, "fetch_pubmed_authors", side_effect=AssertionError("no network")):
            raw = pm.author_lists(pubs, {"11": ["Pm A", "Hur J"]}, offline=True)
        self.assertEqual(raw, {1: ["Pm A", "Hur J"], 2: ["Cv B", "Hur J"]})

    def test_fetch_failure_falls_back_to_cv(self):
        pubs = [pub(1, "Cv A, Hur J. T. J.", pmid="11")]
        cache = {}
        with mock.patch.object(pm, "fetch_pubmed_authors", side_effect=OSError("down")):
            raw = pm.author_lists(pubs, cache)
        self.assertEqual((raw, cache), ({1: ["Cv A", "Hur J"]}, {}))


class Metrics(unittest.TestCase):
    PUBS = [pub(1, "", pmid="11"), pub(2, "", pmid="22")]
    FRESH = {"source": "NIH iCite", "retrieved": "2026-11-20",
             "by_pmid": {"11": {"c": 1, "rcr": 1.0, "pct": 50.0, "cpy": 0.5}, "22": {"c": 2, "rcr": None, "pct": None, "cpy": 1.0}}}

    def test_recent_and_complete_is_kept(self):
        with mock.patch.object(pm, "fetch_icite", side_effect=AssertionError("no network")):
            self.assertIs(pm.update_metrics(self.PUBS, self.FRESH, today=date(2026, 11, 22)), self.FRESH)

    def test_old_file_is_refreshed(self):
        new = {"11": {"c": 5, "rcr": 1.1, "pct": 55.0, "cpy": 1.0}, "22": {"c": 3, "rcr": None, "pct": None, "cpy": 1.0}}
        with mock.patch.object(pm, "fetch_icite", return_value=new):
            out = pm.update_metrics(self.PUBS, self.FRESH, today=date(2026, 12, 15))
        self.assertEqual(out, {"source": "NIH iCite", "retrieved": "2026-12-15", "by_pmid": new})

    def test_missing_pmid_or_failure(self):
        partial = dict(self.FRESH, by_pmid={"11": self.FRESH["by_pmid"]["11"]})
        with mock.patch.object(pm, "fetch_icite", side_effect=OSError("down")):
            self.assertIs(pm.update_metrics(self.PUBS, partial, today=date(2026, 11, 22)), partial)
        with mock.patch.object(pm, "fetch_icite", side_effect=AssertionError("no network")):
            self.assertIs(pm.update_metrics(self.PUBS, partial, offline=True, today=date(2026, 11, 22)), partial)


class UpdateOffline(unittest.TestCase):
    def test_repo_data_reproduces_itself_offline(self):
        root = Path(__file__).resolve().parents[2]
        tmp = Path(tempfile.mkdtemp(prefix="pubmeta-test-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        data = tmp / "data"
        data.mkdir()
        for name in ("publications.json", "coauthors.json", "metrics.json"):
            shutil.copy(root / "data" / name, data / name)
        cache = tmp / "pubmed_authors.json"
        shutil.copy(pm.CACHE, cache)
        with mock.patch.object(pm, "fetch_pubmed_authors", side_effect=AssertionError("no network")), \
             mock.patch.object(pm, "fetch_icite", side_effect=AssertionError("no network")):
            pm.update(data, cache, offline=True)
        for name in ("coauthors.json", "metrics.json"):
            self.assertEqual(json.loads((data / name).read_text()), json.loads((root / "data" / name).read_text()), name)


class Honors(unittest.TestCase):
    def test_cv_section(self):
        paras = [(t, None) for t in [
            "Honors and Awards",
            "2006-2007\tRackham Graduate Fellowship", "University of Michigan, Ann Arbor, Michigan",
            "2007-2009\tScholarship Program University of Michigan, Ann Arbor, Michigan",
            "2010\tRackham Spotlight", "University of Michigan, Ann Arbor, Michigan",
            "2011-2014\tJuvenile Diabetes Research Foundation", "Post-doctoral Fellowship Recipient",
            "Membership in professional organizations",
            "May. 2008 ~\tInternational Society for Computational Biology, member",
        ]]
        self.assertEqual(build_data.parse_honors(paras), [
            {"y": "2006 to 2007", "t": "Rackham Graduate Fellowship, University of Michigan"},
            {"y": "2007 to 2009", "t": "Scholarship Program, University of Michigan"},
            {"y": "2010", "t": "Rackham Spotlight, University of Michigan"},
            {"y": "2011 to 2014", "t": "Juvenile Diabetes Research Foundation Post-doctoral Fellowship"},
        ])


if __name__ == "__main__":
    unittest.main()
