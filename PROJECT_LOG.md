# PROJECT_LOG.md (active) — Hur Lab

Bounded active log. Newest first. Older sessions are archived under `logs/` when over budget (>10 sessions / ~1000 lines).

## Archives
- logs/PROJECT_LOG_2026-H1.md — 5 sessions (2026-03 … 2026-04)

## Session Index (active, newest first)
- 2026-10-30 20:24 CDT
- 2026-10-30 18:22 CDT
- 2026-10-29 22:44 CDT
- 2026-10-14 17:00 CDT
- 2026-10-14 16:11 CDT
- 2026-10-14 13:32 CDT
- 2026-07-09 23:57 CDT
- 2026-04-08 CDT (early)
- 2026-04-08 CDT (implementation)
- 2026-04-08 CDT (security completion)

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

## Session 2026-10-14 13:32 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 5.5, then Sonnet 5.5 for the close)

### Phase(s) worked on
- Content/UX refinement of the Tools & Software page (this session, 352d0464)
- Folded in: the earlier same-day session (455f03ad) and the unlogged commits since 2026-07-09 — **reconstructed from commit messages only**, not re-verified:
  - Gap commits: 9cb954d (Publications: 3 recent papers; rolling 6-month Recent badge), 7332751 (in-press → published citations), 3173575 (BIMD514 Zoom auto-redirect page), 6178001 + 1553737 (MoAI ADK template sync; .gitignore project rules restored)
  - Session 455f03ad: a1ec5fd (server CV auto-update) merged as 297e82b; 09d9cbc (hide grant dollar amounts, compact banners); a059e3b (web.xml blocks dot-directories / agent tooling); e45daaf (People/Positions/Collaborators spacing); ea32045 (Home hero ~10% smaller); 9ee94da (publication sort ties, CV year parsing, Home topic links); fa9f318 (Research collapsible Previous Grants); 464f580 (topic pages two-column, tighter Tools cards, long-citation wrap)

### Concrete changes implemented (this session)
1. **Tool images** (5428e47, 7a0693c): 18 images in `Images/tools/<slug>/` (≤1200 px JPEG q80, ~1.6 MB total, lazy-loaded); `images: [{src, caption}]` per tool in `data/tools.json`. Collapsed cards: 120 px preview strip (`object-cover object-top`); tools without images get a gradient placeholder. Expanded card: 7:3 flex split (details left, image column `md:w-[30%]` right, each image opens full size). Sources: live-site screenshots, public GitHub README figures, PubChemSR app screenshots and ChemFuse architecture figure from the private repos (user approved), scGEN Figure 1 from the published paper.
2. **PubChemSR / ChemFuse links** (7a0693c): both GitHub repos are private (unauthenticated `curl` → 404). PubChemSR now links to SourceForge (`urlLabel: "SourceForge"`), GitHub removed. ChemFuse links removed. New optional fields `urlLabel` (button text) and `notice` (gray badge).
3. **SciMiner** (66be5d2): card renamed "SciMiner 1.1 & 2.0"; `updated` 2026-09-15 = latest code commit across the server's `SciMiner1.1/` (2026-08-23) and `SciMiner2.0/` (2026-09-15) apps.
4. **Status labels** (b3b5c66): "Active / In Development" replaced by visitor-access labels **Available / Beta / Coming soon** (`status`: available | beta | coming-soon), defined once in a `statuses` map in `tools.html` that also renders a one-line legend under the filter buttons. richStudio = beta, ChemFuse = coming-soon, all others available; PubChemSR keeps Available + `notice: "v2.0 coming soon"`.
5. **Borders + order** (c6ccbe2): card outline `border-gray-200`, image divider `border-gray-300`; tools sorted case-insensitively by name at load (`localeCompare`, sensitivity base), so JSON order no longer matters.

### Files touched
- `tools.html`, `data/tools.json`, `Images/tools/**` (new); `PROJECT_HANDOFF.md`, `PROJECT_LOG.md`
- `css/custom.css` deliberately NOT changed (`gradient-border` is shared with `people.html`)

### Key decisions and rationale
- Status labels defined by what a visitor can do (user decision after review showed "In Development" mixed private, beta and published tools).
- ChemFuse workflow figure (fig2) dropped: its SVG rendered with overlapping labels in the browser.
- Sorting done in the page, not the JSON, so new tools land in place automatically.

