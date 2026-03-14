#!/usr/bin/python3.12
"""
parse_cv.py — Parse PI's CV PDF and update website JSON data files.

Usage:
    python3 parse_cv.py [path/to/cv.pdf]

Default PDF path: ../Personal/JungukHur-CV.pdf (relative to script location)

Outputs updated JSON files in ../data/:
    - publications.json
    - grants.json

Dependencies: pdftotext (system), Python 3 standard library only.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data"))
DEFAULT_CV = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "Personal", "JungukHur-CV.pdf"))
PDFTOTEXT = "/usr/bin/pdftotext"

TODAY = date.today().isoformat()

# ── Profile links (static) ──────────────────────────────────────────────────

PROFILES = {
    "pubmed": (
        "https://www.ncbi.nlm.nih.gov/pubmed?term="
        "%22Hur%2C%20Junguk%22[FAU]%20OR%20%22Hur%2C%20Jung%20Uk%22[FAU]"
        "%20OR%20(%22Hur%20J%22[AU]%20AND%20%22Lee%20KJ%22[AU]%20AND%20%22Yoo%20J%22[AU])"
        "%20OR%20(%22Hur%20J%22[AU]%20AND%20%22Feldman%20EL%22[AU])"
    ),
    "orcid": "https://orcid.org/0000-0002-0736-2149",
    "researchgate": "https://www.researchgate.net/profile/Junguk_Hur",
    "myncbi": "https://www.ncbi.nlm.nih.gov/myncbi/junguk.hur.1/bibliography/40307074/public/",
    "cv": "Personal/JungukHur-CV.pdf",
}

PATENT = {
    "title": "A System for Analyzing DNA-Chips Using Gene Ontology, and a Method Thereof",
    "year": 2002,
    "country": "Republic of Korea",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_text(pdf_path):
    """Run pdftotext and return the full text, cleaned of page headers/footers."""
    result = subprocess.run(
        [PDFTOTEXT, pdf_path, "-"],
        capture_output=True, text=True, check=True,
    )
    text = result.stdout
    # Remove page footers: standalone page numbers on their own line
    text = re.sub(r"\n\d{1,2}\n", "\n", text)
    # Remove page headers like "Junguk Hur, Ph.D.\nCurriculum Vitae"
    text = re.sub(r"\nJunguk Hur, Ph\.D\.\s*\nCurriculum Vitae\n", "\n", text)
    return text


def write_json_atomic(path, data):
    """Write JSON to a temp file and atomically rename."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)
    print(f"  Written: {path}")


def find_section(text, markers):
    """Return the index of the first occurrence of any marker, or -1."""
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            return idx
    return -1


def split_numbered_entries(section_text):
    """Split text into numbered entries.  Returns list of (number, raw_text).

    Only matches entry numbers 1-999.  Years like 2008 at the start of a
    continuation line are not treated as new entries.  The function validates
    sequential numbering: a candidate number must be either the next expected
    number (within tolerance) or a reset back to 1 (for subsections with
    their own numbering).
    """
    # Match lines that start with a 1-3 digit number followed by period + space
    pattern = re.compile(r"^(\d{1,3})\.\s", re.MULTILINE)
    raw_matches = list(pattern.finditer(section_text))

    # Filter: keep only matches that look like sequential entry numbers
    filtered = []
    expected = 1
    for m in raw_matches:
        num = int(m.group(1))
        # Accept if it's the expected next number (within tolerance of 2)
        if abs(num - expected) <= 2:
            filtered.append(m)
            expected = num + 1
        elif num == 1:
            # Allow reset to 1 (new subsection with its own numbering)
            filtered.append(m)
            expected = 2
        elif not filtered and num <= 3:
            # First match can be 1, 2, or 3
            filtered.append(m)
            expected = num + 1

    entries = []
    for i, m in enumerate(filtered):
        num = int(m.group(1))
        start = m.end()
        end = filtered[i + 1].start() if i + 1 < len(filtered) else len(section_text)
        raw = section_text[start:end].strip()
        # Join multi-line text: collapse newlines to spaces, clean up
        raw = re.sub(r"\s*\n\s*", " ", raw)
        raw = re.sub(r"\s{2,}", " ", raw).strip()
        entries.append((num, raw))
    return entries


