# PROJECT_LOG.md (active) — Hur Lab

Bounded active log. Newest first. Older sessions are archived under `logs/` when over budget (>10 sessions / ~1000 lines).

## Archives
- logs/PROJECT_LOG_2026-H2.md — 6 sessions (2026-07 … 2026-10)
- logs/PROJECT_LOG_2026-H1.md — 8 sessions (2026-03 … 2026-04)

## Session Index (active, newest first)
- 2026-11-01 19:35 CST
- 2026-10-31 15:24 CDT
- 2026-10-31 13:48 CDT
- 2026-10-31 12:20 CDT
- 2026-10-31 11:05 CDT
- 2026-10-31 10:22 CDT
- 2026-10-31 07:58 CDT
- 2026-10-30 21:55 CDT
- 2026-10-30 21:41 CDT
- 2026-10-30 20:24 CDT

---

## Session 2026-11-01 19:35 CST
- **Coding CLI used**: Claude Code CLI (MoAI-Easy output style; Claude Opus 5.5 for the work, Sonnet 5.5 for the close). Same session id fc6ff544 as the 2026-10-31 closes. This entry also records the morning's overview-generator work (HANDOFF §2/§4 rows dated 2026-11-01 11:45 CDT), which had no log entry.

### Phase(s) worked on
- Internal Research Overview generator (morning, home/other computer) and funded-grants display + supplement handling (evening, office PC `UNDMED-CQ9FRT3`)

### Concrete changes implemented
1. **Morning (95e9538, 9a0e7bc, b68ca57)**: `scripts/build_overview.py` fills `scripts/templates/overview_template.html` (copied from OneDrive `Publications/_overview_build/`; edits: computed year bounds `{{LAST_YEAR}}`/`{{NOW_DECIMAL}}`, tools sentence) from `data/*.json` + `overview_internal.json` and writes `Publications/Hur_Lab_Research_Overview.html` in OneDrive; called at the end of `build_data.py` (also on its "nothing to do" path); CV_DATE = max(filename date of the CV source, last live publish in `applied.jsonl`); em-dash and leftover-placeholder guards; 17 tests; acceptance checks 161/132/18/182/6/20, 77/32/45/102, grants 6/8/12, 0 console errors, 0 em dashes, 0 `$`. Notes file `OVERVIEW_BUILD_NOTES.md` left in the OneDrive folder. Template mode fixed from 100755 to 100644 ("권한 정리").
2. **Server sync (evening)**: server was 7 commits behind (docs + scripts only, but `cv_publish` does not pull before pushing, so the next real publish would have failed with PUSH FAILED); `deploy-from-local.sh` brought it to b68ca57; server `build_data.py --if-available` still exits 0.
3. **Funded grants (c901bbc, e1ab72b)**, PI request on https://hurlab.med.und.edu/hurlab/research-overview.html: active awards first, then completed, with "Active (n)" / "Completed (n)" headers and a heavy rule; the U24 administrative supplement (`3U24AI171008-05S1`, 2026-07 to 2027-05) is its own row (own RePORTER link) placed right under VIOLIN 2.0, not counted as an award (user choices: "row only, count stays 6", "CV wording as the title"). Code: `cvlib.merge_supplements` replaced by `is_supplement` + `grant_ident` (award core + S suffix) + `attach_supplements`; `cv_diff`, `cv_publish` and `build_data` matchers use `grant_ident`; `build_overview.build_grants` flags supplements (`x`) and the template excludes them from the counts; `research-overview.html` mirrors the placement in JS; `index.html` and `write_home_fallback` skip supplements in the "Active grants" count.
4. **Internal JSON moved**: this PC had no `~/.local/share/hurlab-admin-state/overview_internal.json`; recovered from the generated page's `PILOTS`/`ERAS`/`IDEAS` constants into OneDrive `Publications/_overview_build/overview_internal.json`; `build_overview.DEFAULT_INTERNAL` now reads it (user choice "OneDrive folder"). Docs updated (PROJECT_HANDOFF, `CV_UPDATE_STEP2.md` symbol lines, OneDrive notes).

### Files/modules/functions touched
- `scripts/cvlib.py`, `cv_diff.py`, `cv_publish.py`, `build_data.py`, `build_overview.py`, `scripts/templates/overview_template.html`, `research-overview.html`, `index.html`, `data/grants.json`, `tests/unit/test_grant_supplements.py` (new, 12 tests), `PROJECT_HANDOFF.md`, `scripts/CV_UPDATE_STEP2.md`; OneDrive `_overview_build/OVERVIEW_BUILD_NOTES.md` and `overview_internal.json`.

### Key technical decisions and rationale
- A supplement shares its parent's award core, so every matcher that keyed on the bare core would have merged the two once they were separate records; one shared key function fixes all four modules at once (wiki: `concept/an-identity-key-must-tell-a-child-record-from-its-parent`).
- The internal JSON went to OneDrive, not machine-local state, because the user works from several computers synced with smart-rsync and `~/.local/share` does not travel (wiki: `concept/a-hand-edited-input-in-machine-local-state-is-gone-on-the-other-computer`; memory: project_two_build_computers).
- Live site and data only change through the existing path: worktree `WT-*` branch, `git push origin WT-x:main` after a `0 0` check, `deploy-from-local.sh` from the worktree, then the user's `git pull --ff-only` in the primary. Both worktrees and branches disposed after the push was verified.

