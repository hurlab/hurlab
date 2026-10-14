# PROJECT_HANDOFF.md

## 1. Project Overview

**Purpose**: Modern, data-driven academic website for the Hur Lab (Dr. Junguk Hur, UND Biomedical Sciences). Fully redesigned from legacy HTML4 frameset site. All page content driven by JSON data files, with an admin panel for content management and a CV parser for automated publication/grant updates.

**Scope**: 9 HTML pages (8 public + 1 research detail), admin server (port 8180), CV parser script, 8 JSON data files. Deployed on Apache Tomcat 9.0.37 with nginx reverse proxy.

- **Last updated**: 2026-10-14 13:32 CDT
- **Last coding CLI used**: Claude Code CLI (Claude Opus 5.5 / Sonnet 5.5)
- **Git repo**: https://github.com/hurlab/hurlab.git (branch: main)

---

## 2. Current State

| Feature / Component | Status | Notes |
|---|---|---|
| **Core Website** | | |
| Home page (`index.html`) | Completed in Session 2026-03-14 16:30 CDT | Dynamic stats from JSON, recent pubs, funding from grants.json |
| Research page (`research.html`) | Completed in Session 2026-03-25 14:39 CDT | Data-driven, Neurological Disorders expanded (AD, PD), updated collaborators |
| Research detail pages (`research-detail.html`) | Completed in Session 2026-03-25 14:39 CDT | Per-area detail with keyword-filtered pubs, AD/PD keywords added |
| Publications page (`publications.html`) | Completed in Session 2026-03-14 16:30 CDT | CV-parsed data, 6 tabs, sort, search, year filter, PMID+PMCID+DOI badges |
| Tools page (`tools.html`) | Completed in Session 2026-10-14 13:32 CDT | 13 tools, sorted alphabetically at load; card preview-image strip + 7:3 details/images expanded view; card outline + image divider; status labels Available / Beta / Coming soon with on-page legend (one `statuses` map); optional `urlLabel` / `notice` fields. See PROJECT_LOG 2026-10-14 13:32 |
| Site-wide spacing/banner compaction, hidden grant $ amounts, Research "Previous Grants", topic-page 2-col layout | Completed in Session 2026-10-14 (earlier session 455f03ad) | Reconstructed from commits 09d9cbc..464f580; see PROJECT_LOG 2026-10-14 13:32 |
| People page (`people.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, visibility toggles, FAC sections, GitHub (Personal + Lab) |
| Positions page (`positions.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, isHiring=false, visiting scholar 6mo–3yr |
| Collaborators page (`collaborators.html`) | Completed in Session 2026-07-09 23:57 CDT | 7 sections, responsive 2-column grid, reversible hidden-member flag; see PROJECT_LOG 2026-07-09 |
| **Infrastructure** | | |
| Shared nav/footer (`js/components.js`) | Completed in Session 2026-03-25 14:39 CDT | Sakai Portal link added to footer |
| Tailwind theme (`js/theme.js`) | Completed in Session 2026-03-14 13:23 CDT | Teal/indigo palette |
| Custom CSS (`css/custom.css`) | Completed in Session 2026-03-14 13:23 CDT | Animations, card hovers, gradient text |
| **SEO** | | |
| Favicon (`favicon.svg`) | Completed in Session 2026-03-25 14:39 CDT | Teal-to-indigo H monogram with DNA dots |
| `robots.txt` | Completed in Session 2026-03-25 14:39 CDT | Allows crawling, blocks scripts/v1/cgi-bin |
| `sitemap.xml` | Completed in Session 2026-03-25 14:39 CDT | 12 URLs with priorities |
| Open Graph meta tags | Completed in Session 2026-03-25 14:39 CDT | All 8 pages |
| Twitter Card meta tags | Completed in Session 2026-03-25 14:39 CDT | index.html |
| Schema.org JSON-LD | Completed in Session 2026-03-25 14:39 CDT | ResearchOrganization on index.html |
| Google Analytics 4 | Completed in Session 2026-03-25 14:39 CDT | G-Z36JMZ1F1K on all 8 pages |
| **Data Layer (JSON-as-Database)** | | |
| `data/publications.json` | Completed in Session 2026-03-14 16:30 CDT | 170 peer-reviewed (59 with PMCID), 9 under review, 5 in prep, 34 talks, 190 posters |
| `data/grants.json` | Completed in Session 2026-03-25 14:39 CDT | 5 current with NIH Reporter/ARPA-H URLs, effort % removed |
| `data/team.json` | Completed in Session 2026-03-14 16:30 CDT | PI + current + alumni + FAC + FAC alumni + visibility settings |
| `data/tools.json` | Completed in Session 2026-10-14 13:32 CDT | 13 tools; `images: [{src, caption}]` (18 images under `Images/tools/<slug>/`); `status` ∈ available/beta/coming-soon; PubChemSR → SourceForge + "v2.0 coming soon"; ChemFuse coming-soon, no links; SciMiner renamed "SciMiner 1.1 & 2.0" (updated 2026-09-15) |
| `data/research.json` | Completed in Session 2026-05-21 CDT | 6 areas incl. Systems Pharmacology (added 2026-05-21, commit c0a907a); Neuro AD/PD |
| `data/collaborators.json` | Completed in Session 2026-07-09 23:57 CDT | 7 categories, 24 visible + 5 hidden collaborators, all with web-verified profile URLs |
| `data/positions.json` | Completed in Session 2026-03-14 16:30 CDT | isHiring=false, visiting scholar 6mo–3yr |
| `data/site.json` | Completed in Session 2026-03-14 16:30 CDT | Lab-wide config |
| **Admin Panel (port 8180)** | | |
| Admin server (`scripts/admin_server.py`) | Completed in Session 2026-05-21 CDT | Team CRUD/reorder; JSON editors (2026-04-08); TOTP 2FA login w/ QR enrollment (2026-05-21, commit c0a907a) |
| Team drag-and-drop reorder | Completed in Session 2026-03-25 14:39 CDT | Drag rows to reorder within any section |
| CV upload + symlink management | Completed in Session 2026-03-14 16:30 CDT | Saves as dated file, updates 3 symlinks |
| CV parser (`scripts/parse_cv.py`) | Completed in Session 2026-03-14 16:30 CDT | Extracts pubs (with PMCID), grants; git auto-commit |
| Team management (CRUD) | Completed in Session 2026-03-14 16:30 CDT | Current/Alumni/FAC/FAC Alumni sections |
| Section visibility toggles | Completed in Session 2026-03-14 16:30 CDT | Controls which sections show on People page |
| Photo upload for members | Completed in Session 2026-03-14 16:30 CDT | Saves to Images/team/, updates team.json |
| Dashboard status cards | Completed in Session 2026-03-14 16:30 CDT | CV info, pub counts, last updated |
| **Deployment** | | |
| v2 cutover to root | Completed in Session 2026-03-14 16:30 CDT | v2/ removed, site at root, legacy in v1/ |
| Git repository | Completed in Session 2026-03-14 16:30 CDT | github.com/hurlab/hurlab.git, auto-commit on parse |
| Directory cleanup | Completed in Session 2026-03-14 16:30 CDT | Unused dirs moved to v1/, empty Files/ and Temp/ placeholders |

---

## 3. Execution Plan Status

| Phase | Status | Last Updated | Notes |
|---|---|---|---|
| Phase 1: Foundation | Completed | 2026-03-14 13:23 CDT | |
| Phase 2: Data extraction | Completed | 2026-03-14 16:30 CDT | All content now in JSON |
| Phase 3: Content pages | Completed | 2026-03-14 16:30 CDT | All pages data-driven |
| Phase 4: Secondary pages | Completed | 2026-03-14 16:30 CDT | |
| Phase 5: Admin panel & CV automation | Completed | 2026-03-25 14:39 CDT | Full CRUD, CV parser, visibility, drag reorder |
| Phase 6: Cutover & cleanup | Completed | 2026-03-14 16:30 CDT | v2→root, directory cleanup, git init |
| Phase 7: SEO & Analytics | Completed | 2026-03-25 14:39 CDT | Favicon, sitemap, robots, OG, schema.org, GA4 |
| Phase 8: Content refinement | Completed | 2026-03-25 14:39 CDT | Research areas, collaborators, tools expandable cards |

---

## 4. Outstanding Work

| Item | Status | Last Updated | Reference |
|---|---|---|---|
| Image optimization (compress JPGs, add WebP) | Completed | 2026-04-08 CDT | 59.6% size reduction (2.76MB→1.11MB), 6 WebP alternatives, originals backed up |
| Mobile responsiveness testing | Completed | 2026-04-08 CDT | All 8 pages pass at 375px/768px/1280px, touch targets fixed |
| HTTPS fix (university firewall blocks 443) | Resolved | 2026-04-08 CDT | Port 443 opened, SSL renewed |
| Admin panel: collaborators/research/positions editors | Completed | 2026-04-08 CDT | 3 new tabs, 6 API endpoints, full CRUD with git auto-commit |
| Auto-start admin server on boot | Completed | 2026-04-08 CDT | systemd user service + lingering enabled |
| Security hardening | Completed | 2026-04-08 CDT | PBKDF2 hashing, brute force protection, cookie flags, security headers, upload limits, localhost binding |
| CSRF token protection | Completed | 2026-04-08 CDT | Per-session tokens, X-CSRF-Token header on all POST endpoints, timing-safe validation |
| WEB-INF/web.xml security constraints | Completed | 2026-04-08 CDT | Blocks scripts/, tests/, node_modules/, dot files, project files; 403 on all sensitive paths |
| Server-side input sanitization | Completed | 2026-04-08 CDT | HTML tag stripping on stored text fields, generic error messages (no path leaks) |
| Playwright E2E test suite | Completed | 2026-04-08 CDT | 90 tests across 6 spec files, all passing |
| SciMiner card version tag still reads "System migration" (stale next to new name) | Open — ask user what to show | 2026-10-14 13:32 CDT | PROJECT_LOG 2026-10-14 13:32 |
| scGEN card: add paper PMID to `publications`; figure reuse license (Advanced Science) not checked | Open | 2026-10-14 13:32 CDT | PROJECT_LOG 2026-10-14 13:32 |
| When PubChemSR 2.0 / ChemFuse go public: set `status` to `available`, drop PubChemSR `notice`, restore GitHub links | Open (waiting on release) | 2026-10-14 13:32 CDT | PROJECT_LOG 2026-10-14 13:32 |
| Remove 6 merged worktrees under `.moai/worktrees/` (site-compact, site-spacing-2, site-home-compact, site-prev-grants, site-detail-cols, site-tool-images — keep its untracked `.shots/` originals if wanted) | Open | 2026-10-14 13:32 CDT | all branches are on origin/main |
| Primary checkout `main` is behind origin/main (fast-forward only) | Open | 2026-10-14 13:32 CDT | `git pull --ff-only` when no other session is using it |
| CV data gaps: publications #95, #96, #112, #143 have no year in the CV text | Open | 2026-10-14 CDT (earlier session) | PROJECT_LOG 2026-10-14 13:32 |
| `data/grants.json` still holds dollar totals (pages no longer display them) | Open — decide whether to strip | 2026-10-14 CDT (earlier session) | PROJECT_LOG 2026-10-14 13:32 |
| `.playwright-mcp/` (browser-tool scratch) is not in `.gitignore` | Open | 2026-10-14 13:32 CDT | add below `# User Custom Patterns` at end of file |

---

## 5. Risks, Open Questions, and Assumptions

| Item | Status | Opened | Notes |
|---|---|---|---|
| HTTPS unreachable externally | Resolved | 2026-03-14 | 2026-04-08 port 443 opened/SSL renewed; RECURRED 2026-05-06/07 (iptables/ufw REDIRECT sent :443→plain-HTTP :8080), durably fixed by removing REDIRECT from both /etc/ufw/before.rules and /etc/iptables/rules.v4 (see wiki concept/hurlab-https-outage); app URLs restored to https (commit d1eb197) |
| Tailwind Play CDN first-load delay | Open | 2026-03-14 | ~200-400ms, acceptable for academic site |
| Team member photos mostly missing | Open | 2026-03-14 | Only PI and Brett McGregor have photos; admin panel supports upload |
| Admin server not auto-started | Resolved | 2026-04-08 | systemd user service enabled with lingering |
| Server holds uncommitted live edits (`data/team.json`, `Personal/JungukHur_CV.pdf`) | Open | 2026-10-14 | Untouched by all 2026-10-14 deploys (ff-only pulls). After a CV upload, the admin auto-commit stays unpushed on the server — pull it into GitHub before the next deploy (as done with a1ec5fd → 297e82b) |
| Tool status labels are set by hand | Open (by design) | 2026-10-14 | Assumption: `status` reflects visitor access (available / beta / coming-soon); nothing updates it automatically |

---

## 6. Verification Status

| Item | Method | Result | Date/Time |
|---|---|---|---|
| All pages + data files served | `curl` HTTP 200 check | All pass | 2026-03-25 14:39 CDT |
| Tools expandable cards | Manual testing by user | Working; auto-scroll, single-expand | 2026-03-25 14:39 CDT |
| Publications data | JSON inspection | 170 pubs, 59 PMCID | 2026-03-14 16:30 CDT |
| Grants data: 5 current with URLs | JSON inspection | Correct | 2026-03-25 14:39 CDT |
| Team data | JSON inspection | Current + alumni + FAC + FAC alumni | 2026-03-14 16:30 CDT |
| Admin server response time | `curl` timing | 0.001s | 2026-03-14 16:30 CDT |
| Google Analytics 4 | GA tag present on all 8 pages | G-Z36JMZ1F1K confirmed | 2026-03-25 14:39 CDT |
| SEO files | `curl` check | robots.txt, sitemap.xml, favicon.svg all 200 | 2026-03-25 14:39 CDT |
| External review (HURLAB_IMPROVEMENT_PLAN.md) | Assessed all items | Most false positives (server-side fetch without JS); genuine SEO items fixed | 2026-03-25 14:39 CDT |
| Mobile responsiveness | Playwright screenshots at 375/768/1280px | All 8 pages pass, no overflow, touch targets fixed | 2026-04-08 CDT |
| Playwright E2E test suite | `npx playwright test` (90 tests) | 90 passed, 0 failed (34.5s) | 2026-04-08 CDT |
| Security audit | Automated review by Security Auditor agent | 17 findings (0 Critical, 3 High → fixed, 7 Medium → fixed) | 2026-04-08 CDT |
| Admin panel editors | Code review by Reviewer agent | APPROVED with 5 minor non-blocking issues (2 fixed) | 2026-04-08 CDT |
| Image optimization | Before/after size comparison | 59.6% reduction, all images render correctly | 2026-04-08 CDT |
| Admin auto-start | `systemctl --user status` | active (running), linger=yes | 2026-04-08 CDT |
| CSRF protection | Code review by Reviewer agent | APPROVED — timing-safe, all POST endpoints covered | 2026-04-08 CDT |
| Input sanitization | Code review by Reviewer agent | APPROVED — HTML tag stripping, generic errors | 2026-04-08 CDT |
| WEB-INF/web.xml | `curl` HTTP status checks | scripts/→403, tests/→403, public pages→200 | 2026-04-08 CDT |
| Regression after security | `npx playwright test` (90 tests) | 90 passed, 0 failed (36.5s) | 2026-04-08 CDT |
| Collaborators reorganization | Headless Chromium render QA + live-URL curl | 7 sections, 24 visible + 5 hidden, all icons render, 0 JS errors; live HTTP 200 confirmed | 2026-07-09 23:57 CDT |
| Tools images / labels / borders / sort | Playwright (local server) at 1366 px and 390 px: image load check, label+color per card, alphabetical order, filter order; live `curl` of page, JSON, images | 18 images load, 0 page errors; 11 Available / 1 Beta / 1 Coming soon; order ChemFuse→VIOLIN; live HTTP 200, server = GitHub = c6ccbe2 | 2026-10-14 13:32 CDT |
| Not yet verified | — | Playwright E2E suite (90 tests) not re-run after the 2026-10-14 Tools/layout changes; mobile check covered Tools only | 2026-10-14 13:32 CDT |

---

## 7. Restart Instructions

**Site URL**: `https://hurlab.med.und.edu/hurlab/`
**Admin panel**: `http://localhost:8180/` (credentials in `scripts/.admin_credentials`, bound to localhost only)
**Git repo**: `https://github.com/hurlab/hurlab.git`

**Admin server management** (systemd user service, auto-starts on boot):
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
systemctl --user status hurlab-admin.service   # check status
systemctl --user restart hurlab-admin.service   # restart
systemctl --user stop hurlab-admin.service      # stop
journalctl --user -u hurlab-admin.service       # view logs
```

**Running E2E tests**:
```bash
cd /home/hurlab/apache-tomcat-9.0.37/webapps/hurlab
npx playwright test --reporter=list              # run all 90 tests
npx playwright test --reporter=html              # with HTML report
npx playwright test tests/e2e/smoke.spec.ts      # run specific suite
```

**Directory structure**:
```
hurlab/           ← webroot (Tomcat webapp)
  *.html          ← 8 public pages + research-detail.html
  css/, js/       ← styles and scripts
  data/           ← 8 JSON data files (the "database")
  Images/         ← photos (compressed JPGs + WebP alternatives)
  Personal/       ← CV PDF (symlinks)
  scripts/        ← admin_server.py, parse_cv.py, templates/
  tests/          ← Playwright E2E tests + mobile QA screenshots
  cgi-bin/        ← active Perl CGI tools
  miRNA/          ← active miRNA BLAST tools
  v1/             ← legacy site + archived directories
```

**Deployment flow** (confirmed 2026-07-09): the deployed webapp dir on hurlab.med.und.edu **is** the git working tree Tomcat serves. Deploy = commit + push to GitHub, then `ssh hurlab@hurlab.med.und.edu` → `cd .../webapps/hurlab && git pull --ff-only origin main`. Static files (HTML/JS/JSON/images) go live immediately; changes to `scripts/admin_server.py` or its templates need `systemctl --user restart hurlab-admin.service`. The server ALSO commits directly to main (admin-panel CV auto-parse + manual edits), so always `git pull --rebase` locally before pushing. Reusable method: wiki `concept/verify-person-profile-url-before-linking`.

**Worktree deploy flow used 2026-10-14**: work in a `.moai/worktrees/<name>` tree (the primary checkout is shared and behind) → commit there → re-read HEAD/branch → `git fetch` + `git rev-list --count --left-right origin/main...HEAD` (expect `0 N`) → check server HEAD over ssh → `git push origin <branch>:main` → ssh `git pull --ff-only origin main` → verify live with `curl`. No AI attribution trailers in commits (user instruction).

**Wiki**: `concept/a-public-page-is-checked-from-the-visitors-side` — check public links unauthenticated (private repos 404 for visitors); status labels by visitor access.

**Next session**: just say **"resume"** — the saved prompt in the project-root `NEXT_SESSION.md` (pointed to by the ⭐ line in Claude Code auto-memory) drives the restart.

**Recommended next actions**:
1. Clean-up: remove the 6 merged worktrees; fast-forward the primary checkout; add `.playwright-mcp/` to `.gitignore`
2. Ask the user about SciMiner's "System migration" version tag; add scGEN paper PMID
3. Re-run the Playwright E2E suite after the 2026-10-14 layout changes
4. Older carry-overs: upload team photos via admin panel; CSP header for admin panel; WebP `<picture>` elements; collaborator link follow-ups (Cui Tao → Mayo bio; Jinho Yoo http:// link)
- **Last updated**: 2026-10-14 13:32 CDT