def extract_pmid(text):
    """Extract PMID from text like [PMID: 12345678]."""
    m = re.search(r"\[PMID:\s*(\d+)\]", text)
    return m.group(1) if m else None


def extract_doi(text):
    """Extract DOI URL from text."""
    # Match doi: https://... or doi: 10.xxxx/...
    m = re.search(r"doi:\s*(https?://[^\s\]\)]+)", text, re.IGNORECASE)
    if m:
        return m.group(1).rstrip(".")
    m = re.search(r"https?://doi\.org/[^\s\]\)]+", text)
    if m:
        return m.group(0).rstrip(".")
    m = re.search(r"https?://dx\.doi\.org/[^\s\]\)]+", text)
    if m:
        return m.group(0).rstrip(".")
    return None


def extract_year(text):
    """Extract the most likely publication year (4-digit year near end)."""
    # Find all 4-digit years
    years = re.findall(r"\b((?:19|20)\d{2})\b", text)
    if not years:
        return None
    # Return the last year found (usually the publication year at the end)
    return int(years[-1])


def is_preprint(text):
    """Check if entry is a preprint."""
    return bool(re.search(r"\b(arXiv|bioRxiv|medRxiv)\b", text, re.IGNORECASE))


# ── Section boundary detection ───────────────────────────────────────────────

def get_section_boundaries(text):
    """Find start positions of major CV sections. Returns dict of section -> index."""
    sections = {}

    # Peer-reviewed publications
    idx = find_section(text, [
        "Original Papers \u2013 Peer-reviewed",
        "Original Papers – Peer-reviewed",
        "Original Papers - Peer-reviewed",
        "Original Papers",
    ])
    if idx != -1:
        # Move past the header line to the start of entries
        nl = text.find("\n", idx)
        sections["peerReviewed"] = nl + 1 if nl != -1 else idx

    # Under review
    idx = find_section(text, [
        "Manuscripts currently under peer review or in revision",
        "Manuscripts currently under peer review",
    ])
    if idx != -1:
        nl = text.find("\n", idx)
        sections["underReview"] = nl + 1 if nl != -1 else idx

    # In preparation
    idx = find_section(text, [
        "Manuscript in preparation",
        "Manuscripts in preparation",
    ])
    if idx != -1:
        nl = text.find("\n", idx)
        sections["inPreparation"] = nl + 1 if nl != -1 else idx

    # Talks
    idx = find_section(text, [
        "Invited or contributed talks (Oral)",
        "Invited or contributed talks",
    ])
    if idx != -1:
        nl = text.find("\n", idx)
        sections["talks"] = nl + 1 if nl != -1 else idx

    # Panel discussion (marks end of talks if before posters)
    idx = find_section(text, ["Panel discussion"])
    if idx != -1:
        sections["panelDiscussion"] = idx

    # Posters
    idx = find_section(text, [
        "Abstracts (Poster)",
    ])
    if idx != -1:
        nl = text.find("\n", idx)
        sections["posters"] = nl + 1 if nl != -1 else idx

    # Grants
    idx = find_section(text, ["Current - External"])
    if idx != -1:
        # Back up to find "Grant" header before it
        sections["grantsStart"] = idx

    return sections


def extract_section_text(text, sections, section_name, end_sections):
    """Extract text for a section, bounded by the next section in end_sections."""
    if section_name not in sections:
        return ""
    start = sections[section_name]
    end = len(text)
    for es in end_sections:
        if es in sections and sections[es] > start:
            end = min(end, sections[es])
    return text[start:end]


# ── Grant parsing ────────────────────────────────────────────────────────────

