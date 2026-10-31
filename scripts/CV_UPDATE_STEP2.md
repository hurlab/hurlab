# CV incremental update — Step 2: decision memory, publish, rollback

Status: **plan approved by the user on 2026-10-30 (Kickoff given); no code written yet.**
Written 2026-10-30 20:50 CDT (session 184288b1) for the session that implements it.
This file lives under `scripts/` on purpose: the repository is also the public web root and
`scripts/*` is served 403 (WEB-INF/web.xml), while a root-level `.md` would be downloadable.

How to use this file: read it fully, confirm §12 Open decisions with the user (they change the
data model), then implement in the §13 order, tests first.

---

## 1. Why this exists

The public publication and grant lists (`data/publications.json`, `data/grants.json`) are built by
`scripts/build_data.py` from two sources that exist only on the PI's PC: the Excel publication
tracker and the CV `.docx` (paths under `/mnt/c/...`). On the server, a CV upload in the admin
panel updates talks and posters only (`scripts/parse_cv.py`, then `build_data.py --if-available`,
which is a no-op there). So today every CV change to papers or grants needs a local rebuild plus a
deploy.

Goal of the whole feature: the PI uploads a new CV `.docx` on the server, sees what changed,
accepts or rejects each change, publishes, and can undo, without a local rebuild.

## 2. The four steps

| Step | What | Status |
|---|---|---|
| 1 | Diff engine `scripts/cv_diff.py` + `scripts/cvlib.py`: classify every difference between a new CV and the published data (read-only). 19 unit tests | Done, deployed (commit 53b3aba, live in be67bcb) |
| **2** | **This file.** `scripts/cv_publish.py`: decision memory, publish (patch the JSON), snapshots, rollback, history; `build_data.py` re-applies published changes | Plan approved, not started |
| 3 | Admin panel "CV Update" tab driving step 2 (mock-up: `/home/juhur/.moai/worktrees/projects/hurlab/research-overview/.preview/cv-review-mockup.html`, untracked; copy it out before that worktree is disposed) | Not started |
| 4 | After each publish the server pushes to GitHub with a repo-scoped deploy key; the local deploy refuses when origin has commits not pulled locally | Not started (the server-side `~/deploy.sh` already stops when the server has commits GitHub lacks) |

## 3. Scope of step 2

In scope:
- `scripts/cv_publish.py`, a command-line tool with five subcommands (§5)
- private state directory outside the web root (§6)
- accepted-change log in the repository: `WEB-INF/cv-updates/applied.jsonl` (§6)
- patching `data/publications.json` and `data/grants.json` with accepted items only (§7, §8)
- refreshing the outputs derived from them (§9)
- a re-apply hook in `scripts/build_data.py` so a local rebuild keeps server-published changes (§10)
- `tests/unit/test_cv_publish.py` (§14)

Out of scope (do NOT build now): any web UI (step 3), any `git push` or deploy key (step 4), the
tracker Excel file (never written by the server), talks/posters (still `parse_cv.py`).

## 4. Decisions already made (do not re-litigate)

| Decision | Who / when |
|---|---|
| Review state, decisions, snapshots, change history live OUTSIDE the web root: `/home/hurlab/hurlab-admin-state/` | user + relayed agent, 2026-10-30 |
| The diff input is the CV `.docx`; the PDF upload only feeds the public "Download CV" link | same |
| Metadata lookups: PubMed E-utilities, Crossref as DOI fallback; if both are unreachable, flag "missing ID" (both reachable from the server, measured 2026-10-30) | same |
| "Same paper?" band: title similarity 0.75-0.90, year +/- 1, same first-author surname (already in step 1) | same |
| Publish PATCHES the JSON on the server (the tracker is local-only) and logs every accepted change in `WEB-INF/cv-updates/applied.jsonl`; `build_data.py` re-applies that log on a local rebuild | user, 2026-10-30 (chose "patch + rebuild honors log") |
| The log lives under `WEB-INF/` because `WEB-INF/` answers 403 live (measured: `WEB-INF/web.xml` 403 on 127.0.0.1:8081 and publicly) while `data/` is public | measured 2026-10-30 |
| Publish makes a local `git commit` on the server; no push in step 2 | plan, approved 2026-10-30 |
| Acceptance tests use real CV pairs; ground truth was measured independently of cv_diff (§14) | 2026-10-30 |
| Deploys are done by Claude over ssh with `~/deploy.sh`; no sudo | user, 2026-10-30 |

