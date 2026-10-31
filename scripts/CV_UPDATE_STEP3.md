# CV incremental update — Step 3: the admin "CV Update" tab

Status: **implemented on the WT-cv-publish branch** (this file documents the design it follows).
Written 2026-10-31 (session 1e6e3188). Step 2 (`scripts/cv_publish.py`, the engine) and its
design live in `scripts/CV_UPDATE_STEP2.md` — read that first; §12 decisions apply unchanged.

What the user decided for this step (2026-10-31): **one tab, two uploads** — the review input is
the CV `.docx` (the PDF loses the `*`/`$` authorship marks and section boundaries, so it cannot
drive the diff), and the PDF upload that feeds the public "Download CV" link rides along in the
same tab. The old dashboard PDF upload keeps working unchanged.

## 1. Endpoints (admin_server.py)

All under the existing session + CSRF + 2FA + network-allowlist guards; every handler starts
with `_require_auth()` and `_validate_csrf()` like the other `/api/*` endpoints. Scripts run via
`subprocess.run([PYTHON_BIN, "scripts/cv_publish.py", ...])` — fixed argv, no shell, cwd
`scripts/`. The state root is the new constant `ADMIN_STATE` (`/home/hurlab/hurlab-admin-state`,
outside the web root; step 2 decision A).

| Endpoint | Method | Body | Does |
|---|---|---|---|
| `/api/cv-review/upload` | POST | multipart `docx` (required) + optional `pdf` | PDF → the same Personal/ + symlink handling as `/upload` (factored into `_save_cv_pdf`); docx → temp file in `ADMIN_STATE/tmp/`, `cv_publish.py review`, read `runs/<id>/items.json`, return `{run, items, counts}` |
| `/api/cv-review/latest` | GET | — | the newest run in `ADMIN_STATE/runs` with decisions joined (page-refresh recovery); `{run: null}` when none |
| `/api/cv-review/decide` | POST | JSON `{run, ids: [...], decision}` | `cv_publish.py decide` |
| `/api/cv-review/publish` | POST | JSON `{run, dry_run: bool}` | `cv_publish.py publish [--dry-run]`; returns the tool output (timeout 300 s — NEW records hit PubMed/Crossref) |
| `/api/cv-review/rollback` | POST | JSON `{snapshot_id}` (optional) | `cv_publish.py rollback` |
| `/api/cv-review/history` | GET | — | `history.jsonl` entries + snapshot list, read directly (no subprocess) |

Validation before any subprocess: run id and snapshot id match `^\d{8}-\d{6}$`, item ids match
`^[0-9a-f]{12}$`, decision ∈ {accept, reject, hold}. Uploads keep the 50 MB cap; `.docx` /
`.pdf` extensions checked. Nothing under `ADMIN_STATE` is served by Tomcat (it is outside the
web root), and the docx never lands in the repository.

## 2. The tab (templates/admin.html)

Follows `.preview/cv-review-mockup.html` (copied out of the research-overview worktree), trimmed
to what the engine actually offers — every item is accept / reject / hold:

1. **Upload section**: two file inputs (`.docx` required, `.pdf` optional) + "Upload & Review".
2. **Run summary**: kind-count chips; the run id and CV name.
3. **Item cards** grouped by kind family, each with the kind badge, record number/year/title
   header, published vs new side-by-side citation, detail lines, flags, and
   Accept / Reject / Hold buttons. `METADATA` items (pre-accepted) render as accepted and
   locked. `REMOVED` items label the buttons "Remove" / "Keep on site".
4. **Sticky publish bar**: decided counter, **Preview** (dry-run) and **Publish** buttons;
   output goes to a result log.
5. **History & rollback**: one row per publish (snapshot id, time, counts) with a
   confirm-then-rollback button; refresh restores the latest run via `/api/cv-review/latest`.

Every decision click calls `/api/cv-review/decide` immediately, so decisions survive a page
reload (they are stored in `ADMIN_STATE/decisions.json` — the step-2 decision memory).

## 3. Out of scope (same as before)

Per-item "Edit" and the area/preprint radio options from the mock-up are NOT wired — the
engine has no such knobs yet (areas come from the title rules, PREPRINT-NOW-PUBLISHED always
keeps both records). Server push to GitHub remains step 4.

## 4. Verification

Local: a throwaway `/tmp` copy of the admin server (paths sed-patched) is driven end to end —
setup → TOTP (code computed from the seeded secret) → upload → review → decide → publish →
rollback — against a synthetic site copy, so nothing outside `/tmp` is touched. Server: the
usual deploy + trial on a copy, after the user's OK (same protocol as step 2's deployment).