def parse_grants(text):
    """Parse the grants section of the CV into structured data."""
    # Find all grant subsections
    subsection_markers = [
        ("current_external", "Current - External"),
        ("current_internal", "Current - Internal"),
        ("pending_external", "Pending - External"),
        ("pending_internal", "Pending - Internal"),
        ("previous_external", "Previous \u2013 External"),
        ("previous_external", "Previous – External"),
        ("previous_external", "Previous - External"),
        ("previous_internal", "Previous - Internal"),
    ]

    # Find positions of each subsection
    positions = []
    seen_keys = set()
    for key, marker in subsection_markers:
        idx = text.find(marker)
        if idx != -1 and key not in seen_keys:
            positions.append((idx, key, marker))
            seen_keys.add(key)
        elif idx != -1 and key in seen_keys:
            # Update if this occurrence is earlier (shouldn't happen normally)
            pass

    positions.sort(key=lambda x: x[0])

    # Find the end of the grants section: look for next major section
    # Typically "Academic Consultant role" or "Teaching" or "Publications" etc.
    grants_end_markers = [
        "Academic Consultant role",
        "Teaching",
        "Publications",
        "Presentations",
    ]
    grants_end = len(text)
    for marker in grants_end_markers:
        idx = text.find(marker)
        if idx != -1:
            # Only use if it comes after the grants section start
            if positions and idx > positions[0][0]:
                grants_end = min(grants_end, idx)

    result = {"current": [], "pending": [], "previous": [], "lastUpdated": TODAY}

    for i, (pos, key, marker) in enumerate(positions):
        # Determine end of this subsection
        if i + 1 < len(positions):
            end = positions[i + 1][0]
        else:
            end = grants_end

        subsection_text = text[pos + len(marker):end].strip()

        # Determine output category
        if key.startswith("current"):
            category = "current"
        elif key.startswith("pending"):
            category = "pending"
        else:
            category = "previous"

        # Check for N/A or None
        first_line = subsection_text.strip().split("\n")[0].strip() if subsection_text.strip() else ""
        if first_line.lower() in ("n/a", "none", ""):
            continue

        # Check if this is an "In preparation" subsection within pending
        # Some pending grants have "In preparation" entries
        has_in_prep = False
        in_prep_idx = subsection_text.find("In preparation")
        if in_prep_idx != -1 and key.startswith("pending"):
            has_in_prep = True

        grants = parse_grant_entries(subsection_text, category)
        result[category].extend(grants)

    return result


def parse_grant_entries(section_text, category):
    """Parse individual grant entries from a subsection."""
    entries = split_numbered_entries(section_text)
    grants = []

    for num, raw in entries:
        grant = parse_single_grant(raw, num)
        if grant:
            grants.append(grant)

    return grants


def parse_single_grant(raw, num):
    """Parse a single grant entry text into structured data."""
    grant = {"number": num}

    # The raw text is already joined into one line
    text = raw

    # Extract grant identifier (first line usually has the funder info)
    # Pattern: NIH/NIAID U24 1U24AI171008 or similar, or just the org name
    # Try to extract the funder line — it's everything before the first parenthetical PI info
    funder_match = re.match(r"^(.+?)(?:\s*\((?:M?PIs?|PI|submitted|for submission)[:\s])", text, re.IGNORECASE)
    if funder_match:
        grant["funder"] = funder_match.group(1).strip()
    else:
        # Try simpler: everything before "Role:"
        fm = re.match(r"^(.+?)\s+Role:", text)
        if fm:
            grant["funder"] = fm.group(1).strip()
        else:
            grant["funder"] = ""

    # Extract PIs
    pi_match = re.search(r"\((?:M?PIs?|PI)[:\s]+([^)]+)\)", text, re.IGNORECASE)
    if pi_match:
        grant["pis"] = pi_match.group(1).strip()
    else:
        grant["pis"] = ""

    # Extract role
    role_match = re.search(r"Role:\s*([^\s].*?)(?:\s+Total:|\s*$)", text)
    if role_match:
        grant["role"] = role_match.group(1).strip()
    else:
        grant["role"] = ""

    # Extract total
    total_match = re.search(r"Total:\s*(\$[\d,]+(?:\s*\([^)]*\))?)", text)
    if total_match:
        grant["total"] = total_match.group(1).strip()
    else:
        grant["total"] = ""

    # Extract date period
    period_match = re.search(r"\((\d{1,2}/\d{1,4}\s*-\s*\d{1,2}/\d{4})\)", text)
    if not period_match:
        period_match = re.search(r"\((\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4})\)", text)
    if period_match:
        grant["period"] = period_match.group(1).strip()
    else:
        grant["period"] = ""

    # Extract title
    title_match = re.search(r"Title:\s*(.+?)(?:\s+Note:|\s*$)", text)
    if title_match:
        grant["title"] = title_match.group(1).strip()
    else:
        grant["title"] = ""

    # Extract note
    note_match = re.search(r"Note:\s*(.+?)$", text)
    if note_match:
        grant["note"] = note_match.group(1).strip()
    else:
        grant["note"] = ""

    # Extract submission info for pending grants
    sub_match = re.search(r"\((submitted\s+(?:in|on)\s+[^)]+)\)", text, re.IGNORECASE)
    if not sub_match:
        sub_match = re.search(r"\((for submission\s+(?:in|on)\s+[^)]+)\)", text, re.IGNORECASE)
    if sub_match:
        grant["submitted"] = sub_match.group(1).strip()

    return grant