## 5. Command-line interface

`python3 scripts/cv_publish.py [--state DIR] [--data DIR] <command> ...`
- `--state` default: env `HURLAB_ADMIN_STATE`, else `/home/hurlab/hurlab-admin-state`
- `--data` default: `<repo>/data` (tests point both at temp dirs)

| Command | Does | Writes |
|---|---|---|
| `review --new-cv CV.docx [--year N]` | Runs `cv_diff.load_cv` + `cv_diff.load_published` + `cv_diff.diff`; copies the CV into the state dir; applies remembered decisions (§6 decisions); prints the report with each item's id and current decision | `runs/<run-id>/items.json`, `uploads/<run-id>.docx` |
| `decide <run-id> <item-id>... accept\|reject\|hold` | Records decisions; unknown ids are an error (exit non-zero, nothing written) | `decisions.json` |
| `publish <run-id> [--dry-run]` | §7: snapshot, patch accepted items, refresh derived outputs, append the log, `git commit` | snapshot dir, `data/*.json`, `index.html`, `WEB-INF/cv-updates/applied.jsonl`, `history.jsonl` |
| `rollback [<snapshot-id>]` | Restores the snapshot (default: the latest) byte-for-byte, appends a rollback record to the log, commits | same files |
| `history` | Lists publishes and rollbacks | nothing |

Exit codes: 0 success; 1 user error (unknown id, nothing accepted); 2 refused for safety (dirty
tracked `data/` files that this tool did not write, stale run: published data changed since the
review). Every message plain English; never print dollar amounts or pending proposals (the CV holds
them; cv_diff already keeps pending grants out of items).

## 6. State and file layout

```
/home/hurlab/hurlab-admin-state/          (private, NOT in git, NOT in the web root)
  uploads/<run-id>.docx                   the uploaded CV (holds $ amounts: never copy into the repo)
  runs/<run-id>/items.json                cv_diff output + "basis" (sha256 of publications.json and grants.json at review time)
  decisions.json                          {item-id: {"decision": "accept|reject|hold", "at": ISO time, "run": run-id}}
  snapshots/<snapshot-id>/                byte copies of every file publish will touch + manifest.json (sha256 per file)
  history.jsonl                           one line per publish / rollback (private detail: run, counts, snapshot)

<repo>/WEB-INF/cv-updates/applied.jsonl   (in git, served 403) one line per APPLIED change, enough to re-apply it
```

- `run-id` and `snapshot-id`: `YYYYMMDD-HHMMSS` (local time), unique.
- Decision memory works because item ids are content hashes (`cv_diff.item_id` over kinds + key +
  `json.dumps(new)`): the same change in the next CV has the same id, so a rejected change stays
  rejected; a different change gets a new id and is asked again.
- `applied.jsonl` record (one JSON object per line):
  `{"at": ISO, "run": run-id, "item": item-id, "kinds": [...], "key": {"pmid"|"doi"|"title"|"award": ...}, "target": "publications|grants", "set": {field: value, ...}, "op": "update|add|remove"}`
  `key` identifies the record without depending on its number; `set` holds only CV-owned fields (§8).

## 7. Publish algorithm

1. Load `runs/<run-id>/items.json`; refuse (exit 2) if the current sha256 of `data/publications.json`
   or `data/grants.json` differs from the run's `basis` (someone published or rebuilt since review).
2. Take the accepted items; if none, exit 1.
3. Snapshot every file about to change (`data/publications.json`, `data/grants.json`,
   `data/overview.json`, `index.html`, `WEB-INF/cv-updates/applied.jsonl`) into `snapshots/<id>/`.