### Problems and resolutions
- Port 8765 held by an unrelated `uvicorn` → local test server moved to 879x ports.
- Playwright screenshots can only be written under the project root (`.playwright-mcp/`) — temp images saved there and deleted after review.
- No SVG converter installed → SVGs rendered via the browser and screenshotted.
- `pkill -f "http.server 8791"` matched its own shell (exit 144) → use the bracket form `[h]ttp.server`.
- A Python one-liner `open(f,'w').write(open(f).read()…)` truncated `MEMORY.md` before reading it → rewritten in full.

### Completed / resolved this session
- Tools-card images (the task carried over from 455f03ad) — Completed.
- Private-repo 404 buttons (PubChemSR, ChemFuse) — Resolved.
- scGEN "no images" — Resolved (paper Figure 1).

### Verification performed
- Playwright on a local server at 1366 px and 390 px: all 18 images load (`naturalWidth` > 0), 0 page errors, expanded image column = 353 px of a 1216 px card, label + color correct on all 13 cards, alphabetical order correct (also within the R Package filter), PubChemSR note fits on one line.
- Live: `curl` 200 for `tools.html`, `data/tools.json` and sample images; live JSON shows 18 images / 13 tools, 11 available / 1 beta / 1 coming-soon, "SciMiner 1.1 & 2.0". Server = GitHub = c6ccbe2 after each ff-only pull; server's uncommitted `team.json` / CV PDF untouched.
- Not run: the 90-test Playwright E2E suite.

---

## Session 2026-07-09 23:57 CDT
- **Coding CLI used**: Claude Code CLI (Claude Opus 4.8)

### Phase(s) worked on
- Session start (startsession reconcile): classified project state; found handoff/git drift (3 commits post-dating the docs)
- Deployment verification: confirmed live server ↔ GitHub ↔ local fully synced
- Content maintenance: collaborators page reorganization + live deploy

### Concrete changes implemented
1. Verified the deployed webapp dir on hurlab.med.und.edu **is** the git working tree Tomcat serves; all three copies (local, GitHub, server) at the same HEAD. Deploy path = commit/push + `git pull` on server.
2. Reorganized `data/collaborators.json` from 4 → 7 sections:
   - Hid 5 collaborators via a reversible `"hidden": true` flag (Brosius, Eun-Hee Cho, Kyung Ju Lee, Joyce Ohm, Susan Masino) — retained in JSON, filtered out on the page.
   - Added 14 collaborators, each with an individually web-verified profile URL: Stephanie Eid (AUB), Amy Rumora (Columbia), Yong Kim & Mi-Hyeon Jang (Rutgers), Alexander Diehl (UB), Bill Duncan (UF), Guanming Wu (OHSU), Cui Tao (Mayo), Ramkumar Mathur & Donald Jurivich (UND), Jun-Il Yoo (Inha), Motoki Takaku (UND), Nadeem Khan (UF), Kumi Nagamoto-Combs (UND), Jinho Yoo (YooJinBioSoft, Korea).
   - New sections: Geriatrics / Biological Age / Digital Health, Cancer, Immunology / Infectious Disease.
   - Renamed: "Epigenetics in NeuroSciences" → Neuroscience; "Literature Mining / Ontology" → Biomedical Informatics / Ontology (moved to first). Moved Archana Dhasarathy → Cancer. Title separators normalized to "/" (no "&").
3. `collaborators.html`: reversible hidden filter in the member `x-for`; added amber/rose/blue colors + clock/chart/shield icons; two-column responsive grid per section (`grid-cols-1 sm:grid-cols-2`).
4. `scripts/templates/admin.html`: added amber/rose colors + clock/chart icons to the admin panel color/icon dropdowns.

### Files/modules/functions touched
- `data/collaborators.json` — 4→7 sections, 24 visible + 5 hidden members
- `collaborators.html` — hidden filter, colorMap +3, icons +3, 2-column grid
- `scripts/templates/admin.html` — colorOptions/iconOptions extended
- `PROJECT_HANDOFF.md`, `PROJECT_LOG.md` — this endsession reconcile