# ── Publication parsing ──────────────────────────────────────────────────────

def parse_peer_reviewed(text, sections):
    """Parse peer-reviewed publications, including conference proceedings and preprints.

    The section between peerReviewed and underReview contains multiple subsections:
    - Original Papers (peer-reviewed)
    - Conference Proceedings - Peer-reviewed
    - Conference Proceedings - Not peer-reviewed
    - Preprint (BioRxived) - Not peer-reviewed
    Each subsection restarts its numbering at 1.
    """
    full_section = extract_section_text(
        text, sections, "peerReviewed",
        ["underReview", "inPreparation", "talks", "panelDiscussion", "posters"],
    )

    # Split the full section into subsections by their headers
    subsection_headers = [
        ("Reviews or Editorial", "review"),
        ("Editorial \u2013 Not peer-reviewed", "editorialNonPR"),
        ("Editorial – Not peer-reviewed", "editorialNonPR"),
        ("Editorial - Not peer-reviewed", "editorialNonPR"),
        ("Book Editing", "bookEditing"),
        ("Book chapter", "bookChapter"),
        ("Conference Proceedings \u2013 Peer-reviewed", "conferenceProceedings"),
        ("Conference Proceedings – Peer-reviewed", "conferenceProceedings"),
        ("Conference Proceedings - Peer-reviewed", "conferenceProceedings"),
        ("Conference Proceedings \u2013 Not peer-reviewed", "conferenceProceedingsNonPR"),
        ("Conference Proceedings – Not peer-reviewed", "conferenceProceedingsNonPR"),
        ("Conference Proceedings - Not peer-reviewed", "conferenceProceedingsNonPR"),
        ("Preprint (BioRxiv", "preprints"),
        ("Preprint (bioRxiv", "preprints"),
    ]

    # Find subsection boundaries
    sub_positions = []
    for header, label in subsection_headers:
        idx = full_section.find(header)
        if idx != -1:
            sub_positions.append((idx, label, header))

    sub_positions.sort(key=lambda x: x[0])

    # Parse the main "Original Papers" section (before first subsection header)
    main_end = sub_positions[0][0] if sub_positions else len(full_section)
    main_text = full_section[:main_end]

    all_pubs = []
    global_num = [0]  # use list for mutation in nested function

    def process_entries(section_text, category):
        entries = split_numbered_entries(section_text)
        for num, raw in entries:
            global_num[0] += 1
            pmid = extract_pmid(raw)
            doi = extract_doi(raw)
            year = extract_year(raw)
            preprint = is_preprint(raw)

            # Also mark preprints by category
            if category == "preprints":
                preprint = True

            # Clean display text
            display_text = raw
            display_text = re.sub(r"\s*\[PMID:\s*\d+\]", "", display_text)
            display_text = re.sub(r"\s*\[PMCID:\s*\w+\]", "", display_text)
            display_text = re.sub(r"\s*\[Full text\]", "", display_text)
            display_text = display_text.strip()

            all_pubs.append({
                "number": global_num[0],
                "text": display_text,
                "pmid": pmid,
                "doi": doi,
                "year": year,
                "isPreprint": preprint,
                "category": category,
            })

    # Process main original papers
    process_entries(main_text, "originalPaper")

    # Process each subsection
    for i, (pos, label, header) in enumerate(sub_positions):
        # Find end of header line
        header_end = full_section.find("\n", pos)
        if header_end == -1:
            header_end = pos + len(header)
        start = header_end + 1
        end = sub_positions[i + 1][0] if i + 1 < len(sub_positions) else len(full_section)
        sub_text = full_section[start:end]
        process_entries(sub_text, label)

    return all_pubs


