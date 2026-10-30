"""
Reading the PI's CV (.docx): publications, grants and the citation details the site uses.

Shared by build_data.py (full rebuild from the tracker + CV) and cv_diff.py (incremental
comparison of a new CV against the published data). Python standard library plus python-docx.
"""

import re
from datetime import date

# CV grant subsections; None = never published (pending proposals)
GRANT_SECTIONS = {
    "Current - External": ("external", "active"),
    "Current - Internal": ("internal", "active"),
    "Completed - External": ("external", "completed"),
    "Completed - Internal": ("internal", "completed"),
    "Pending - External": None,
    "Pending - Internal": None,
}
GRANT_STOP = {"Academic Consultant role", "Paid Consulting Activity", "Computational Tools and Databases"}

# CV publication subsection (by prefix) -> the tracker's category names
SECTION_CATEGORY = [
    ("Original Papers", "Article"),
    ("Group Authorship", "Group authorship"),
    ("Reviews or Editorial", "Review"),
    ("Editorial", "Editorial"),
    ("Book Editing", "Book"),
    ("Book chapter", "Book chapter"),
    ("Conference Proceedings – Peer-reviewed", "Proceedings (peer-reviewed)"),
    ("Conference Proceedings – Not", "Proceedings (not peer-reviewed)"),
    ("Preprint", "Preprint"),
]

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _ignore(msg):
    pass


def no_em_dash(text):
    return text.replace(" — ", ", ").replace("—", "-") if text else text


def norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def ym(text):
    """'7/1/2022' | '10/2015' | 'Jan. 2015' | '2016' -> 'YYYY-MM' (or None)."""
    text = text.strip().rstrip(".")
    m = re.match(r"(\d{1,2})/(?:\d{1,2}/)?(\d{4})$", text)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    m = re.match(r"([A-Za-z]{3})[a-z]*\.?\s*(\d{4})$", text)
    if m and m.group(1).lower() in MONTHS:
        return f"{m.group(2)}-{MONTHS[m.group(1).lower()]:02d}"
    m = re.match(r"(\d{4})$", text)
    return f"{m.group(1)}-01" if m else None


def cv_paragraphs(path):
    """Yield (text, numbered) for every body paragraph, in document order."""
    import docx
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    doc = docx.Document(path)
    for el in doc.element.body.iterchildren():
        if el.tag.endswith("}p"):
            yield Paragraph(el, doc).text, el.find(".//" + qn("w:numPr")) is not None


# ---------------------------------------------------------------- publications

def parse_cv_publications(paras):
    """Numbered entries of the CV's Publications section, with their subsection heading.
    Manuscripts under review are skipped: they never reach the public site."""
    entries, section, started = [], None, False
    for text, numbered in paras:
        t = text.strip()
        if t == "Publications":
            started = True
            continue
        if not started or not t:
            continue
        if t == "Presentations":
            break
        if not numbered:
            section = t
            continue
        if section and section.startswith("Manuscripts currently"):
            continue
        entries.append({"section": section or "", "text": no_em_dash(t), "used": False,
                        "peerReviewed": "– Peer-reviewed" in (section or "") or "- Peer-reviewed" in (section or "")})
    return entries


def section_category(section):
    for prefix, category in SECTION_CATEGORY:
        if (section or "").startswith(prefix):
            return category
    return None


def authorship(text, category):
    """first | corresponding | coauthor from the CV marks (* equal contribution, $ corresponding).
    First = Hur J listed first, or Hur J* with every preceding author also starred.
    Corresponding = Hur J$ when not first. Left out (None): edited books, and records whose byline
    does not name Hur J (group authorship as a challenge participant)."""
    if category == "Book":
        return None
    m = re.search(r"Hur J([*$]*)(?=[\s,.;]|$)", text or "")
    if not m:
        return None
    before = [t.strip() for t in re.split(r",|\band\b", text[:m.start()]) if t.strip()]
    if not before or ("*" in m.group(1) and all("*" in t for t in before)):
        return "first"
    return "corresponding" if "$" in m.group(1) else "coauthor"


# An author token: surname (may hold spaces, hyphens, accents) + initials, then optional marks.
_AUTHOR_END = re.compile(r"[A-Z][A-Za-z.\-]{0,6}[*$]*\.\s+(?=[A-Za-z0-9\"'(\[])")  # titles can start lowercase ("miRNA ...")


def split_citation(text):
    """(authors, title, rest) of a CV citation. Heuristic: the author list ends at the first
    '. ' that follows an initials token; the title runs to the next sentence end."""
    text = (text or "").strip()
    m = _AUTHOR_END.search(text)
    if not m:
        return "", "", text
    authors = text[:m.end()].strip().rstrip(".")
    tail = text[m.end():]
    t = re.search(r"[.?!]\s+(?=[A-Z0-9])", tail)
    title = tail[:t.start() + 1].strip() if t else tail.strip()
    rest = tail[t.end():].strip() if t else ""
    return authors, title.rstrip("."), rest


def author_list(authors):
    """[(name without marks, marks)] in byline order; '…' and consortium notes are dropped."""
    out = []
    for tok in re.split(r",|;|\band\b", authors or ""):
        tok = tok.strip()
        if not tok or tok in ("…", "...") or len(tok) > 60:
            continue
        m = re.match(r"(.*?)([*$]*)$", tok)
        out.append((m.group(1).strip(), m.group(2)))
    return out