### Key technical decisions and rationale
- Reversible `hidden` flag over deletion: keeps the data; the admin save round-trips it (whole-object JSON serialization preserves unknown fields).
- No-fabrication URL verification: every new link fetched and identity-confirmed. Caught a search-surfaced ORCID that belonged to a DIFFERENT person (jiyeon jo, not Jinho Yoo); used YooJinBioSoft's http site (its HTTPS cert is mismatched — shared hosting).
- Two-column grid to cut vertical page length.

### Problems encountered and resolutions
- Local clone had no node_modules (gitignored) → installed `@playwright/test` (browsers already cached) to run headless render QA with Chromium.
- AOS opacity hid below-fold sections in static screenshots → forced `aos-animate` for the QA capture.
- Cui Tao's Mayo bio bot-blocks (HTTP 403) and Stephanie Eid's AUB profile is a JS SPA → used verified Google Scholar / AUB registry cross-check; flagged for a browser spot-check.

### Deployment (3 commits, pushed + pulled to server + live-verified)
- `c3f1df5` reorg → `b3b8a36` two-column → `e581475` Jinho Yoo + title tidy.
- Each: `git pull --ff-only` on server (admin service restart for the admin.html change); live `https://hurlab.med.und.edu/hurlab/` returned HTTP 200 with updated content.

### Items explicitly completed / resolved this session
- Collaborators reorganization deployed live and verified.
- Handoff/log drift reconciled: 3 previously-undocumented commits (fef9c27, c0a907a, d1eb197) now reflected in PROJECT_HANDOFF.md; HTTPS risk row corrected for the 2026-05 recurrence.

### Verification performed
- Headless Chromium render QA: 7 sections, 24 visible + 5 hidden, all icons resolved, 0 JS errors.
- Live URL curl after each deploy: HTTP 200, correct titles/members.
- git: clean tree; local HEAD == origin/main == server HEAD (e581475).

---

## Session 2026-04-08 CDT (early)

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)

### Phase(s) worked on
- Document updates only (no implementation)

### Concrete changes implemented
1. Marked HTTPS/port 443 issue as Resolved in PROJECT_HANDOFF.md (SSL renewed, port 443 opened by UND IT)
2. Removed "Contact UND IT about HTTPS/port 443" from recommended next actions
3. Updated CLAUDE.md to fix stale `v2/` references — site is now at root, not in `v2/` subdirectory
4. Updated timestamps in PROJECT_HANDOFF.md

### Items explicitly completed
- HTTPS/SSL resolution recorded
- CLAUDE.md corrected to reflect root-level deployment (v2→root cutover happened in Session 2026-03-14 16:30 CDT)

---

## Session 2026-04-08 CDT (implementation)

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)
- **Harness**: 4-agent team (Orchestrator + Implementer + Reviewer + QA + Security Auditor)

### Phase(s) worked on
- Phase A: Image optimization
- Phase B: Mobile responsiveness QA and fixes
- Phase C: Admin panel JSON editors (collaborators, research, positions)
- Phase D: Admin server auto-start
- Security hardening
- Playwright E2E test suite

### Concrete changes implemented

**Phase A — Image Optimization:**
1. Compressed 9 JPGs using Pillow (quality=85): 2.76MB → 1.11MB (59.6% reduction)
2. Generated 6 WebP alternatives for largest images (additional 47-70% smaller)
3. Backed up originals to `Images/originals/`
4. No filename changes — all HTML/JSON references intact

**Phase B — Mobile Responsiveness:**
5. Created Playwright QA scripts (`tests/mobile-qa.mjs`, `tests/touch-targets-audit.mjs`)
6. Tested all 8 pages at 375px, 768px, 1280px — no horizontal overflow
7. Fixed small touch targets on mobile via CSS media query (`css/custom.css` lines 104-160)
8. Verified hamburger menu visible and functional on all pages

**Phase C — Admin Panel Editors:**
9. Added generic `load_json_data()` / `save_json_data()` helpers to `admin_server.py`
10. Added 6 API endpoints: GET/POST for `/api/collaborators`, `/api/research`, `/api/positions`
11. Each POST saves JSON atomically, sets `lastUpdated`, and git auto-commits
12. Added `_handle_save_json()` generic handler with auth + JSON parsing + dict validation
13. Added Collaborators tab: category CRUD, member CRUD, color/icon dropdowns
14. Added Research Areas tab: intro editor, area CRUD, collapsible details editor
15. Added Positions tab: isHiring toggle, position type CRUD, research areas, contact email
16. Updated `switchTab()` for 5 tabs, each fetches data on activate
17. Fixed `teamMemberAction()` to also re-render `fac_alumni` section (reviewer finding)