def parse_under_review(text, sections):
    """Parse manuscripts under review."""
    section_text = extract_section_text(
        text, sections, "underReview",
        ["inPreparation", "talks", "panelDiscussion", "posters"],
    )
    entries = split_numbered_entries(section_text)
    pubs = []
    for num, raw in entries:
        year = extract_year(raw)

        # Try to extract status from parenthetical info
        status = "Under review"
        status_match = re.search(
            r"\((.*?(?:Under\s+(?:review|1st|2nd|3rd)\s*(?:Revision|Review)?|"
            r"Revision\s+(?:requested|on\s+going|submitted)|"
            r"Submitted|Rejected|In\s+preparation\s+for\s+resubmission|"
            r"In\s+Revision)[^)]*)\)",
            raw, re.IGNORECASE,
        )
        if status_match:
            status = status_match.group(1).strip()
            # Clean up: get just the status part
            # Find the status keyword
            s = re.search(
                r"(Under\s+(?:\d+\w*\s+)?(?:Revision|Review|review)|"
                r"Revision\s+(?:requested|on\s*going|submitted)[^;)]*|"
                r"In\s+Revision|"
                r"In\s+preparation\s+for\s+resubmission|"
                r"Rejected[^;)]*)",
                status, re.IGNORECASE,
            )
            if s:
                status = s.group(1).strip()

        # Clean display text
        display_text = raw.strip()

        pubs.append({
            "number": num,
            "text": display_text,
            "year": year,
            "status": status,
        })
    return pubs


def parse_in_preparation(text, sections):
    """Parse manuscripts in preparation."""
    section_text = extract_section_text(
        text, sections, "inPreparation",
        ["talks", "panelDiscussion", "posters"],
    )
    # The "inPreparation" section for publications starts after "Manuscript in preparation"
    # But we also need to handle the case where there's a "Presentations" header before talks
    # Trim at "Presentations" if it appears
    pres_idx = section_text.find("Presentations")
    if pres_idx != -1:
        section_text = section_text[:pres_idx]

    entries = split_numbered_entries(section_text)
    pubs = []
    for num, raw in entries:
        display_text = raw.strip()
        # Extract target journal if mentioned
        status = "In preparation"
        status_match = re.search(
            r"\((In\s+preparation[^)]*|In\s+Preparation[^)]*|being\s+revised[^)]*)\)",
            raw, re.IGNORECASE,
        )
        if status_match:
            status = status_match.group(1).strip()

        pubs.append({
            "number": num,
            "text": display_text,
            "status": status,
        })
    return pubs


def parse_talks(text, sections):
    """Parse invited/contributed talks."""
    end_sections = ["panelDiscussion", "posters"]
    section_text = extract_section_text(text, sections, "talks", end_sections)
    entries = split_numbered_entries(section_text)
    talks = []
    for num, raw in entries:
        display_text = raw.strip()

        # Extract type and scope from parenthetical at end
        talk_type = ""
        scope = ""
        type_match = re.search(
            r"\((Invited|Contributed)(?:\s+talk)?(?:;\s*(Local|Regional|National|International))?\s*\)\s*$",
            raw, re.IGNORECASE,
        )
        if type_match:
            talk_type = type_match.group(1).strip().capitalize()
            scope = type_match.group(2).strip().capitalize() if type_match.group(2) else ""
        else:
            # Try alternate pattern: (Invited; Local) or (Keynote) or similar
            type_match2 = re.search(
                r"\(([^)]*(?:Invited|Contributed|Keynote)[^)]*)\)\s*$",
                raw, re.IGNORECASE,
            )
            if type_match2:
                info = type_match2.group(1)
                if re.search(r"Invited", info, re.IGNORECASE):
                    talk_type = "Invited"
                elif re.search(r"Contributed", info, re.IGNORECASE):
                    talk_type = "Contributed"
                elif re.search(r"Keynote", info, re.IGNORECASE):
                    talk_type = "Keynote"
                scope_m = re.search(r"(Local|Regional|National|International)", info, re.IGNORECASE)
                if scope_m:
                    scope = scope_m.group(1).capitalize()

        talks.append({
            "number": num,
            "text": display_text,
            "type": talk_type,
            "scope": scope,
        })
    return talks


