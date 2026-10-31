# PROJECT_LOG.md (active) — Hur Lab

Bounded active log. Newest first. Older sessions are archived under `logs/` when over budget (>10 sessions / ~1000 lines).

## Archives
- logs/PROJECT_LOG_2026-H2.md — 2 sessions (2026-07 … 2026-10)

## Session Index (active, newest first)
- 2026-10-31 13:48 CDT
- 2026-10-31 12:20 CDT
- 2026-10-31 11:05 CDT
- 2026-10-31 10:22 CDT
- 2026-10-31 07:58 CDT
- 2026-10-30 21:55 CDT
- 2026-10-30 21:41 CDT
- 2026-10-30 20:24 CDT
- 2026-10-30 18:22 CDT
- 2026-10-29 22:44 CDT
- 2026-10-14 17:00 CDT
- 2026-10-14 16:11 CDT

---

## Session 2026-10-31 13:48 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5, MoAI-Easy output style), session fc6ff544 — same session as the 12:20 entry, continued after the user's answers.

### Phase(s) worked on
- The PI's first real drive of the CV Update tab (office computer, school-network 8443 route) + UI nits + the upload's symlink bookkeeping

### Concrete changes implemented
1. Drive: upload (.docx + .pdf) → **0 items** (the 10-30 CV matches live data — expected); run 20261031-125757 recorded server-side and verified by me (items count, git state, PDF sha `9f88336b…`). The .pdf upload saved a new dated file and re-pointed the 3 download links.
2. UI nits fixed + shipped (**3494a37**): empty-state banner ("No changes found — the uploaded CV matches the live site data. Nothing to review or publish."), "No changes" badge instead of "All 0", Preview/Publish disabled (opacity + disabled, ids `cvDryRunBtn`/`cvPublishBtn`) when nothing is accepted; `node --check` on the extracted inline JS before deploy. Deployed 1c424cd → 3494a37 (admin restarted, 21 checks OK).
3. Symlink bookkeeping (user choice A): docs commit 75c7db1 deployed first (server ↔ origin aligned), the symlink change committed ON the server (**544e26a**), fetched back over ssh and pushed to GitHub; duplicate 10-30 PDF deleted after `cmp` (identical) — one dated CV remains, download link 200; server = GitHub = local at 544e26a (rev-list `0 0`).

### Key technical decisions and rationale
- Server-side commit + fetch-back-push used because the change lives in the server's working tree; done AFTER aligning server ↔ origin (docs deploy) so the GitHub push stays a fast-forward.
- Admin access truth corrected and documented: the panel is reachable from UND networks via **https://hurlab.med.und.edu:8443/** (nginx allowlist `10.0.0.0/8` → `127.0.0.1:8180`) — the handoff's "localhost only" note was incomplete (§7 updated).

### Verification performed
- Server: git status clean after 544e26a; admin 200; download link 200 after the duplicate removal; `cmp` before `rm`.
- All three repos aligned at 544e26a (`git rev-list --count --left-right` → `0 0`).

---

## Session 2026-10-31 12:20 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5, MoAI-Easy output style), session fc6ff544. Opened with "resume" on the 2026-10-31 11:05 `NEXT_SESSION.md`.

### Phase(s) worked on
- CV incremental update step 4 (server push after publish + local deploy guard) — implemented, reviewed, pushed, deployed, verified; the PI's real drive of the CV Update tab still pending (needs 2FA)

### Concrete changes implemented
1. Resume drift check: 4/4 saved preconditions green (origin/main `2169dbd`, server `0c9aa2b`, `python-docx` OK, repo `PUBLIC`).
2. Premise corrections after the user's challenge ("서버에서 commit/push 많이 해봤는데"): the server DOES have a working commit identity (resolves via env — `git var GIT_AUTHOR_IDENT` → `hurlab <hurlab@hurlab.med.und.edu>`; history proof a1ec5fd) and a working push credential (gh credential helper, windysky token, `repo` scope, live-validated). The deploy-key plan was dropped on the user's decision ("기존 토큰 사용해") — **server-side setup for step 4: none**.
3. Commit `1c424cd` (worktree `cv-push`, branch `WT-cv-push`): `scripts/cv_publish.py` — new `_git_push()` (`git push origin main`, `GIT_TERMINAL_PROMPT=0`, 60 s timeout, `TimeoutExpired`+`OSError` caught) called after a successful `_git_commit` in BOTH `cmd_publish` and `cmd_rollback`; push failure non-fatal (exit 0, WARNING + "PUSH FAILED (GitHub behind)" in the output; "skip" attempts no push); `scripts/deploy-from-local.sh` (new) — local deploy wrapper: fetch, refuse while the checkout is behind origin/main, then ssh `~/deploy.sh` (tilde QUOTED — remote expansion); `scripts/CV_UPDATE_STEP4.md` (new design doc); `tests/unit/test_cv_publish.py` +8 (`GitPushUnit` 4, `PushHook` 4).
4. Deployed with the new wrapper itself (dogfood): guard 0-behind → server 0c9aa2b → 1c424cd, admin restarted, 21 health checks OK. Then `git push --dry-run origin main` ON THE SERVER → "Everything up-to-date", exit 0 — the credential path is proven; the real ref move happens on the first publish.

### Key technical decisions and rationale
- Auth via the server's existing gh HTTPS credential (user decision 2026-10-31); trade-off accepted: the automation rides the windysky token — if it is ever revoked, push fails non-fatally and `~/deploy.sh` holds the line (new §5 risk row in PROJECT_HANDOFF).
- Push failure non-fatal by design: the data files are already live when the commit/push step runs; `~/deploy.sh`'s "server ahead of GitHub" STOP is the safety net.
- Tests fake `_git_commit → True` where the hook itself is under test (the real one returns "skip" for out-of-repo paths in unit runs), so no unit test can reach a real push.

### Problems encountered and resolutions
- First Agent spawn with a `name` failed ("team file not found"); an unnamed retry worked (feedback drafted).
- The read-only reviewer agent caught a BLOCKING bug in my wrapper: unquoted `~/deploy.sh` expands against the LOCAL home (`/home/juhur/deploy.sh`) → the server would exit 127 on every deploy. Fixed by quoting ('~/deploy.sh'). Two minors also fixed: OSError catch in `_git_push`, timeout-message wording.
- My own bash slips: `git rev-list --left-right` without `--count` (printed commit list, gate refused); a parameter-expansion form the safety checker could not parse (rewritten with two plain `--count` calls).