4. Apply each accepted item per the table below; collect `applied.jsonl` records.
5. Refresh derived outputs (§9); set `lastUpdated` to today.
6. Write JSON with `build_data.write_json` (it refuses em dashes); append `applied.jsonl` and `history.jsonl`.
7. `git add` the changed paths by explicit pathspec and `git commit -m "CV update: N changes (run <run-id>)"`.
   If the commit fails, restore the snapshot and exit non-zero.
`--dry-run` stops after step 4 and prints what would change.

Per item kind (kinds come from `cv_diff`; an item can carry several, apply all of them):

| Kind | On accept |
|---|---|
| `METADATA` (pre-accepted by step 1) | update CV-owned fields (§8) of the matched record |
| `CHANGED`, `AUTHORSHIP-MARK-CHANGED`, `CATEGORY-MOVED` | update CV-owned fields of the matched record (`old.number`) |
| `NEW` | add a record (§8 "New records") |
| `PREPRINT-NOW-PUBLISHED` | add the published version as a new record; the preprint stays |
| `SAME-PAPER?` | accept = it is the same paper: update the old record; reject = nothing (the user handles it by hand) |
| `REMOVED` | step 1 marks removals "never applied automatically": only an explicit accept removes the record (open decision §12-c) |
| `GRANT-NEW` | add to `current` or `previous` by status (§8 "Grants") |
| `GRANT-STATUS-CHANGED`, `GRANT-SECTION-MOVED`, `GRANT-CHANGED` | update the grant's CV-owned fields; move between `current`/`previous` when the status changes |
| `GRANT-REMOVED` | same rule as `REMOVED` |
| any item with `flags` | publishable, but `review` must show the flags and `publish` prints them again |

## 8. Field ownership

Publications (`data/publications.json` → `peerReviewed[]`; keys in use today: `area, areaDetail,
areaIndex, areaSource, authorship, category, cvSection, date, datePrecision, dateSource, doi,
isPeerReviewed, isPreprint, journal, links, number, pmcid, pmid, text, title, topicFolder, year`,
optional `trackerYear`):

| Owner | Fields | Rule |
|---|---|---|
| CV (publish may overwrite) | `text`, `title`, `category`, `isPreprint`, `isPeerReviewed`, `cvSection`, `authorship`, `pmid`, `doi` | from the CV record (`cvlib.cv_record`); `authorship` via `cvlib.authorship(text, category)`; `title` only when the item says the title changed |
| Derived (recompute) | `links.pubmed`, `links.doi`, `year` (see §12-a) | links from pmid/doi as `build_data.build_publications` does |
| Tracker / build (never overwrite) | `number`, `journal`, `pmcid`, `links.pmc`, `area`, `areaIndex`, `areaSource`, `areaDetail`, `topicFolder`, `date`, `datePrecision`, `dateSource`, `trackerYear` | only filled for NEW records |

New records: `number` per §12-b; `journal` and `date` from PubMed (`build_data.pubmed_dates` has
the date logic; the esummary result also carries `fulljournalname`/`source`) then Crossref
(`build_data.crossref_date`; `container-title` for the journal), every call with a timeout; if
neither answers, keep the record and add flag "missing ID"; `area` via
`build_data.classify(title, None)` (title rules; `areaSource` "title" or "default"); `topicFolder`
null.

Grants (`data/grants.json` → `current[]`, `previous[]`; keys: `funder, pis, role, title, period,
start, end, type, status, note, award, agency, url, linkLabel`): CV-owned = `funder, pis, role,
title, period, start, end, type, status`; build-owned = `award, agency` (`build_data.split_award`),
`url, linkLabel` (RePORTER lookup `build_data.add_grant_links`, keeps old links), `note`.

## 9. Derived outputs a publish must refresh