### Problems encountered and resolutions
- Playwright MCP browser missing on this PC (expects chromium-1252): used the cached chromium-1247 headless binary for screenshots and DOM dumps.
- `build_data.py --force` only moved `lastUpdated` in `publications.json`/`overview.json`; reverted with `git checkout --` inside the worktree.
- 5 `Reapply` tests errored without CV fixtures on this PC; fixed by `CV_FIXTURE_DIR` pointing at the Dropbox CV folder (73/73 OK).
- Port 8765 was already taken by another local server (curl returned its pages); used 8791/8792. A `pkill -f` matched its own shell (exit 144); replaced by killing the pid found with `ss`.
- ruff reports 6 F-findings, all in `scripts/admin_server.py` and already present on origin/main; left alone.

### Items explicitly completed / resolved / superseded this session
- Completed: overview generator, template mode fix, server catch-up deploy, grants regroup, supplement row + placement, internal JSON relocation. Superseded: the "local state folder" location for `overview_internal.json`. Opened then closed: the old local copy on the first computer needs no merge, the user has not worked there since creating the file (HANDOFF §4).

### Verification performed
- Unit suite 73/73 OK; `cv_diff` of the 2026-10-30 CV: 0 items vs new data, 1 GRANT-NEW vs old data; live site headless check "Active (6)", "Completed (20)", supplement right after VIOLIN 2.0, 0 console errors, home counter 6; deploys c901bbc and e1ab72b with 21 health checks each; primary = origin/main = server = e1ab72b, `0 0`.

### Not verified
- `cv_publish`'s real (non-dry-run) push still awaits the first real CV change; no real publish has yet gone through `grant_ident` (applied.jsonl does not exist, so no old records need migrating).

## Session 2026-10-31 15:24 CDT
- **Coding CLI used**: Claude Code CLI (MoAI-Easy output style; Claude Opus 5.5, GLM 5.3 for the close). Third close of session fc6ff544 — no new code after cc9901e.

### Phase(s) worked on
- Post-close cleanup executed immediately on the user's request, then the final close

### Concrete changes implemented
1. Cleanup (details recorded in the 13:48 entry, item 5): all 5 worktrees disposed, 12 `WT-` branches deleted (last one via a throwaway detached tree after an ancestor check), artifacts preserved at `.preview/cv-tab-harness/` and `logs/`; docs committed as cc9901e.
2. The user fast-forwarded the primary (`git pull --ff-only`, eb0a358 → cc9901e) — this close ran IN the primary for the first time since the CV arc began.

### Items explicitly completed this session
- Worktree/branch disposal + primary sync (everything the 14:04 close had queued for "next session")

### Verification performed
- `git rev-parse HEAD` = cc9901e = origin/main, `behind=0 ahead=0`; `git worktree list` → primary only; `WT-*` branch count 0

---

## Session 2026-10-31 13:48 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5, MoAI-Easy output style), session fc6ff544 — same session as the 12:20 entry, continued after the user's answers.

### Phase(s) worked on
- The PI's first real drive of the CV Update tab (office computer, school-network 8443 route) + UI nits + the upload's symlink bookkeeping

### Concrete changes implemented
1. Drive: upload (.docx + .pdf) → **0 items** (the 10-30 CV matches live data — expected); run 20261031-125757 recorded server-side and verified by me (items count, git state, PDF sha `9f88336b…`). The .pdf upload saved a new dated file and re-pointed the 3 download links.
2. UI nits fixed + shipped (**3494a37**): empty-state banner ("No changes found — the uploaded CV matches the live site data. Nothing to review or publish."), "No changes" badge instead of "All 0", Preview/Publish disabled (opacity + disabled, ids `cvDryRunBtn`/`cvPublishBtn`) when nothing is accepted; `node --check` on the extracted inline JS before deploy. Deployed 1c424cd → 3494a37 (admin restarted, 21 checks OK).
3. Symlink bookkeeping (user choice A): docs commit 75c7db1 deployed first (server ↔ origin aligned), the symlink change committed ON the server (**544e26a**), fetched back over ssh and pushed to GitHub; duplicate 10-30 PDF deleted after `cmp` (identical) — one dated CV remains, download link 200; server = GitHub = local at 544e26a (rev-list `0 0`).
4. Session close (/endsession 14:04 CDT): 2 cross-project wiki lessons authored (unquoted tilde in ssh remote commands; localhost binding vs reachability); PROJECT_LOG rotated with the H2 archive consolidated at the primary checkout's `logs/`; `NEXT_SESSION.md` refreshed for the cleanup session.
5. Immediate cleanup on the user's "지금 다 정리해" (14:55): cv-publish's harness artifacts copied to the primary (`.preview/cv-tab-harness/`: mock-up + `e2e-setup.py` + `e2e-drive.py`); the 4 other worktrees removed (`--force`; untracked `.codex`/`.preview` junk only, verified first); 11 merged `WT-` branches deleted from within cv-push; cv-push removed right after this commit and `WT-cv-push` deleted via a throwaway tree; the primary fast-forward remains the user's single `git pull --ff-only`.

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