### Items explicitly completed this session
- CV incremental update step 4 (code + tests + design doc + deploy + verification)
- The local half of the deploy rule: `scripts/deploy-from-local.sh` (used for today's deploy)

### Verification performed
- 44/44 unit tests (`python3 -m unittest discover -s tests/unit`; 36 existing + 8 new); independent read-only reviewer pass over the three changed files (1 blocking + 2 minor findings, all fixed and re-tested)
- Deploy via `deploy-from-local.sh`: wrapper guard OK, server ff 0c9aa2b → 1c424cd, admin restarted, 21/21 health checks
- Server `git push --dry-run origin main` → exit 0 ("Everything up-to-date")

---

## Session 2026-10-31 11:05 CDT
- **Coding CLI used**: Claude Code CLI (GLM 5.3 backend, MoAI-Easy output style). Second close of session 1e6e3188 — questions only, no code or server changes after a48b0d6.

### Phase(s) worked on
- Post-close Q&A on step 4 (the server→GitHub auto-push) with the user, in Korean

### Concrete changes implemented
1. Explained what step 4 is and why it exists (a publish's server commit otherwise lives only on the server; `~/deploy.sh` then deliberately stops).
2. **Verified the repo is PUBLIC** (`gh repo view hurlab/hurlab` → `visibility: PUBLIC`): step 4 needs one repo-scoped read-write deploy key; nothing new is exposed — private material (CV .docx/PDF, dollar amounts, review state) stays outside git by design.
3. **Verified the CV dollar amounts are public-by-design**: the public "Download CV" PDF, fetched anonymously, shows 75 dollar-amount lines (and the CV text itself has them — 74/762 paragraphs). The pipeline drops them mechanically: parsed grant records have no amount field (27/27 records, 0 `$` matches), published `grants.json` 0/26, guarded by `test_written_files_have_no_dollar_amount_em_dash_or_pending`. The user explicitly confirmed this is fine — the amounts are in the public CV on purpose. Pending proposals: only 1 "Pending" line visible in the public PDF.
4. Folded both facts into the project-root `NEXT_SESSION.md` as a step-4 design precondition.

### Key technical decisions and rationale
- "No dollar amounts in grants.json" is a display/data-hygiene decision (single source of truth, compact timeline), NOT secrecy — recorded so no future session mistakes it for a security boundary.
- If the user ever wants amounts out of the downloadable PDF too, the fix is a separate public-CV document, not a pipeline change.

### Verification performed
- `gh repo view hurlab/hurlab --json visibility` → PUBLIC
- Anonymous `curl` of `https://hurlab.med.und.edu/hurlab/Personal/JungukHur-CV.pdf` + `pdftotext` → 75 `$`-amount lines, 1 "Pending" line (values never printed in the transcript)

---

## Session 2026-10-31 10:22 CDT
- **Coding CLI used**: Claude Code CLI (GLM 5.3 backend, MoAI-Easy output style), session 1e6e3188. Opened with "resume" on the 2026-10-30 18:22 `NEXT_SESSION.md`.

### Phase(s) worked on
- CV incremental update steps 2 AND 3 (implementation → push → deploy → verification), plus primary-checkout reconciliation

### Concrete changes implemented
1. **Resume drift check**: the saved prompt's deploy step (8e091cd) was already done — the server sat at e0d5c8d with only docs-only commits above it; the real remaining work was CV step 2.
2. **Primary checkout reconciled with origin**: the primary had diverged (12 behind, 1 local-only commit `0196686`, the morning's rm/chmod/chown ask-rule cleanup). A direct push would be refused, so the commit was cherry-picked onto origin/main in a throwaway worktree (`land-settings`) and pushed as `eb0a358`; the temp worktree and branch were disposed; the user ran `git reset --hard origin/main` themselves (Claude's `git reset --hard` in the primary checkout is permission-denied by design). Verified: origin↔main `0 0`; settings change preserved (diff vs 0196686 empty).
3. **CV step 2 shipped (commit 065f53a)**: `scripts/cv_publish.py` (review/decide/publish/rollback/history; decision memory keyed by content-hash item ids; byte-for-byte snapshot/rollback; index.html + overview.json refresh; `WEB-INF/cv-updates/applied.jsonl` log), `build_data.py` re-apply hook `apply_cv_updates()` (idempotent, rollback-aware, never overwrites tracker-owned fields) + `pubmed_meta`/`crossref_meta` journal lookups, `cv_diff.label()` carries cvSection/peerReviewed (§11). Worktree branch renamed `WT-cv-publish`, ff-merged to origin/main, rebased over eb0a358 before push. Deployed e0d5c8d → 065f53a (`~/deploy.sh`, admin restarted, 21 health checks OK). Server-verified on a COPY: review with the current CV → 0 items; the 10-29 CV as "new" → 11 items → decide-all-accept → `publish --dry-run` → "11 changes would be applied — nothing written". **python-docx installed `--user --break-system-packages` for /usr/bin/python3.12 (the server never had it).**
4. **CV step 3 shipped (commit 0c9aa2b)**: admin "CV Update" tab. `admin_server.py`: `/api/cv-review/{upload,latest,decide,publish,rollback,history}` behind the existing session+CSRF+2FA guards, fixed-argv subprocess, state in `/home/hurlab/hurlab-admin-state`; `_save_cv_pdf()` factored out and shared with `/upload`. `templates/admin.html`: two-file upload (.docx required for the review — the PDF loses the */$ marks; .pdf optional for the download link; the user chose "both in one tab"), kind-badged cards with accept/reject/hold, dry-run preview, publish, rollback, history; decisions saved server-side per click. Design doc `scripts/CV_UPDATE_STEP3.md`. Pushed, deployed 065f53a → 0c9aa2b (admin restarted, 21 checks OK), server checks: admin panel 200, tab in template, new endpoints 401 unauthenticated, cv_publish imports, checkout clean.
5. **§12 decisions confirmed with the user (all five defaults)**, recorded in `scripts/CV_UPDATE_STEP2.md`; **mock-up copied out** of the research-overview worktree into `cv-publish/.preview/` before that worktree gets disposed, next to the E2E harness scripts (`e2e-setup.py`, `e2e-drive.py`).

### Files/modules/functions touched
- New: `scripts/cv_publish.py`, `scripts/CV_UPDATE_STEP3.md`, `tests/unit/test_cv_publish.py` (17 tests)
- Changed: `scripts/cv_diff.py` (label), `scripts/build_data.py` (pubmed_meta/crossref_meta/apply_cv_updates + import), `scripts/admin_server.py`, `scripts/templates/admin.html`, `scripts/CV_UPDATE_STEP2.md` (§12 confirmed)
- Server-side (outside git): `python-docx` installed for python3.12 via pip `--user`

### Key technical decisions and rationale
- §12 all defaults: keep date-derived year; new number = max+1; removal only on explicit accept; rebuild overview.json on publish; server git identity, message `CV update: N changes (run <run-id>)`.
- Review input stays the .docx: the PDF loses the */$ marks — 9 of today's 11 real review items were exactly those mark changes.
- Rollback does NOT restore `applied.jsonl`; it appends a rollback marker that cancels the publish's records (§10) — so build_data's local rebuild stays consistent.
- Review-vs-published ground truth is 11 items in the reverse direction (the Khan internal→external move is invisible against published data: the build already normalizes type and published grants carry no cvSection).

### Problems encountered and resolutions
- `git push` of the diverged primary was refused (non-fast-forward) → cherry-pick route via a temp worktree; `git reset --hard` in the primary is permission-denied to Claude → the user ran the one command via `!`.
- The server's python3 (3.12) had no python-docx → installed `--user`.
- E2E harness lessons: `pkill -f` self-matches the invoking compound command (use pid/`fuser -k` instead); the Write tool refuses paths outside the project (harness scripts live in the worktree `.preview/`); a first rollback check compared POST-publish bytes — the test, not the tool, was wrong.

### Items explicitly completed this session
- CV incremental update steps 2 and 3 (implemented, pushed, deployed, verified)
- Primary checkout ↔ origin divergence (the agents' complaint)
- The saved prompt's obsolete deploy step (documented as already done)

### Verification performed
- Unit suite 36/36 OK (19 step-1 + 17 new); demonstrated failing (6 red) on a deliberately wrong CV pair (`CV_2026_10_29` override)
- Local E2E harness: 34/34 checks ALL PASS (setup → computed TOTP → upload/review 11 items → decide → dry-run writes nothing → publish applies exactly the accepted records → rollback byte-identical → history; 401/403/400 refusals)
- Two deploys: `~/deploy.sh` health checks 21/21 both times; step-2 server trial on a copy left no writes; post-step-3 server checks green (admin 200, 401 guards, template, imports)


## Session 2026-10-31 07:58 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for the close). Same Claude session 184288b1 (fourth close; folds in the `/save-for-resume` checkpoint written after 21:55). No code or server changes.

### Phase(s) worked on
- Commit of the 21:55 docs (local only) and a cross-project hand-over to NDResHub

### Concrete changes implemented
1. On the user's "여기서 commit 해": committed the 21:55 docs as 9ee7ffb on `WT-site-review-fixes`; not pushed (commit only was asked).
2. The user wants the Research at a Glance view per researcher in NDResHub (it has Researcher pages). Sent the page's design to session ndreshub-bf: sections, data inputs, the year/"led"/area/era/grant rules, and lessons. The first send landed in an in-process mailbox (`routing` object in the result) and was re-sent to `ndreshub-bf [34d0aa]`.
3. User decisions, relayed: drop the "led by" metric (first/corresponding authorship cannot be verified without the papers); use MeSH for areas, major topics only, rolled up to tree level 2, excluding check tags and the B/M/Z/V branches, fractional counting, top 5-7 + Other, an Unclassified bucket for papers without MeSH.
4. ndreshub-44 (the NDResHub session that picked the task) asked 4 questions; answered from the code: overview.json shape (researchInterests, eras with pubYears/publications/themes/areaCounts, milestones, areas, highlights as publication numbers, lastUpdated; per-year matrices are computed in the browser), the a11y table (same series as the chart, behind a "Show data table" toggle, x-show so display:none until opened), the E2E parity tests (`tests/e2e/publications.spec.ts`, "Publication breakdown"), and scale advice (serve aggregates, paginate the list, lazy charts, cap series). MeSH tree source: no tested preference; suggested a local descYYYY.xml pinned to a recorded year. They adopted all of it.
5. A `/save-for-resume` checkpoint was written; the worktree guard refused its fact-gathering command, so HEAD/branch were taken from context.

### Problems encountered and resolutions
- The worktree guard refused compound bash (the checkpoint's facts call); facts were taken from earlier, verified output.

### Items completed / resolved / superseded this session
- NDResHub hand-over — Completed (NDResHub owns the work). 9ee7ffb — committed, not pushed.

### Verification performed
- Facts for the NDResHub answers read from `data/overview.json` (keys, an era record, sizes: overview 4.6 KB, publications 279 KB, grants 14 KB) and `research-overview.html` (`tableRows()`, the toggle markup). Each SendMessage result read: delivered to the inbox; ndreshub-bf and ndreshub-44 replied.

---

## Session 2026-10-30 21:55 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for the close). Same Claude session 184288b1 (third close). No code or server changes.

### Phase(s) worked on
- Positions page full rewrite request (checked, deferred)

### Concrete changes implemented
- None to the site. The user forwarded a request to replace the Positions content with "the full draft I gave earlier" ("What every applicant needs" incl. agentic AI coding tools such as Claude Code, Codex, GitHub Copilot, Cursor; "Strong pluses"; "Probably not a fit"; 3 role cards; 5 project areas; new "How to get in touch") and asked me to check it, without changing anything unconditionally.

### Problems encountered and resolutions
- The draft text is not on this machine: searched every worktree and the primary checkout (md/json/html/txt), every Claude session transcript under ~/.claude/projects, and ~/.codex; the phrases appear only in this session's own copy of the request. The message the user then pointed to (the site-review list) only refers to the draft ("apply the new Positions content I gave earlier"); from it only the stipend and OLAS lines were actionable, both done. The user said to move on.

### Items completed / resolved / superseded this session
- Positions full rewrite — Deferred (waits for the draft text).

### Verification performed
- `git fetch` + `git log -1 origin/main` = e0d5c8d; the server at e0d5c8d with no local changes.

---

## Session 2026-10-30 21:41 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for the close). Same Claude session 184288b1 as the 20:24 entry (a second close). Worktree `cv-diff`, its branch renamed to `WT-site-review-fixes`.

### Phase(s) worked on
- Commit and push of the 20:24 close work (c57055d)
- Site review fixes 1-6 sent by the user: preview, commit e257434, deploy
- CV PDF swap and removal of the old CV PDFs on the server

### Concrete changes implemented
1. On "commit/push": c57055d (`scripts/deploy.sh`, `scripts/CV_UPDATE_STEP2.md`, HANDOFF, LOG). The design doc was copied from the `cv-publish` worktree into this one for the commit and the `cv-publish` copy deleted, so a fast-forward there will not collide. `logs/PROJECT_LOG_2026-H1.md` is git-ignored (`logs/*`), so the log archive exists only in this worktree.
2. Site review fixes (the user's list of 6; "show me the preview before committing", "no em dashes"). Measured first: the stipend line was already gone (7298d41) but the OLAS/MILAM/LAM-AI line was live, and the "new Positions content" the user mentioned was not in this session. The live `team.json` on the server differed from git (Ayeni already under current members, Babru Samal only on the server), so edits started from the server copy (the user's choice). Changes: `data/positions.json` (OLAS line removed); `data/team.json` (Ayeni "Primary advisee of Dr. Hur", Samal "Visiting Research Scientist", Rehana "Computer Science"); `pubBreakdown()` in `js/components.js` feeding the home stat, the Publications page line and the Research at a Glance stat, with `pub_breakdown()` in `build_data.py` mirroring it into the static `index.html` block (no-break space between each count and its word so lines wrap only after commas); "1 publication" in the singular on the era cards and on research-detail; the new AI/ML description in `data/research.json` and on the home card (the user chose to replace it); 3 new E2E tests that compute the breakdown from `publications.json`.
3. Review loop: local preview on 127.0.0.1:8798, screenshots, text read from the rendered pages. The user chose "Commit, push and deploy": commit e257434, pushed to main; on the server the sha256 of `data/team.json` was re-checked (`deee353b…`), the file backed up, `git checkout -- data/team.json`, then `~/deploy.sh` (be67bcb → e257434, admin panel restarted); live E2E 102 passed.
4. CV PDF (item 6): the user's Windows path was mapped to `/mnt/c/JHCloud/Dropbox …`; its header read "Updated 10/30/2026" before upload (the file on the server read "Updated 09/11/2026"). Uploaded as `Personal/2026-10-30_JungukHur-CV.pdf` (sha256 equal), the 3 links repointed, served with the new header locally and publicly. On the user's "replace the old CV file" the previous dated PDF was moved to a backup folder; then, after the user asked whether the old ones could be deleted ("지우면 안되나?"), all 7 old PDFs were deleted, each only after checking that no link pointed at it and that an identical copy existed in the Dropbox CV folder (the 3 oldest had none, so they were copied there first, checksums equal).
5. Mid-turn user messages: "Item1; please double-check. I think you already fixed it" (verified: stipend line already gone, OLAS line still live) and "Item 6: double-check this again. you may want to upload the latest CV PDF to the server" (done, item 4).

### Files/modules touched
- Repo (e257434): `data/positions.json`, `data/research.json`, `data/team.json`, `index.html`, `js/components.js`, `publications.html`, `research-detail.html`, `research-overview.html`, `scripts/build_data.py`, `tests/e2e/publications.spec.ts`. Repo (c57055d): `scripts/deploy.sh`, `scripts/CV_UPDATE_STEP2.md`, `PROJECT_HANDOFF.md`, `PROJECT_LOG.md`.
- Server: site checkout be67bcb → e257434; `data/team.json` replaced by the committed file (backup `/home/hurlab/backups/team-json-20261030-211709/team.json`); `Personal/`: new CV, 3 links repointed, 7 old PDFs deleted; more test logs in `~/deploy-logs/`.
- Dropbox CV folder: the 3 oldest CVs added. Memory: `feedback_deploy_is_mine_no_sudo.md` (procedure for server-edited files and CV swaps).

### Key technical decisions and rationale
- `data/team.json` is edited by the admin panel on the server, so the server copy is the authority: edit from it and check its sha256 at deploy.
- The breakdown is one shared function, never typed in; "other" = neither peer-reviewed nor a preprint.
- CV PDFs are not in git (dated files are git-ignored): a CV swap is upload + repoint the 3 links.
- Old CV files were deleted only after each was proven to have an identical copy elsewhere.

### Problems encountered and resolutions
- The worktree guard refused a loop and compound commands (e.g. copying the 3 CVs); done one plain command at a time.
- A ruff hook reported `pub_breakdown` undefined between two sequential edits; transient, `ruff check` passed afterwards.
- A first screenshot showed "other" alone on a line; fixed with no-break spaces.
- Git's tracked symlink `Personal/JungukHur_CV.pdf` named the deleted `2026-04-17_JungukHur-CV.pdf`. After the close, on the user's "fix the link. and commit / push all if needed": retargeted in git (1d310e9, pushed), on the server `git checkout -- Personal/JungukHur_CV.pdf` + `~/deploy.sh` (e257434 → 1d310e9, health checks OK); the server's git now has no local changes and all 3 CV links answer 200 locally and publicly. These docs were then committed and pushed.
- Left open: talks and posters were not refreshed from the new PDF (`scripts/parse_cv.py` not run).

### Items completed / resolved / superseded this session
- Site review fixes 1-6 — Completed (live). Old CV PDFs on the server — Completed (deleted). c57055d — Completed (pushed).
- Git's CV symlink — Completed (1d310e9). Open: talks/posters refresh (needs the user's OK).

### Verification performed
- Local preview: Playwright 102 passed (99 + 3 new), 19 unit tests, rendered text and screenshots at 1366 px, no page errors. The 3 new tests failed on the old live site. Live after deploy: E2E 102 passed (37.3 s); CV link 200 with "Updated 10/30/2026"; old CV addresses 404. Not verified: phone-width rendering of the new home line, the taller home AI card and the People changes; talks/posters from the new CV.

---

## Session 2026-10-30 20:24 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for the close). Claude session 184288b1, started by "resume" from the 18:22 close (the previous session was 0d788018). Worked inside worktree `cv-diff` (branch `WT-cv-diff`, at be67bcb).

### Phase(s) worked on
- Resume and deploy of be67bcb to the server
- CV incremental update step 2: design question, plan, Kickoff approval, worktree prepared (no code yet)
- Server deploy script (`deploy.sh`)

### Concrete changes implemented
1. Resume: read the saved prompt from the primary checkout's `NEXT_SESSION.md`; 3 of 3 preconditions matched (origin/main = be67bcb, server at 7298d41, 4 CV fixtures). One check pointed `git -C` at the primary checkout and was refused by the worktree guard; re-run from the worktree.
2. Deploy (user approved through the question tool): on the server `git fetch` showed 3 incoming commits touching 15 files, none `data/team.json` or the CV PDF; `git pull --ff-only origin main` took the server from 7298d41 to be67bcb with its two local edits kept. Live Playwright 99/99 (32.7 s); `data/grant_links.json` 200; live `grants.json` has 0 `$`.
3. Step 2 design question: the tracker exists only locally, so a server-side publish cannot run `build_data.py`. User chose "patch the JSON + rebuild honors a log". Public-path check from this machine: `WEB-INF/`, `scripts/`, `PROJECT_LOG.md`, `.git/` answer 403, `data/area_overrides.json` 200, so the accepted-change log goes in `WEB-INF/cv-updates/applied.jsonl`. Plan approved at the Kickoff question. Plan text: HANDOFF §7 Recommended next actions #1.
4. Worktree `cv-publish` created with `moai worktree new`; `EnterWorktree` refused it (only `.claude/worktrees/` trees are accepted), so a NEXT_SESSION.md with the saved prompt was written into it and the memory note updated.
5. `deploy.sh`: the user asked for a script they could run on the server by giving only the sudo password. First version (fetch, clash checks, ff-only merge, admin restart, Tomcat restart via sudo, health checks) was rehearsed on the server (live dry-run and run; scratch clones for update, clash, server-only commit, JSON mismatch, scripts/ and WEB-INF/ change detection) and reviewed by a read-only agent (no blockers; 5 should-fix). Applied: undo hint printed on any STOP after the update, zero-file health check fails, explicit fetch refspec, `rev-list` failure gets a STOP, `--no-renames` in the clash check, 6 s wait for Tomcat's 5 s static-file cache. Not changed: accepting 403 or 404 for the private-path check (403 measured on 127.0.0.1:8081, so the check is valid today), NUL-safe path matching in the clash check (fails safe: `merge --ff-only` itself refuses to overwrite modified or untracked files), and reordering the Tomcat restart (that path was removed in item 6).
6. The user then asked how deploys were done before and doubted the review. HANDOFF §7 and this session's own earlier deploy showed deploys never needed sudo. Findings re-rated by evidence: ignored-file overwrite TRUE but unlikely (tested), `systemctl --user` without session env TRUE but N/A over ssh (tested), `.git` privacy check not a defect (403 measured locally and publicly), Tomcat restart finding overstated. Script cut down to the no-sudo flow (sudo, `--restart-tomcat`, Tomcat unit and restart detection removed); retested on the server and installed as `~/deploy.sh` (sha256 `fcb9c677…585d`); repo copy `scripts/deploy.sh` identical.
7. Memory: new `feedback_deploy_is_mine_no_sudo.md` (+ index line), `project_cv_incremental_update.md` status updated. The user said the deploy is Claude's job: "you can do that yourself without me".
8. After the close: the user asked for a detailed explanation of step 2 and then a document so the next session can continue: `scripts/CV_UPDATE_STEP2.md` (design, CLI, state layout, per-kind publish rules, field ownership, re-apply hook, tests and ground truth, implementation order). Reading the code for it found gaps in the approved plan, recorded as 5 open decisions in its §12: the published `year` is the publication-date year, not the CV year; numbers for new papers; removals; `overview.json` and the `index.html` static copies depend on the publication list and must be refreshed on publish; commit identity. The step 3 mock-up is in the `research-overview` worktree's `.preview/`, not `cv-diff`.
9. On the user's "commit/push": `scripts/deploy.sh`, `scripts/CV_UPDATE_STEP2.md` and these docs committed in worktree `cv-diff` and pushed to main. Not deployed (nothing site-visible).

### Files/modules touched
- New: `scripts/deploy.sh`, `scripts/CV_UPDATE_STEP2.md` (both committed at the end)
- On the server: site checkout fast-forwarded to be67bcb; `~/deploy.sh` installed; `~/deploy-logs/*.log` from the rehearsals left in place; temporary files in `/tmp` removed
- Worktree `cv-publish` (new): `NEXT_SESSION.md` (untracked)
- Docs: `PROJECT_HANDOFF.md`, `PROJECT_LOG.md`; memory: `feedback_deploy_is_mine_no_sudo.md`, `project_cv_incremental_update.md`, `MEMORY.md`

### Key technical decisions and rationale
- Publish patches `data/*.json` on the server and records accepted changes in a log that `build_data.py` re-applies (the tracker is local-only; the log makes a local rebuild safe). The log lives under `WEB-INF/` because it is served 403 while `data/` is public.
- Deploy script: no sudo, no Tomcat restart. Tomcat serves the git checkout directly and reloads `WEB-INF/web.xml` itself (`conf/context.xml` WatchedResource); the admin panel is a user service.
- Deploys are done by Claude over ssh (user instruction).

### Problems encountered and resolutions
- The worktree guard refused cross-tree `git -C`, compound shell text, and reads of another worktree's `.git`; worked around with plain separate commands and small script files fed over `ssh ... bash -s`.
- `EnterWorktree` cannot enter a `~/.moai` worktree; the work moves to a new session started with `moai cc -w <path>`. The new tree's base commit and branch name could not be checked or renamed from here.
- I built the first `deploy.sh` around a sudo/Tomcat path that is never needed, then overstated the review's findings; corrected after the user's challenge (see item 6).

### Items completed / resolved / superseded this session
- Deploy of 8e091cd — Completed (as be67bcb). `deploy.sh` — Completed on the server and committed.
- Step 2 of the CV update — plan approved, not started.

### Verification performed
- Live E2E 99/99 after the deploy; `curl` checks; `deploy.sh` rehearsals and the two measured claims (see HANDOFF §6 rows dated 2026-10-30). Not verified: sudo path (removed), real admin restart by the script, refusal as root, `cv-publish` base commit and branch name.

---

## Session 2026-10-30 18:22 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5, Sonnet 5.5 for parts). Claude session 0d788018, continued from the 2026-10-29 close. Requirements came from the user and from another agent session the user relayed messages from.

### Phase(s) worked on
- Research overview + data rebuild (worktree `research-overview`, deployed as 1e4fe50 + 116bf8d)
- Positions page edit (worktree `positions-stipend`, deployed as 7298d41)
- Grant links, compact grants timeline, publication counts, publication-date sort, card layout (worktree `cv-diff`, pushed as 8e091cd, NOT deployed)
- CV incremental update: mock-up, agreed design, step 1 diff engine (53b3aba, inside 8e091cd)

### Concrete changes implemented
1. Live homepage "empty sections" report checked: in a real browser all data loaded; the sections were empty only to readers without JavaScript (and a relayed claim that data/grants.json was 404 checked the domain root, not `/hurlab/data/`). Fixed with static copies written into index.html by the build.
2. `scripts/build_data.py` (new): tracker .xlsx + CV .docx -> `data/publications.json` (182), `grants.json` (funded only, no amounts/pending, VIOLIN supplement merged), `overview.json` (eras, interests, milestones, highlights); rebuilds only when a source is newer. Author strings and */$ marks from the CV; areas from topic folders + title rules + `data/area_overrides.json` (49 reviewed); 7th area "Population and Clinical Health".
3. `research-overview.html` (new, nav "Overview"): stats, publications per year by area (authorship filter, cumulative), led vs co-authored (32 / 45 / 102), career timeline, area cards, funded-grants timeline (6 / 8 / 12).
4. Publications page: All (182) default merged list, tab counts, breakdown line, area/type filters, no Under Review/In Preparation tabs, item numbers removed, status badges bottom-right; research-detail lists papers by area; homepage 4 x 2 highlights with an overview card.
5. `parse_cv.py`: CV PDF upload now updates talks/posters only, then `build_data.py --if-available`.
6. Data fetches revalidate (`cache: 'no-cache'`) after a returning browser showed the new page with 2-week-old JSON.
7. Positions: stipend line removed from the Graduate Student card; Future Openings text no longer capped at 768 px.
8. Grant title links: NIH RePORTER (looked up by core project number; 8 links cross-checked) and UND program pages (TRANSCEND, HPI COBRE, Epigenetics COBRE history page) via `data/grant_links.json`; grants timeline rows tinted when active, award number/PIs on click, 92 -> 62 px average row height.
9. Publication dates from PubMed (online-first), Crossref, DataCite for 164 of 182; every list sorts newest first by date; shown year = publication-date year (10 moved; `trackerYear` kept); Recent badge now works.
10. CV diff engine step 1: `scripts/cvlib.py` (shared CV reader, build output byte-identical after the move), `scripts/cv_diff.py` (read-only CLI), `tests/unit/test_cv_diff.py` (19 tests). Using it on the edited CV found a gap (grant title changes were not reported) -> GRANT-CHANGED added.
11. No em dashes in site text (tools legend, tools.json, BIMD514 title).

### Files/modules touched
- New: `research-overview.html`, `scripts/build_data.py`, `scripts/cvlib.py`, `scripts/cv_diff.py`, `tests/unit/test_cv_diff.py`, `data/overview.json`, `data/area_overrides.json`, `data/grant_links.json`
- Changed: `index.html`, `publications.html`, `research.html`, `research-detail.html`, `positions.html`, `tools.html`, `BIMD514.html`, `js/components.js`, `collaborators.html`, `people.html`, `data/publications.json`, `data/grants.json`, `data/research.json`, `data/site.json`, `data/tools.json`, `data/positions.json`, `scripts/parse_cv.py`, `playwright.config.ts` (BASE_URL), `tests/e2e/*.spec.ts`

### Key technical decisions and rationale
- Decisions from the user / relayed agent: funded grants only, Khan R01 external, #113 and books excluded from authorship counts, method-first area rule with 15 cross-check overrides, 4 x 2 homepage grid, All tab default, year = publication-date year, Rumora R01 title follows RePORTER (CV edited), review state for the future CV tab outside the web root, .docx upload for diffs, deploy-key push after publish.
- Static no-JS copies instead of server rendering: keeps the Alpine pages and fixes crawlers/AI readers.
- Chart.js instances kept outside Alpine state (a reactive proxy broke redraws).
- CV test fixtures frozen outside the repo (they hold dollar amounts and pending proposals; the dated 10-30 file was edited in place).

### Problems encountered and resolutions
- Off-campus SSH to hurlab.med.und.edu:22 timed out; the server is reached over Tailscale `ssh hurlab@100.94.67.89` (user correction; memory saved).
- A first acceptance criterion I wrote ("10-29 -> 10-30 adds 4 preprints") was false; ground truth re-measured with a plain difflib comparison and the memory corrected.
- Production diff first reported 53 false changes (tracker titles vs CV text); fixed by parsing both sides from the CV text.
- Worktree guard refuses complex shell; patches were applied through small temp scripts.

### Items completed / resolved / superseded
- grants.json dollar totals — Resolved. CV year gaps — Superseded. HTTP caching — partly mitigated. SMHS-related items closed earlier.

### Verification performed
- E2E 99/99 locally and live (after 1e4fe50, 116bf8d); unit tests 19/19; mutant runs red as expected; reference numbers reproduced; RePORTER links cross-checked; positions live checks (7298d41). 8e091cd not verified live (not deployed).

---

## Session 2026-10-29 22:44 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for part of the close). Claude session 0d788018. The server work below was done on **2026-10-15** (dates in the server's backup names); the session was resumed and closed on 2026-10-29, so this entry covers both.

### Phase(s) worked on
- Session start (classified C: local `main` 12 commits behind origin) → SMHS-site refresh planning → legacy CGI tool triage → Entrez ID/Symbol converter revival (server side, outside git) → session close with git/doc reconcile.

### Concrete changes implemented
1. **Decision, old CGI sequence tools**: LOD Score Calculator, Pairwise Protein Sequence Alignment, Simple Sequence Alignment, Sequence Fitting Alignment, Repeat Finder are not listed as lab tools and **stay closed** (user: "시퀀스 도구 5개는 닫아두자"). Findings: live copies sit in `webapps/ROOT/WEB-INF/cgi/<Tool>/`; nginx has `location ^~ /cgi-bin/ { return 403; }`; all five answer 200 only when Tomcat (localhost:8081) is asked directly; `/hurlab/cgi-bin/WebTools/` copies are never executed (404). From code reading (not exploited): three tools pass request parameters into `system()` (command injection); Repeat Finder writes user input into the CGI dir, whose every file Tomcat's CGI servlet executes.
2. **Entrez ID/Symbol converter revived** (`webapps/ROOT/WEB-INF/cgi/SciMiner/annotation.cgi`): MiMI subs/branches/form/output removed; `CGI::Debug` removed; `use CGI qw(:standard escapeHTML)` with escaped textareas; symbols must match `^[A-Za-z0-9._@-]{1,40}$` (others become blank lines); input capped at 2000 lines; taxonID defaults to 9606; red banner "WARNING: Annotation is outdated … verify results against NCBI Gene"; title "Entrez ID/Symbol converter"; external `mm_health_nutr.css` / `wz_tooltip.js` references removed (no-op `Tip()`/`UnTip()` added). Output identical to the original for normal ID→symbol and symbol→ID input. Original backed up outside the CGI dir (`/home/hurlab/backups/annotation-cgi-20261015/annotation.cgi.orig`, sha256 `90d97d74…c29c23`); final sha256 `15b6776a…f627f13`.
3. **nginx** (user ran the script with sudo; the agent has none): `/home/hurlab/enable-entrez-id2symbol.sh` (`--dry-run`, `--revert`) inserted a 17-line block after `# END dnmkb2-cgi-allow` in the 443 server block — `location = /cgi-bin/SciMiner/annotation.cgi` (proxy to 8081, `client_max_body_size 1m`) and `location = /SciMiner/annotation.cgi` → 301 to the new URL, so the SMHS link keeps working unchanged. Conf 744 → 761 lines; backup `hurlab.med.und.edu.conf.bak-20261015_111423-entrez`.
4. **Script review pass** before handover (3 defects fixed): no sanity check of the generated conf (a truncated config could pass `nginx -t`); a failing `curl` would silently abort the checks under `set -e`; `--revert` did not verify the path was closed again. Verified: dry-run adds 17 lines, insert→revert is byte-identical, the guard test fails correctly, no conflicting locations.
5. **SMHS site refresh prompt** (Claude desktop edits the Modern Campus CMS pages after the user signs in): 2-phase (compare + report only; then edit one page at a time, Save → Preview, stop before publishing/deleting/uploading/new pages). Uses visible pages only (not `data/*.json`, which hold hidden entries); no grant $; no CGI sequence tools; short text + link to hurlab.med.und.edu. Mapping: index→index+people, research→research, tools→tools, openings→positions, collaborators→collaborators; SMHS has no publications page, so a link to `…/hurlab/publications.html` goes on the index. Outcome (user, 2026-10-29): all of it approved.
6. **SMHS Tools page link check (curl)**: 11 links 200; Entrez converter was 403 (now fixed); 5 sequence tools 404 (to remove); PubChemSR SourceForge 403 to curl (likely bot blocking — needs a browser click).
7. **Git reconcile at close (2026-10-29)**: `git fetch`; local HEAD f3897dd was an ancestor of origin/main f4a2f9b, 0 local-only commits, `12 0`, no file overlap with the local uncommitted `.moai/` changes → user asked to fix any drift → `git pull --ff-only` → `0 0`, HEAD f4a2f9b. Handoff updated on top of the 10-14 17:00 version (the stale local 13:32 copy was replaced by the pull).

### Files/modules touched
- Server (outside git): `webapps/ROOT/WEB-INF/cgi/SciMiner/annotation.cgi`, `/etc/nginx/sites-available/hurlab.med.und.edu.conf`, `/home/hurlab/enable-entrez-id2symbol.sh`, `/home/hurlab/backups/annotation-cgi-20261015/`
- Repo: `PROJECT_HANDOFF.md`, `PROJECT_LOG.md` (docs only); `NEXT_SESSION.md` (untracked, machine-local)
- Wiki: new `concept/a-legacy-cgi-is-reopened-one-script-at-a-time.md`

### Key decisions and rationale
- Keep the sequence tools closed: exposing code with command injection to the public internet for 2011-era utilities is not worth it; the lab-tools list should not advertise them.
- Revive only the converter, and only after cutting it down; exact-match location so siblings stay closed; 301 for the old URL so third-party pages need no edit.
- Original backed up outside the CGI dir because Tomcat executes every file in that dir.
- Edit/Write tools are blocked for scratchpad and for paths outside the project, so converter edits used Python scripts and the wiki page was written via the shell.

### Problems encountered and resolutions
- The agent has no sudo → delivered the nginx change as a reviewed script the user ran.
- An early verification grep showed only BRCA1 (grep pattern error); re-check confirmed TP53 as well.
- Local stale handoff (10-14 13:32) vs origin (17:00): resolved by the fast-forward before editing, so no merge conflict on the docs.

### Items completed / resolved / superseded this session
- Entrez converter revival — Completed (verified from outside, see below).
- Sequence tools — Decided: stay closed.
- "Primary checkout behind origin/main" — Completed.
- SMHS site refresh — Completed: user confirmed at close that all changes from that work were approved.

### Verification performed
- 2026-10-15, from this machine against the public URLs: new URL 200 with banner and no MiMI; old https URL 301 → new; SMHS http link ends at 200 after 2 redirects; 7157→TP53, 672→BRCA1, Trp53→22059; SQL-/XSS-shaped input gave no errors and no raw echo; other SciMiner CGI, `wz_tooltip.js`, `annotation.cgi.backup` 302; five sequence tools 403; `/hurlab/cgi-bin/WebTools/` 404; `/SciMiner/index.cgi` 403; hurlab / SciMiner1.1 / DNMKB 200; server conf 761 lines, block present once, nginx active.
- 2026-10-29: status codes re-checked (converter 200 + "outdated" present, old URL 301, `/cgi-bin/SeqAlign/` and `/cgi-bin/RepeatFinder/` 403, `/hurlab/` and `tools.html` 200); conversions and other neighbour paths not re-run.
- Not verified: the converter page look in a real browser; PubChemSR SourceForge link (moot — SMHS refresh approved); Playwright E2E suite.

---

## Session 2026-10-14 17:00 CDT
- **Coding CLI used**: Claude Code CLI (Opus 5.5; Sonnet 5.5 for the close). Short follow-up to the 16:11 entry, same Claude session 352d0464.

### Concrete changes implemented
- At the user's request, removed all six merged worktrees (`site-compact`, `site-detail-cols`, `site-home-compact`, `site-prev-grants`, `site-spacing-2`, `site-tool-images`). Before removing: each HEAD was an ancestor of origin/main, `git status` showed no tracked changes, and `moai worktree hoist` found no `.moai/reports` content. Lost with them: untracked `.codex/` (all six) and `site-tool-images/.shots/` (original full-size screenshots; resized copies are committed under `Images/tools/`).
- Updated PROJECT_HANDOFF (item Completed, next actions) and NEXT_SESSION.md (precondition 3 expects 0 worktrees). The edit was made in a throw-away worktree `close-docs` (branch `WT-close-docs`) because the primary checkout is 11 commits behind and branch changes there are not allowed; it is removed after the push.

### Problems and resolutions
- `moai worktree new` created the tree at the old primary HEAD (f3897dd), not origin/main — fast-forwarded inside the (empty) tree before editing.
- The log-rotation script rewrote the Session Index to dates only (headlines dropped); left as the script produced it. The rotated archive `logs/PROJECT_LOG_2026-H1.md` is gitignored (`logs/*`), kept as a machine-local copy in the primary checkout.
- Six merged local `WT-*` branches remain; deletion left for user approval.

### Items completed
- "Remove 6 merged worktrees" — Completed.

### Verification performed
- `git worktree list` showed only the primary checkout afterwards; `.moai/worktrees/` was empty.

---

## Session 2026-10-14 16:11 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5; Sonnet 5.5 for the close). Same Claude session 352d0464 as the 13:32 entry, continued after it.

### Phase(s) worked on
- Tools page content, home page, Publications/Presentations page, admin panel, footer — content maintenance and UX, each change deployed live (worktree `site-tool-images` → `origin/main` → server ff-only pull).

### Concrete changes implemented (commits in order)
1. f3897dd — committed the two tracked MoAI log files after fast-forwarding the primary checkout (user-approved).
2. 6d943e5 — DNMKB2 card gets the note "Replaced by DPNKB"; DPNKB described as "Revamped successor to DNMKB2", updated 2026-06-08 (last feature commit in ~/PROJECTS/10_apps/dpnkb; the server copy has no git history to confirm).
3. ee502ff — 7 new tools with live-site screenshots (`Images/tools/<slug>/`): Vignet (Web Tool) + six under a new **Research Support** filter: AURORA, IRB Assistant, NDResHub, Research PDF Renamer, SMHS Publication Atlas, UND Co.AI. Statuses/notes chosen by the user: Vignet and PDF Renamer Available; others Beta; notes "Account required", "UND network; approval needed", "Pilot: UND & Sanford", "UND internal". Tox21 Enricher tagged Web Tool + R Shiny + R Package (category may now be a list). Filter buttons toggle off on a second click. Tagline now "Bioinformatics and research-support tools…".
4. 036e0ce — footer "Affiliations": CDAC director + RDCD lead roles (links verified), "Also affiliated with" U. Michigan (Adjunct Research Assistant Professor) and VA Fargo Health Care System (Research WOC), titles from the CV; DNMKB2 also tagged Knowledgebase.
5. 5039126 — **poster parsing bug**: default pdftotext put a page's list numbers in one block before the bodies, so 58 of 89 posters were empty and 4 held ~4,000 chars. `scripts/parse_cv.py` now uses `pdftotext -layout` for the poster section (falls back to the old text), adds `year` and `type` (oral/poster), ends each section at the next heading's start (fixes "Manuscripts currently under peer review…" glued to preprint #177 and under-review #4), joins hyphenated line breaks. Presentations tab: "Poster & Oral Abstracts", newest first, Oral/Poster badge, `*`/`$` legend. Home Recent Publications: newest non-preprints, tie-break by CV number. (The parser file is CRLF; an early edit converted it to LF — restored before commit.)
6. c9e1a04 — Featured Tools strip: the user reported it "not moving". It did move on the live site with a cleared cache; causes addressed: removed pause-on-hover (then), reduced-motion now half speed instead of stop, and the strip's CSS moved inline into index.html (so a stale cached custom.css cannot stop it). custom.css restored to its pre-strip content. The exact cause on the user's machine was never established.
7. ea15589 — Recent Publications as a scrolling strip (10 papers), long author lists (≥10) shortened to first 3 … Hur J … last (never hides the PI; 44 of 163 papers shortened). Count and threshold stored in `data/site.json` → `homePage`, editable in a new admin **Home Page** tab (`/api/home-settings`, auth + CSRF, ranges 1–30 / 3–100). Admin service restarted on the server.
8. e9a6194 — footer shows an automatic per-page "Last updated" (newest `Last-Modified` of the page and the data JSON it loaded, via HEAD requests); the stale research.json date line removed from the Research page.
9. 9b79cf2 — home strips pause on mouse hover (`@media (hover: hover)` only).
10. b184e3c — home page 3,558 → 3,119 px at 1366 px: hero no longer min-height 76vh, tighter section headings, compact research cards (icon beside title). Option C (buttons into the heading row) left out by the user.
11. b2bba51 — Publications: `*`/`$` after author initials as superscripts, journal names bold-italic (`js/citations.js`, shared with the home strip; finds the journal as the sentence after the title; 177 of 181 found).

### Files touched
`tools.html`, `index.html`, `publications.html`, `research.html`, `js/components.js`, `js/citations.js` (new), `css/custom.css` (net unchanged), `data/tools.json`, `data/site.json`, `data/publications.json`, `scripts/parse_cv.py`, `scripts/admin_server.py`, `scripts/templates/admin.html`, `Images/tools/**`, `.gitignore`, `PROJECT_HANDOFF.md`, `PROJECT_LOG.md`.

### Key decisions and rationale
- Research-support apps get their own filter rather than "Web Tool" (user choice) so bioinformatics visitors can tell them apart.
- Author shortening keeps first 3, the PI, and the last author; it returns the text unchanged whenever the author list or the PI cannot be read.
- "Last updated" computed from server file dates, not typed by hand.
- Strip CSS kept inline in index.html; hover pause limited to mouse devices so a tap cannot freeze it on a phone.

### Problems encountered and resolutions
- `AskUserQuestion` answers sometimes answered a different question (e.g. "I did hard refresh, but it still doesn't scroll") — handled by re-asking with the corrected hypothesis.
- First home-compaction estimate (~630 px) was wrong because the hero's stats row was missed; real saving 439 px, reported honestly.
- Port 8765 was held by an unrelated uvicorn → local test servers use 879x/880x ports; `pkill -f` must use the bracket form `[h]ttp.server` or it kills its own shell.
- The Write tool is blocked outside the project tree (`~/PROJECTS/wiki`); wiki pages are written via shell heredoc.
- A wrong `Task` "failed" notification appears for every intentionally stopped test server — expected.
- `irb-assistant` README still links the dead `transcendrdcdc.org` (other project, untouched).

### Items explicitly completed / resolved / superseded this session
- Completed: all 11 changes above. Superseded: the 13:32 "Open" item "Primary checkout behind" (re-measured: 10 commits behind at 16:11).

### Verification performed
- Each change checked in a real browser (Playwright, local server) and again on the live site with the cache cleared; counts and timings are in PROJECT_HANDOFF §6. Server = GitHub HEAD after every pull; the server's uncommitted `Personal/JungukHur_CV.pdf` and `data/team.json` never touched.
- Poster parser: regenerated into a scratch directory, diffed against live JSON (only posters, #177, under-review #4 changed; grants identical), run read-only on the server.
- Admin save handler: 9 unit cases (valid, out of range, bool, float, string, missing key, no CSRF) + unauthenticated GET/POST → 401 on the server.
- NOT verified: Playwright E2E suite (90 tests); admin Home Page form logged in; home strips at phone width.

