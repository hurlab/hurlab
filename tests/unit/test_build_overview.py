"""Tests for scripts/build_overview.py (the internal Research Overview page).

Run: python3 -m unittest discover -s tests/unit -v

The website data comes from the repo's data/ directory; overview_internal.json is private
(kept outside the repo), so each test writes a small stand-in to a temp directory. Nothing is
written to OneDrive.
"""

import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import build_overview as bo  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "data"
INTERNAL = {
    "pilotsNote": "Internal pilot awards funded early work.",
    "eras": [{"y": "2004 to 2006", "h": "Start", "w": "Where", "l": ["one"], "r": [2004, 2006]}],
    "ideas": [{"h": "Idea", "f": "A x B", "d": "Description"}],
}


def consts(page):
    """The eight injected constants, parsed back from the page."""
    names = "PUBS|THEMES|KEY|GRANTS|PILOTS|ERAS|TOOLS|IDEAS"  # the template has other const names
    return {m.group(1): json.loads(m.group(2).replace("<\\/", "</"))
            for m in re.finditer(rf"const ({names})=(.*?);\n", page + "\n")}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="overview-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.internal = self.tmp / "overview_internal.json"
        self.internal.write_text(json.dumps(INTERNAL))

    def render(self, data_dir=DATA, today=date(2026, 11, 1)):
        return bo.render(data_dir, self.internal, today=today)


class Helpers(unittest.TestCase):
    def test_first_author(self):
        self.assertEqual(bo.first_author("Huang F, Hur J$, Lee S."), "Huang F")
        self.assertEqual(bo.first_author("*Lee S*, Hur J$. Title."), "Lee S")
        self.assertEqual(bo.first_author("Bai JPF and Hur J. Systems Medicine."), "Bai JPF")
        self.assertEqual(bo.first_author("Rehana H and Hur J$. Schema-Grounded."), "Rehana H")
        # the template drops "et al." only for the full name
        self.assertEqual(bo.first_author("*Hur J$, Lee S. Title."), "Junguk Hur")

    def test_decimal_year(self):
        self.assertEqual(bo.decimal_year("2022-07"), 2022.5)
        self.assertEqual(bo.decimal_year("2027-06"), 2027.42)
        self.assertEqual(bo.decimal_year("2015-01"), 2015.0)

    def test_page_title(self):
        self.assertEqual(bo.page_title("A study of X."), "A study of X")
        self.assertEqual(bo.page_title("Why X?"), "Why X?")
        self.assertEqual(bo.page_title("Wait..."), "Wait...")

    def test_no_em_dash_is_recursive(self):
        self.assertEqual(bo.no_em_dash({"a": ["x — y", "p—q"]}), {"a": ["x, y", "p-q"]})

    def test_js_const_escapes_script_end(self):
        self.assertNotIn("</script>", bo.js_const("X", ["</script>"]))