def parse_posters(text, sections):
    """Parse poster presentations."""
    section_text = extract_section_text(text, sections, "posters", [])
    # The posters section goes to the end of the text (or until a known section)
    # Trim at known end markers
    for end_marker in ["Service", "Patent", "References"]:
        idx = section_text.find(end_marker)
        if idx != -1:
            section_text = section_text[:idx]

    entries = split_numbered_entries(section_text)
    posters = []
    for num, raw in entries:
        display_text = raw.strip()
        posters.append({
            "number": num,
            "text": display_text,
        })
    return posters


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Determine PDF path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = DEFAULT_CV

    pdf_path = os.path.abspath(pdf_path)

    if not os.path.isfile(pdf_path):
        print(f"Error: CV PDF not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(PDFTOTEXT):
        print(f"Error: pdftotext not found at {PDFTOTEXT}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing CV: {pdf_path}")
    print(f"Output directory: {DATA_DIR}")
    print(f"Date: {TODAY}")
    print()

    # Step 1: Extract text
    print("Extracting text from PDF...")
    text = extract_text(pdf_path)
    print(f"  Extracted {len(text)} characters, {text.count(chr(10))} lines")

    # Step 2: Find section boundaries
    print("Detecting section boundaries...")
    sections = get_section_boundaries(text)
    for name, pos in sorted(sections.items(), key=lambda x: x[1]):
        # Show a snippet of text at that position
        snippet = text[pos:pos + 60].replace("\n", " ").strip()
        print(f"  {name}: pos {pos} -> \"{snippet}...\"")
    print()

    # Step 3: Parse publications
    print("Parsing peer-reviewed publications...")
    peer_reviewed = parse_peer_reviewed(text, sections)
    print(f"  Found {len(peer_reviewed)} peer-reviewed publications")

    print("Parsing preprints...")
    preprint_count = sum(1 for p in peer_reviewed if p["isPreprint"])
    print(f"  Found {preprint_count} preprints among peer-reviewed entries")

    print("Parsing manuscripts under review...")
    under_review = parse_under_review(text, sections)
    print(f"  Found {len(under_review)} manuscripts under review")

    print("Parsing manuscripts in preparation...")
    in_preparation = parse_in_preparation(text, sections)
    print(f"  Found {len(in_preparation)} manuscripts in preparation")

    print("Parsing talks...")
    talks = parse_talks(text, sections)
    print(f"  Found {len(talks)} talks")

    print("Parsing posters...")
    posters = parse_posters(text, sections)
    print(f"  Found {len(posters)} posters")
    print()

    # Step 4: Build publications.json
    publications = {
        "profiles": PROFILES,
        "peerReviewed": peer_reviewed,
        "underReview": under_review,
        "inPreparation": in_preparation,
        "talks": talks,
        "posters": posters,
        "patent": PATENT,
        "lastUpdated": TODAY,
    }

    print("Writing publications.json...")
    os.makedirs(DATA_DIR, exist_ok=True)
    write_json_atomic(os.path.join(DATA_DIR, "publications.json"), publications)

    # Step 5: Parse and write grants
    print("Parsing grants...")
    grants = parse_grants(text)
    print(f"  Found {len(grants['current'])} current, "
          f"{len(grants['pending'])} pending, "
          f"{len(grants['previous'])} previous grants")

    print("Writing grants.json...")
    write_json_atomic(os.path.join(DATA_DIR, "grants.json"), grants)

    print()
    print("Done!")
    print(f"  Publications: {len(peer_reviewed)} peer-reviewed, "
          f"{len(under_review)} under review, "
          f"{len(in_preparation)} in preparation")
    print(f"  Talks: {len(talks)}, Posters: {len(posters)}")
    print(f"  Grants: {len(grants['current'])} current, "
          f"{len(grants['pending'])} pending, "
          f"{len(grants['previous'])} previous")


def git_auto_commit():
    """Auto-commit data/ changes if inside a git repo."""
    repo_dir = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
    git_dir = os.path.join(repo_dir, ".git")
    if not os.path.isdir(git_dir):
        return
    try:
        subprocess.run(
            ["git", "add", "data/publications.json", "data/grants.json"],
            cwd=repo_dir, capture_output=True, timeout=10
        )
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_dir, capture_output=True, timeout=10
        )
        if result.returncode != 0:  # there are staged changes
            subprocess.run(
                ["git", "commit", "-m", f"Auto-update publications and grants from CV ({TODAY})"],
                cwd=repo_dir, capture_output=True, timeout=10
            )
            print(f"  Git: auto-committed data changes ({TODAY})")
        else:
            print("  Git: no changes to commit")
    except Exception as e:
        print(f"  Git: auto-commit skipped ({e})")


if __name__ == "__main__":
    main()
    git_auto_commit()
