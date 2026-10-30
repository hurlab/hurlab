# PROJECT_HANDOFF.md

## 1. Project Overview

**Purpose**: Modern, data-driven academic website for the Hur Lab (Dr. Junguk Hur, UND Biomedical Sciences). Fully redesigned from legacy HTML4 frameset site. All page content driven by JSON data files, with an admin panel for content management and a CV parser for automated publication/grant updates.

**Scope**: 9 HTML pages (8 public + 1 research detail), admin server (port 8180), CV parser script, 8 JSON data files. Deployed on Apache Tomcat 9.0.37 with nginx reverse proxy.

- **Last updated**: 2026-10-29 22:44 CDT
- **Last coding CLI used**: Claude Code CLI (Claude Opus 5.5 / Sonnet 5.5)
- **Git repo**: https://github.com/hurlab/hurlab.git (branch: main)

---

## 2. Current State

| Feature / Component | Status | Notes |
|---|---|---|
| **Core Website** | | |
| Home page (`index.html`) | Completed in Session 2026-10-14 16:11 CDT | Recent Publications = auto-scrolling strip of the newest N published papers (N and author-shorten threshold from `data/site.json` homePage, admin "Home Page" tab; long author lists shortened to first 3 … Hur J … last); Featured Tools = auto-scrolling strip of all tools from tools.json; both pause on mouse hover (mouse devices only), the button, or keyboard focus; hero fits its content; compact research cards. Marquee CSS is inline in index.html on purpose. See PROJECT_LOG 2026-10-14 16:11 |
| Research page (`research.html`) | Completed in Session 2026-03-25 14:39 CDT | Data-driven, Neurological Disorders expanded (AD, PD), updated collaborators |
| Research detail pages (`research-detail.html`) | Completed in Session 2026-03-25 14:39 CDT | Per-area detail with keyword-filtered pubs, AD/PD keywords added |
| Publications page (`publications.html`) | Completed in Session 2026-10-14 16:11 CDT | `*`/`$` author markers as superscripts, journal names bold-italic (177 of 181 found; shared `js/citations.js`); Presentations tab = "Poster & Oral Abstracts", newest first, Oral/Poster badge, `*`/`$` legend; poster parse bug fixed in `scripts/parse_cv.py` (layout-mode text) |
| Tools page (`tools.html`) | Completed in Session 2026-10-14 16:11 CDT | 20 tools sorted A–Z at load; filters All/Knowledgebase/Web Tool/Research Support/R Package/R Shiny/Python/Desktop (Desktop is empty); a second click on the active filter returns to All; category may be a list (Tox21 Enricher, DNMKB2); preview strip + 7:3 expanded view; card outline; status labels Available/Beta/Coming soon + legend; optional `urlLabel`/`notice`. See PROJECT_LOG 2026-10-14 13:32 and 16:11 |
| Site-wide spacing/banner compaction, hidden grant $ amounts, Research "Previous Grants", topic-page 2-col layout | Completed in Session 2026-10-14 (earlier session 455f03ad) | Reconstructed from commits 09d9cbc..464f580; see PROJECT_LOG 2026-10-14 13:32 |
| People page (`people.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, visibility toggles, FAC sections, GitHub (Personal + Lab) |
| Positions page (`positions.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, isHiring=false, visiting scholar 6mo–3yr |
| Collaborators page (`collaborators.html`) | Completed in Session 2026-07-09 23:57 CDT | 7 sections, responsive 2-column grid, reversible hidden-member flag; see PROJECT_LOG 2026-07-09 |
| **Infrastructure** | | |
| Shared nav/footer (`js/components.js`) | Completed in Session 2026-03-25 14:39 CDT | Sakai Portal link added to footer; footer lists the CDAC/RDCD roles + "Also affiliated with" (U. Michigan adjunct, VA Fargo WOC) and an automatic per-page "Last updated" (newest server Last-Modified of the page and its data files), 2026-10-14 |
| Tailwind theme (`js/theme.js`) | Completed in Session 2026-03-14 13:23 CDT | Teal/indigo palette |
| Custom CSS (`css/custom.css`) | Completed in Session 2026-03-14 13:23 CDT | Animations, card hovers, gradient text |
| Legacy Entrez ID/Symbol converter (server-side, NOT in git) | Completed in Session 2026-10-29 22:44 CDT (work done on the server 2026-10-15) | Revived at `https://hurlab.med.und.edu/cgi-bin/SciMiner/annotation.cgi`; old `/SciMiner/annotation.cgi` returns 301 to it, so the SMHS link works unchanged. Script cut down (MiMI removed, input whitelisted/capped, output HTML-escaped, red "Annotation is outdated" banner). Details in "Server-side changes outside git" below. See PROJECT_LOG 2026-10-29 22:44 |
| Legacy sequence tools (LOD Score, Pairwise Protein Alignment, Simple Sequence Alignment, Sequence Fitting, Repeat Finder) | Decided: stay closed, not listed | 2026-10-29 22:44 CDT | nginx 403 on `/cgi-bin/`; user decision 2026-10-15. Code reading showed `system()` command injection and a user-input file written into the executed CGI dir. Handled on the SMHS side as part of the approved SMHS refresh |
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
| `data/tools.json` | Completed in Session 2026-10-14 16:11 CDT | 20 tools (7 added this evening: Vignet + 6 research-support apps); `images`, `status` (available/beta/coming-soon), `category` string or list, `urlLabel`, `notice`; DNMKB2 "Replaced by DPNKB" and Web Tool + Knowledgebase; DPNKB described as its revamped successor (updated 2026-06-08) |
| `data/research.json` | Completed in Session 2026-05-21 CDT | 6 areas incl. Systems Pharmacology (added 2026-05-21, commit c0a907a); Neuro AD/PD |
| `data/collaborators.json` | Completed in Session 2026-07-09 23:57 CDT | 7 categories, 24 visible + 5 hidden collaborators, all with web-verified profile URLs |
| `data/positions.json` | Completed in Session 2026-03-14 16:30 CDT | isHiring=false, visiting scholar 6mo–3yr |
| `data/site.json` | Completed in Session 2026-10-14 16:11 CDT | Lab-wide config + `homePage` {recentPublicationsCount: 10, authorShortenThreshold: 10}, editable in the admin Home Page tab |
| **Admin Panel (port 8180)** | | |
| Admin server (`scripts/admin_server.py`) | Completed in Session 2026-10-14 16:11 CDT | Team CRUD/reorder; JSON editors (2026-04-08); TOTP 2FA login w/ QR enrollment (2026-05-21, commit c0a907a); Home Page tab + `/api/home-settings` (auth + CSRF, ranges validated), 2026-10-14 |
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
| Remove 6 merged worktrees under `.moai/worktrees/` | Completed | 2026-10-14 17:00 CDT | All six were verified merged into origin/main with no tracked changes and removed (their untracked `.codex/` and the original `.shots/` screenshots went with them; resized images are committed). The six local `WT-*` branches still exist — delete with `git branch -d` after user OK (branch change in the shared checkout) |
| Primary checkout `main` is behind origin/main (12 commits) | Completed | 2026-10-29 22:44 CDT | Checked first: local HEAD was an ancestor of origin/main, 0 local-only commits, no overlap with the local uncommitted `.moai/` files; `git pull --ff-only` → HEAD = origin/main = f4a2f9b (`0 0`) |
| SMHS site pages (`med.und.edu/research/labs/hur/`) refreshed from the lab site via the Claude-desktop 2-phase prompt | Completed | 2026-10-29 22:44 CDT | User confirmed 2026-10-29: all changes from that work were approved — no further action |
| SMHS Tools page links (PubChemSR SourceForge 403 to curl) | Superseded | 2026-10-29 22:44 CDT | Covered by the approved SMHS refresh; user said no further SMHS follow-up is needed |
| Converter page look (external CSS/JS removed from the CGI) never viewed in a real browser | Open | 2026-10-29 22:44 CDT | Open `https://hurlab.med.und.edu/cgi-bin/SciMiner/annotation.cgi`; ask the user if fonts/colors look off |
| Local `WT-*` branches: 7 now (handoff said 6) | Open — ask before deleting | 2026-10-29 22:44 CDT | `git branch --list 'WT-*'`; branch change in the shared checkout needs user OK |
| Uncommitted local `.moai/harness/usage-log.jsonl`, `.moai/lessons-inbox.jsonl` (+ untracked `.moai/logs/`, `.moai/reports/`) | Open — harness bookkeeping, left alone | 2026-10-29 22:44 CDT | Last committed as f3897dd; stage by explicit pathspec if committing |
| CV data gaps: publications #95, #96, #112, #143 have no year in the CV text | Open | 2026-10-14 CDT (earlier session) | PROJECT_LOG 2026-10-14 13:32 |
| `data/grants.json` still holds dollar totals (pages no longer display them) | Open — decide whether to strip | 2026-10-14 CDT (earlier session) | PROJECT_LOG 2026-10-14 13:32 |
| `.playwright-mcp/` (browser-tool scratch) is not in `.gitignore` | Open | 2026-10-14 13:32 CDT | add below `# User Custom Patterns` at end of file |
| HTTP caching: Tomcat sends no Cache-Control/Expires, so browsers can keep stale HTML/CSS/JS (a hard refresh is needed after deploys). Offered: ExpiresFilter in WEB-INF/web.xml + version tags on css/js links + no-cache on data fetches | Open — user has not chosen | 2026-10-14 16:11 CDT | PROJECT_LOG 2026-10-14 16:11 |
| Four citations get no bold-italic journal (CV punctuation): #47 "Bai J.P.F.,", #113 consortium author, #135/#136 comma-separated format | Open — fix the CV entries or accept | 2026-10-14 16:11 CDT | PROJECT_LOG 2026-10-14 16:11 |
| Poster list cannot show the CV's bold lab-member names (plain text extraction drops formatting; would need font info from the PDF) | Open — optional | 2026-10-14 16:11 CDT | PROJECT_LOG 2026-10-14 16:11 |
| "Desktop" filter on the Tools page matches no tool | Open — remove the button or tag a tool | 2026-10-14 16:11 CDT | PROJECT_LOG 2026-10-14 16:11 |
| DPNKB card still has placeholder version "Latest"; its 2026-06-08 date is the last feature commit in ~/PROJECTS/10_apps/dpnkb (server copy has no git history to confirm) | Open | 2026-10-14 16:11 CDT | PROJECT_LOG 2026-10-14 16:11 |

---

## 5. Risks, Open Questions, and Assumptions

| Item | Status | Opened | Notes |
|---|---|---|---|
| HTTPS unreachable externally | Resolved | 2026-03-14 | 2026-04-08 port 443 opened/SSL renewed; RECURRED 2026-05-06/07 (iptables/ufw REDIRECT sent :443→plain-HTTP :8080), durably fixed by removing REDIRECT from both /etc/ufw/before.rules and /etc/iptables/rules.v4 (see wiki concept/hurlab-https-outage); app URLs restored to https (commit d1eb197) |
| Tailwind Play CDN first-load delay | Open | 2026-03-14 | ~200-400ms, acceptable for academic site |
| Team member photos mostly missing | Open | 2026-03-14 | Only PI and Brett McGregor have photos; admin panel supports upload |
| Admin server not auto-started | Resolved | 2026-04-08 | systemd user service enabled with lingering |
| Server holds uncommitted live edits (`data/team.json`, `Personal/JungukHur_CV.pdf`) | Open | 2026-10-14 | Untouched by all 2026-10-14 deploys (ff-only pulls). After a CV upload, the admin auto-commit stays unpushed on the server — pull it into GitHub before the next deploy (as done with a1ec5fd → 297e82b) |
| Admin "Home Page" tab not exercised by a logged-in user | Open | 2026-10-14 | Handler unit-tested (9 cases) and unauthenticated GET/POST return 401 on the server; the form itself has not been tried (login needs the PI's 2FA code). Saving commits on the server and that commit stays unpushed, like CV uploads — pull it into GitHub before the next deploy |
| Tool status labels are set by hand | Open (by design) | 2026-10-14 | Assumption: `status` reflects visitor access (available / beta / coming-soon); nothing updates it automatically |
| Server changes made outside git (nginx conf block, converter CGI, helper script, backups) are not version-controlled | Open — documented only here | 2026-10-15 | If nginx config is regenerated or the box is rebuilt, the block `# ... entrez` after `# END dnmkb2-cgi-allow` and the cut-down `annotation.cgi` must be re-applied: run `/home/hurlab/enable-entrez-id2symbol.sh` (has `--dry-run` / `--revert`). See §7 "Server-side changes outside git" |
| Legacy sequence-tool CGIs still exist on disk under `webapps/ROOT/WEB-INF/cgi/` and answer on Tomcat localhost:8081 | Open (mitigated by nginx 403) | 2026-10-15 | Not exposed externally. Anyone loosening the `/cgi-bin/` deny rule would expose command-injection code. Consider deleting or moving them out of the CGI dir (user has not asked) |

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
| Poster parser fix | Regenerated from the live CV into a scratch dir and diffed against the live JSON; ran the parser read-only on the server | 89 posters, 0 empty, 0 without year, 23 oral; only posters + #177 + under-review #4 changed; grants identical | 2026-10-14 15:30 CDT |
| Home strips, hover pause, footer date, home compaction, citation formatting | Playwright on a local server and on the live site (cache cleared): movement px/2 s, hover/leave, reduced-motion, page heights, journal/superscript counts | Strips move (≈135 px/2 s) and pause on hover; home page 3,558 → 3,119 px; 159/164 peer-reviewed cards show a bold-italic journal; 0 console errors | 2026-10-14 16:05 CDT |
| Entrez converter revival (first verified 2026-10-15 from this machine) | `curl` against the public URLs; conversions 7157→TP53 "tumor protein p53", 672→BRCA1, Trp53→22059; SQL-/XSS-shaped input; neighbour paths | New URL 200 + warning present + no MiMI; old https URL 301 → new; SMHS `http://…/SciMiner/annotation.cgi` ends at 200 after 2 redirects; injection input: no errors, XSS input not echoed raw; still closed: other SciMiner CGI (302), `wz_tooltip.js` (302), `annotation.cgi.backup` (302), 5 sequence tools (403), `/hurlab/cgi-bin/WebTools/` (404), `/SciMiner/index.cgi` (403); hurlab / SciMiner1.1 / DNMKB 200. Server: block present once, conf 761 lines, CGI sha256 `15b6776a…` | 2026-10-15 |
| Same, re-checked today (status codes only) | `curl -s -o /dev/null -w` on the public URLs | converter 200 with "outdated" banner; old URL 301 → new; `/cgi-bin/SeqAlign/` and `/cgi-bin/RepeatFinder/` 403; `/hurlab/` and `tools.html` 200; `js/citations.js` 200. Conversions and the other neighbour paths were NOT re-run | 2026-10-29 22:44 CDT |
| Primary checkout sync | `git fetch`; `git rev-list --count --left-right origin/main...HEAD` before and after `git pull --ff-only` | before `12 0` (0 local-only commits, no overlap with local changes); after `0 0`, HEAD f4a2f9b | 2026-10-29 22:44 CDT |
| Not yet verified | — | Playwright E2E suite (90 tests) not re-run after the 2026-10-14 changes; admin Home Page form not tried logged in; mobile check covered Tools only (home strips checked at 1366 px and in reduced-motion mode, not at phone width) | 2026-10-14 16:11 CDT |

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

**Wiki**: `concept/pdftotext-reading-order-detaches-list-numbers-from-their-entries` (numbered-list parsing) · `concept/a-public-page-is-checked-from-the-visitors-side` — check public links unauthenticated (private repos 404 for visitors); status labels by visitor access.

**Server-side changes outside git (done 2026-10-15; the agent has no sudo, the user ran the nginx step)**:
- `annotation.cgi` (the real script) is `/home/hurlab/apache-tomcat-9.0.37/webapps/ROOT/WEB-INF/cgi/SciMiner/annotation.cgi`; sha256 `15b6776a3ada558acb4efc15e1a76c6e8ae71730164b6f6947ca7d98fa627f13`. The original is backed up at `/home/hurlab/backups/annotation-cgi-20261015/annotation.cgi.orig` (sha256 `90d97d74…c29c23`), deliberately outside the CGI dir. The old 98-byte stub `webapps/SciMiner/annotation.cgi` (redirects to `/cgi-bin/SciMiner/annotation.cgi`) and `annotation.cgi.backup` (2020) were left untouched.
- nginx: `/etc/nginx/sites-available/hurlab.med.und.edu.conf` (443 server block) got a 17-line block after `# END dnmkb2-cgi-allow`: `location = /cgi-bin/SciMiner/annotation.cgi` (proxy to localhost:8081, `client_max_body_size 1m`) and `location = /SciMiner/annotation.cgi { return 301 https://hurlab.med.und.edu/cgi-bin/SciMiner/annotation.cgi; }`. Config went from 744 to 761 lines. Backup: `hurlab.med.und.edu.conf.bak-20261015_111423-entrez` (same directory).
- Helper: `/home/hurlab/enable-entrez-id2symbol.sh` (`--dry-run`, `--revert`; checks the CGI sha, line-count guard, `nginx -t` with auto-restore, reload, 7 checks).
- Local working copies of the converter are in that session's scratchpad only (gone); the server copy and the backup are the sources of truth.
- Wiki: `concept/a-legacy-cgi-is-reopened-one-script-at-a-time`.

**Next session**: just say **"resume"** — the saved prompt in the project-root `NEXT_SESSION.md` (pointed to by the ⭐ line in Claude Code auto-memory) drives the restart.

**Recommended next actions**:
1. Clean-up: delete the 7 leftover local `WT-*` branches (ask first); add `.playwright-mcp/` to `.gitignore` (below `# User Custom Patterns`, at the end) — primary checkout is already fast-forwarded (2026-10-29)
2. Ask the user: HTTP caching fix (yes/no), SciMiner's "System migration" version tag, the empty Desktop filter; add scGEN paper PMID
3. Browser spot-check by the user: the converter page look
4. Re-run the Playwright E2E suite after the 2026-10-14 changes; try the admin Home Page tab logged in
5. Older carry-overs: upload team photos via admin panel; CSP header for admin panel; WebP `<picture>` elements; collaborator link follow-ups (Cui Tao → Mayo bio; Jinho Yoo http:// link)
- **Last updated**: 2026-10-29 22:44 CDT