Found by reading the code on 2026-10-30; the approved plan did not list them:
- `index.html` static no-JavaScript copies between `<!-- BUILD:... -->` markers (publication count,
  active-grant count, 5 recent papers, funding list): call `build_data.write_home_fallback(pubs, grants)`.
- `data/overview.json` (`researchInterests, eras, milestones, areas, highlights`): era publication
  counts and highlights depend on the publication list. The uploaded CV is available, so
  `build_data.parse_profile(paras)` + `build_overview(...)` + `pick_highlights(...)` can rebuild it
  on the server (open decision §12-d).
- `research-overview.html` and `publications.html` read the JSON at page load, so they follow
  automatically.

## 10. Re-apply hook in `build_data.py`

After `build_publications` + `add_pub_dates` and the grant build, before writing:
read `WEB-INF/cv-updates/applied.jsonl` in order and for each record find the target by `key`
(PMID, then DOI, then normalized title; grants by award core, then title):
- record found and all `set` fields already equal → skip silently (the tracker caught up)
- record found, fields differ → apply `set`, print `RE-APPLIED`
- `op: add` and no record found → add it, print `RE-ADDED (add to the tracker)`
- `op: remove` → drop it, print `RE-REMOVED`
Idempotent: running the build twice gives byte-identical output. A rollback record cancels the
records of its publish.

## 11. Implementation notes found in the code

- `cv_diff.label()` keeps only `number, year, category, pmid, doi, title, text, authorship`; publish
  also needs the CV section and the peer-reviewed flag. Either extend `label()` (this changes every
  item id, harmless while no decisions are stored; run the 19 step-1 tests afterwards) or re-read
  the run's uploaded CV and rebuild the record with `cvlib.cv_record`.
- The grant items' `new` holds only `funder, role, title, start, end, type, status`; `pis` and
  `period` must come from the CV again (`cvlib.parse_grants(..., include_pending=False)`).
- Published records carry `number` (`load_published` copies it into the comparison record), so
  `old.number` locates the record to update.
- `import build_data` is side-effect free (work happens in `main()`), so its helpers can be reused;
  do not copy them.
- The CV `.docx` and the fixtures hold dollar amounts and pending proposals: keep them out of the
  repository and out of `applied.jsonl`.

## 12. Open decisions — confirm with the user BEFORE coding

| # | Question | Default if the user agrees |
|---|---|---|
| a | `year`: the plan called it CV-owned, but the published `year` is the publication-date year (build_data replaces the tracker year when a date exists, keeping `trackerYear`). Overwrite it from the CV? | Do not overwrite `year` when the record has a `date`; update it only for records without a date |
| b | `number` for a new paper: numbers come from the tracker | next integer above the current maximum; re-apply matches by PMID/DOI/title, never by number |
| c | `REMOVED` / `GRANT-REMOVED`: allow removal on explicit accept? | yes, explicit accept only; never pre-accepted |
| d | Rebuild `overview.json` on the server from the uploaded CV during publish? | yes (§9) |
| e | Commit identity and message on the server | the server's existing git identity; `CV update: N changes (run <run-id>)` |

**Confirmed by the user on 2026-10-31 (session 1e6e3188): all five defaults accepted as written** —
(a) keep the date-derived year, (b) new number = max + 1, (c) removal only on explicit accept,
(d) rebuild `overview.json` during publish, (e) server git identity with
`CV update: N changes (run <run-id>)`. Implemented accordingly in this branch.

## 13. Implementation order (tests first)