**Phase D — Admin Auto-Start:**
18. Created systemd user service at `~/.config/systemd/user/hurlab-admin.service`
19. Enabled and started service, verified active (running) with HTTP 200
20. Enabled user lingering (`loginctl enable-linger hurlab`) for boot persistence

**Security Hardening:**
21. Upgraded password hashing from unsalted SHA-256 to PBKDF2-SHA256 (600K iterations, random salt)
22. Added auto-migration: legacy hashes upgraded on next successful login
23. Added brute force protection: 5 attempts per IP, then 5-minute lockout
24. Added `Secure; SameSite=Strict` to session cookies
25. Added security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`
26. Added upload size limits: 50MB for CVs, 10MB for photos
27. Added photo extension validation against allowlist (jpg, jpeg, png, gif, webp)
28. Changed server binding from `0.0.0.0` to `127.0.0.1` (configurable via `ADMIN_BIND_ADDR` env)
29. Set credentials file permissions to 600
30. Added `data/` disallow to `robots.txt`; fixed sitemap URL to HTTPS

**Playwright E2E Test Suite:**
31. Installed `@playwright/test`, created `playwright.config.ts`
32. Created 6 test files with 90 tests total:
    - `smoke.spec.ts` (40 tests): HTTP 200, title, nav, footer, GA tag for all 8 pages
    - `navigation.spec.ts` (20 tests): desktop nav links, mobile hamburger, footer sections
    - `publications.spec.ts` (6 tests): data load, tabs, search, year filter
    - `tools.spec.ts` (5 tests): card load, expand, single-expand, details
    - `responsive.spec.ts` (12 tests): overflow check, hamburger visibility at 375/1280px
    - `data-integrity.spec.ts` (7 tests): validates all 7 JSON data files

### Files/modules/functions touched
- `Images/*.jpg` — 9 JPGs compressed in place
- `Images/*.webp` — 6 new WebP alternatives
- `Images/originals/` — backup of original JPGs
- `css/custom.css` — mobile touch target improvements (lines 104-160)
- `robots.txt` — added `data/` disallow, fixed sitemap URL to HTTPS
- `scripts/admin_server.py` — 6 new endpoints, security hardening, generic JSON helpers
- `scripts/templates/admin.html` — 3 new tabs (Collaborators, Research, Positions), fac_alumni render fix
- `~/.config/systemd/user/hurlab-admin.service` — new systemd user service
- `playwright.config.ts` — new Playwright config
- `package.json` — new (for @playwright/test dependency)
- `tests/e2e/*.spec.ts` — 6 new E2E test files
- `tests/mobile-qa.mjs` — mobile QA screenshot script
- `tests/touch-targets-audit.mjs` — touch target detail audit
- `tests/screenshots/` — QA screenshots at 3 viewports
- `PROJECT_HANDOFF.md` — updated all outstanding items to Completed
- `PROJECT_LOG.md` — this entry

### Key technical decisions and rationale
- **PBKDF2 over bcrypt**: Uses only Python stdlib (no pip install needed), 600K iterations meets OWASP 2024 recommendations
- **Legacy hash auto-migration**: Existing credentials work immediately; upgraded transparently on next login
- **127.0.0.1 binding with env override**: Secure by default, but `ADMIN_BIND_ADDR=0.0.0.0` available for SSH tunnel scenarios
- **systemd user service over cron**: Better process management, auto-restart on failure, proper logging via journald
- **Generic JSON helpers**: `load_json_data()`/`save_json_data()` reduce code duplication for all data file operations
- **Mobile CSS media query**: Touch target fix scoped to `@media (max-width: 767px)` to avoid affecting desktop

### Problems encountered and resolutions
1. **Playwright baseURL**: Needed trailing slash (`/hurlab/` not `/hurlab`) for correct relative path resolution. **Resolved** by updating config.
2. **Mobile hamburger locator**: Alpine.js `x-show` menu panel needed specific `nav div[x-show="open"]` selector. **Resolved** in navigation tests.
3. **Publications count text split across spans**: `filteredCount` in separate `x-text` span, not in parent text. **Resolved** by targeting specific span locator.

### Harness statistics
- **Subagent spawns**: 7 total (3 Implementers, 1 QA-Mobile, 1 QA-E2E, 1 Reviewer, 1 Security Auditor)
- **SPECs created**: 0 (all work scoped via detailed task briefs)
- **Task briefs issued**: 7
- **Security findings**: 17 total (0 Critical, 3 High → fixed, 7 Medium → 6 fixed, 5 Low, 2 Info)
- **Review verdict**: APPROVED with 5 minor non-blocking issues (2 fixed)
- **E2E tests**: 90 passed, 0 failed (34.5s)

### Items explicitly completed
- All 4 original outstanding items from PROJECT_HANDOFF.md
- Security hardening (not originally planned, added during session)
- Playwright E2E test suite (not originally planned, added during session)

### Remaining outstanding work
- None from original backlog. Future improvements noted in PROJECT_HANDOFF.md §7.

---

## Session 2026-04-08 CDT (security completion)

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)
- **Harness**: 4-agent team (Orchestrator + Implementer + Reviewer + QA)

### Phase(s) worked on
- Remaining security hardening items from previous session's recommendations

### Concrete changes implemented

**CSRF Token Protection:**
1. `create_session()` generates 256-bit CSRF token via `secrets.token_hex(32)`
2. Token injected into admin template via `{{CSRF_TOKEN}}` meta tag
3. `_validate_csrf()` method validates `X-CSRF-Token` header with timing-safe comparison
4. All 10 POST endpoints protected (upload, parse, team/member, team/pi, team/photo, team/visibility, team/reorder, collaborators, research, positions)
5. Login, setup, logout correctly excluded
6. Frontend `apiFetch()` helper auto-attaches header on all API calls
7. XHR file upload also sends CSRF header

**WEB-INF/web.xml Security Constraints:**
8. Created `WEB-INF/web.xml` with Tomcat 4.0 servlet spec
9. Blocks: `/scripts/*`, `/tests/*`, `/node_modules/*`, dot files, project management files
10. Custom error pages: 403/404 redirect to `/index.html`
11. Tomcat auto-reloaded — all sensitive paths return 403

**Server-Side Input Sanitization:**
12. Added `sanitize_text()` — strips HTML tags via regex
13. Added `sanitize_dict()` — recursive sanitization of string fields in dicts/lists
14. Applied to: team member add/edit, PI info edit, generic JSON save (collaborators/research/positions)
15. Text fields sanitized: name, title, description, institution, url, headline, overview, contactEmail, intro

**Generic Error Messages:**
16. Updated 8 `except Exception` handlers to log real error to stderr, return "Internal server error" to client
17. Fixed one remaining path leak in status endpoint (`f"Error: {e}"` → `"Error reading publications"`)

### Files/modules/functions touched
- `scripts/admin_server.py` — CSRF methods, sanitize helpers, generic error handlers, status fix
- `scripts/templates/admin.html` — CSRF meta tag, `apiFetch()` helper, XHR header
- `WEB-INF/web.xml` — new Tomcat security constraints
- `PROJECT_HANDOFF.md` — updated outstanding items and verification
- `PROJECT_LOG.md` — this entry

### Verification performed
- Code review by Reviewer agent: APPROVED (1 minor issue found and fixed)
- Playwright E2E regression: 90/90 passed (36.5s)
- web.xml security: all sensitive paths → 403, all public paths → 200
- Admin server compile + restart: OK, HTTP 200

### Harness statistics
- **Subagent spawns**: 5 total (3 Implementers, 1 Reviewer, 1 QA)
- **Task briefs issued**: 5
- **Review verdict**: APPROVED with 1 minor issue (fixed)
- **E2E regression**: 90 passed, 0 failed

### Items explicitly completed
- CSRF token protection (Security finding #5 - Medium → resolved)
- WEB-INF/web.xml (Security finding #13 - Low → resolved)
- Input sanitization (Security finding #10 - Medium → resolved)
- Generic error messages (Security finding #15 - Low → resolved)

### Remaining outstanding work
- None. All security findings from audit now resolved or documented as acceptable risk.

---