def cv_record(entry):
    """A CV publication entry in the shape the diff compares."""
    text = entry["text"]
    authors, title, rest = split_citation(text)
    names = author_list(authors)
    pmid = re.search(r"PMID:?\s*(\d{6,9})", text)
    doi = re.search(r"\b(10\.\d{4,9}/[^\s\]\[,;]+?)(?=[.,;\])]?(?:\s|$))", text)
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", rest or text)
    category = section_category(entry["section"])
    return {
        "text": text,
        "section": entry["section"],
        "category": category,
        "isPreprint": category == "Preprint",
        "peerReviewed": entry["peerReviewed"],
        "pmid": pmid.group(1) if pmid else None,
        "doi": doi.group(1).rstrip(".").lower() if doi else None,
        "year": int(years[0]) if years else None,
        "title": title,
        "authors": names,
        "firstAuthor": (names[0][0].split()[0] if names and names[0][0] else ""),
        "authorship": authorship(text, category),
    }


# ---------------------------------------------------------------- grants

def parse_grants(paras, note=_ignore, today=None, include_pending=False):
    """Grant records from the CV's Grant section. Pending proposals are skipped unless
    include_pending (the diff keeps a private fingerprint of them; they are never published)."""
    records, section, current, started = [], None, None, False
    for text, numbered in paras:
        t = text.strip()
        if t == "Grant":
            started = True
            continue
        if not started or not t:
            continue
        if t in GRANT_STOP:
            break
        if t in GRANT_SECTIONS:
            section, current = t, None
            continue
        if section is None or (GRANT_SECTIONS[section] is None and not include_pending):
            continue
        if numbered or current is None:
            current = {"section": section, "raw": t}
            records.append(current)
        else:
            current["raw"] += "\n" + t
    return [g for g in (parse_grant(r, note, today) for r in records) if g]


def parse_grant(rec, note=_ignore, today=None):
    today = today or date.today()
    raw = re.sub(r"\s+(Note|Title|Role):", r"\n\1:", rec["raw"])
    kind, status = GRANT_SECTIONS[rec["section"]] or ("pending", "pending")
    header = raw.split("\nRole:")[0].split("\n")[0]
    header = re.sub(r"\(submitted[^)]*\)", "", header)
    pis = re.search(r"\((?:MPIs?|PIs?):\s*([^)]*)\)", header)
    period = re.search(r"\((\d{1,2}/(?:\d{1,2}/)?\d{4})\s*-\s*(\d{1,2}/(?:\d{1,2}/)?\d{4})[^)]*\)", raw)
    role = re.search(r"Role:\s*([^\t\n]+?)\s*(?:\t|Total:|$)", raw, re.M)
    title = re.search(r"Title:\s*(.+)", raw)
    funder = re.sub(r"\([^)]*\)", "", header)
    funder = re.sub(r"\s+", " ", funder.replace("\t", " ")).strip(" ,")
    g = {
        "funder": no_em_dash(funder),
        "pis": no_em_dash(pis.group(1).strip()) if pis else "",
        "role": no_em_dash(role.group(1).strip()) if role else "",
        "title": no_em_dash(title.group(1).strip().rstrip(". ")) if title else "",
        "period": f"{period.group(1)}-{period.group(2)}" if period else "",
        "start": ym(period.group(1)) if period else None,
        "end": ym(period.group(2)) if period else None,
        "type": kind,
        "status": status,
        "note": "",
        "cvSection": rec["section"],  # for the diff only; build_data.py drops it before publishing
    }
    if status == "pending":
        return g
    if not (g["title"] and g["start"] and g["end"] and g["role"]):
        note(f"GRANT INCOMPLETE ({rec['section']}): {g['funder']!r} title={g['title']!r} "
             f"period={g['period']!r} role={g['role']!r}")
    if kind == "internal" and not g["funder"].startswith("UND"):
        g["type"] = "external"
        note(f"GRANT TYPE: CV lists {g['funder']!r} under {rec['section']}; the funder is not UND, "
             f"so it is counted as external")
    if g["end"]:
        by_date = "active" if g["end"] >= today.strftime("%Y-%m") else "completed"
        if by_date != status:
            note(f"GRANT STATUS: CV lists {g['title']!r} under {rec['section']} but its end date "
                 f"{g['end']} reads as {by_date}; kept the CV section")
    return g


def award_core(funder):
    """The stable part of an NIH-style award number (e.g. U24AI171008), or None."""
    m = re.search(r"[A-Z]\d{2}[A-Z]{2}\d{6}", funder or "")
    return m.group(0) if m else None


def merge_supplements(grants, note=_ignore):
    """Fold 'Administrative Supplement: <parent title>' entries into their parent award as a note."""
    out = []
    for g in grants:
        if g["title"].lower().startswith("administrative supplement"):
            core = award_core(g["funder"])
            parent = next((p for p in grants if p is not g and core and core in p["funder"]
                           and not p["title"].lower().startswith("administrative supplement")), None)
            if parent:
                years = f"{g['start'][:4]}-{g['end'][:4]}" if g["start"] and g["end"] else ""
                parent["note"] = f"Includes {years} administrative supplement".replace("  ", " ")
                note(f"MERGED supplement {g['funder']!r} into {parent['funder']!r}")
                continue
            note(f"SUPPLEMENT WITHOUT PARENT kept separate: {g['funder']!r}")
        out.append(g)
    return out