1. Tests for the state layout and `review` / `decide` (decision memory), then the code.
2. Tests for `publish` on the real CV pair and for `rollback` byte-identity, then the code.
3. Derived outputs (§9) with tests that `index.html` markers and `overview.json` change as expected.
4. `build_data.py` re-apply hook with an idempotence test.
5. Run all unit tests (step 1's 19 must stay green), then a manual `review` → `publish --dry-run`
   on the server against a copy of the site (never the live checkout until the user says so).

## 14. Tests and acceptance criteria

Test file `tests/unit/test_cv_publish.py`, same style as `tests/unit/test_cv_diff.py` (unittest,
skips when the CV fixtures are not reachable). Fixtures: frozen CVs in
`~/.local/share/hurlab-cv-fixtures/` (`2026-10-15`, `2026-10-21`, `2026-10-29`, `2026-10-30`
`_JungukHur-CV.docx`; override with `CV_FIXTURE_DIR`). State and data go to temp dirs. PubMed and
Crossref are replaced by fakes (no network in tests).

Ground truth, measured independently of cv_diff (plain difflib comparison, 2026-10-30):
- **10-29 → 10-30:** 9 papers with a changed Hur J mark (Boison `*` → `$`, plus Combs, Jemiyo,
  Adeluwa, Hasin, Rehana LLM-proceedings, Rehana ChatGPT, Rehana arXiv, Asaduzzaman); Auerbach `*` →
  `$` in Combs; the Nutr J author list (Lee SY... → Kim M, Lee S, Hur J, Shin D); the Khan R01
  moved internal → external. No new records.
- **10-15 → 10-21:** Neuroglia retitle + author cleanup + move to Reviews; EBioMedicine move to
  Group Authorship; the Editorial from "(In press)" to a full citation; a new Book Editing entry;
  citation-tail edits on Shin 2020 and Hur 2021.

Acceptance (each must also be seen failing on a wrong input before it counts):
1. Publishing every item of 10-29 → 10-30 (starting from data built from the 10-29 CV) changes exactly the ground-truth records and nothing else; a diff of the result against the 10-30 CV reports 0 items.
2. `publish` then `rollback` restores every touched file byte-for-byte (sha256 equal).
3. A rejected item is shown as rejected in the next `review` of the same CV and is not published; a changed version of it gets a new id.
4. Running `build_data`'s re-apply twice on the same log gives byte-identical output.
5. `publish` refuses (exit 2) when the published data changed after `review`.
6. A NEW record gets journal/date from the fake PubMed; with both fakes failing it carries the "missing ID" flag.
7. No em dash, no `$` amount, no pending proposal in any written file.

## 15. Preconditions for the implementing session

```
git rev-parse --show-toplevel   → /home/juhur/.moai/worktrees/projects/hurlab/cv-publish
git rev-parse --short HEAD      → be67bcb   (then: git branch -m WT-cv-publish; git fetch origin main;
                                            git merge --ff-only origin/main  → brings this file in)
ls ~/.local/share/hurlab-cv-fixtures/*.docx | wc -l   → 4
python3 -m unittest discover -s tests/unit            → 19 tests, OK
```

## 16. After step 2

- Commit on the `WT-cv-publish` branch; push and deploy only with the user's OK. Deploy: `ssh
  hurlab@100.94.67.89 ~/deploy.sh` (no sudo; it fast-forwards, restarts the admin panel when
  `scripts/` changed, and runs health checks).
- Then step 3 (admin tab) and step 4 (deploy-key push).

## 17. Code references (as of be67bcb)

- `scripts/cv_diff.py`: `load_cv` 36, `load_published` 43, `match_records` 77, `item_id` 115,
  `label` 119, `flags_for` 123, `compare_pair` 137, `diff_publications` 174, `diff_grants` 216,
  `diff` 251, `main` 285
- `scripts/cvlib.py`: `cv_paragraphs` 64, `parse_cv_publications` 77, `section_category` 100,
  `authorship` 107, `cv_record` 154, `parse_grants` 181, `parse_grant` 207, `award_core` 249,
  `merge_supplements` 255
- `scripts/build_data.py`: `classify` 130, `build_publications` 170, `pick_highlights` 237,
  `parse_profile` 256, `build_overview` 294, `pubmed_dates` 371, `crossref_date` 401,
  `add_pub_dates` 421, `split_award` 470, `add_grant_links` 516, `write_home_fallback` 551,
  `write_json` 582, `main` 589
- Memory: `project_cv_incremental_update.md` (design history, ground truth).