class Render(Base):
    def test_all_constants_and_placeholders(self):
        page = self.render()
        c = consts(page)
        self.assertEqual(list(c), ["PUBS", "THEMES", "KEY", "GRANTS", "PILOTS", "ERAS", "TOOLS", "IDEAS"])
        self.assertNotRegex(page, r"\{\{[A-Z_]+\}\}")
        self.assertIn("22 years of computational biomedicine", page)  # 2026 - 2004
        self.assertNotIn("—", page)
        self.assertIn("for(let y=2004;y<=2026;y++)", page)  # chart years end at the build year
        self.assertIn("const now=2026.83;", page)           # 2026-11-01 on the grant timeline

    def test_chart_years_follow_the_build_year(self):
        page = self.render(today=date(2027, 3, 1))
        self.assertIn("for(let y=2004;y<=2027;y++)", page)
        self.assertIn("const now=2027.16;", page)
        self.assertIn("23 years of computational biomedicine", page)

    def test_field_mapping_matches_the_website_data(self):
        c = consts(self.render())
        pubs = json.loads((DATA / "publications.json").read_text())
        src = {p["number"]: p for p in pubs["peerReviewed"]}
        self.assertEqual(len(c["PUBS"]), len(src))
        for p in c["PUBS"]:
            s = src[p["id"]]
            self.assertEqual(p["cat"], s["category"])
            self.assertEqual(p["year"], s["year"])
            self.assertEqual(p["theme"], s["areaIndex"] + 1)
            self.assertEqual(p["r"], {"first": "F", "corresponding": "C"}.get(s["authorship"], ""))
            self.assertEqual(p["pmid"], s["pmid"] or "")
        self.assertEqual(c["THEMES"], {str(i + 1): a for i, a in enumerate(pubs["areas"])})
        self.assertTrue(all(isinstance(n, int) for ids in c["KEY"].values() for n in ids))

    def test_grants_internal_flag_and_order(self):
        c = consts(self.render())
        g = json.loads((DATA / "grants.json").read_text())
        allg = g["current"] + g["previous"]
        self.assertEqual(len(c["GRANTS"]), len(allg))
        self.assertEqual(sum(1 for x in c["GRANTS"] if x.get("i")),
                         sum(1 for x in allg if x["type"] == "internal"))
        self.assertTrue(all(x.get("i") is True for x in c["GRANTS"] if "i" in x))
        group = [0 if x["a"] else 2 if x.get("i") else 1 for x in c["GRANTS"]]
        self.assertEqual(group, sorted(group), "active, then completed external, then internal")

    def test_tools_use_url_then_github(self):
        c = consts(self.render())
        tools = json.loads((DATA / "tools.json").read_text())
        self.assertEqual(len(c["TOOLS"]), len(tools))
        for (name, _desc, url), t in zip(c["TOOLS"], tools):
            self.assertEqual(name, t["name"])
            self.assertEqual(url, t.get("url") or t.get("github") or "")

    def test_internal_content_is_injected_verbatim(self):
        c = consts(self.render())
        self.assertEqual(c["PILOTS"], INTERNAL["pilotsNote"])
        self.assertEqual(c["ERAS"], INTERNAL["eras"])
        self.assertEqual(c["IDEAS"], INTERNAL["ideas"])

    def test_em_dash_in_a_source_never_reaches_the_page(self):
        data = self.tmp / "data"
        shutil.copytree(DATA, data)
        doc = json.loads((data / "publications.json").read_text())
        doc["peerReviewed"][0]["title"] = "Left — right"
        (data / "publications.json").write_text(json.dumps(doc))
        page = self.render(data_dir=data)
        self.assertNotIn("—", page)
        self.assertIn("Left, right", page)

    def test_cv_date_ignores_the_build_date(self):
        # lastUpdated moves on every rebuild; it must not move the CV date
        no_log = self.tmp / "none.jsonl"
        self.assertEqual(bo.cv_date({"lastUpdated": "2026-11-01"}, {"source": "2026-10-30_X.docx"}, no_log),
                         "October 30, 2026")
        self.assertEqual(bo.cv_date({"lastUpdated": "2026-11-01"}, {}, no_log), "November 1, 2026")

    def test_cv_date_follows_a_live_publish_but_not_a_rolled_back_one(self):
        log = self.tmp / "applied.jsonl"
        log.write_text("\n".join(json.dumps(r) for r in [
            {"at": "2026-12-02T10:00:00", "run": "R1", "op": "update"},
            {"at": "2027-01-15T10:00:00", "run": "R2", "op": "update"},
            {"at": "2027-01-15T11:00:00", "op": "rollback", "rollbackOf": "R2"},
        ]) + "\n")
        self.assertEqual(bo.cv_date({}, {"source": "2026-10-30_X.docx"}, log), "December 2, 2026")


class Run(Base):
    def test_unmounted_output_is_a_quiet_skip(self):
        out = self.tmp / "no-such-onedrive" / "page.html"
        self.assertEqual(bo.run(out, self.internal), 0)
        self.assertFalse(out.exists())

    def test_writes_the_page(self):
        out = self.tmp / "page.html"
        self.assertEqual(bo.run(out, self.internal), 0)
        self.assertIn("const PUBS=", out.read_text(encoding="utf-8"))
        self.assertFalse(out.with_name("page.html.tmp").exists())

    def test_missing_internal_file_is_loud(self):
        with self.assertRaises(SystemExit):
            bo.run(self.tmp / "page.html", self.tmp / "missing.json")


if __name__ == "__main__":
    unittest.main()
