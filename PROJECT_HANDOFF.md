# PROJECT_HANDOFF.md

## 1. Project Overview

**Purpose**: Modern, data-driven academic website for the Hur Lab (Dr. Junguk Hur, UND Biomedical Sciences). Fully redesigned from legacy HTML4 frameset site. All page content driven by JSON data files, with an admin panel for content management and a CV parser for automated publication/grant updates.

**Scope**: 9 HTML pages (8 public + 1 research detail), admin server (port 8180), CV parser script, 8 JSON data files. Deployed on Apache Tomcat 9.0.37 with nginx reverse proxy.

- **Last updated**: 2026-04-08 CDT
- **Last coding CLI used**: Claude Code CLI (Claude Opus 4.6)
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
| Tools page (`tools.html`) | Completed in Session 2026-03-25 14:39 CDT | 11 tools (added VIOLIN, Ignet), expandable detail cards, single-expand, auto-scroll |
| People page (`people.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, visibility toggles, FAC sections, GitHub (Personal + Lab) |
| Positions page (`positions.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, isHiring=false, visiting scholar 6mo–3yr |
| Collaborators page (`collaborators.html`) | Completed in Session 2026-03-25 14:39 CDT | Updated: Lyssenko added, Brosius→U Arizona, Lee→Korean NRC |
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
| `data/tools.json` | Completed in Session 2026-03-25 14:39 CDT | 11 tools with expandable details (longDescription, features, publications, relatedAreas) |
| `data/research.json` | Completed in Session 2026-03-25 14:39 CDT | 5 areas; Neuro expanded (AD/PD), AI collab updated, Ontology collab updated |
| `data/collaborators.json` | Completed in Session 2026-03-25 14:39 CDT | 4 categories, 15 collaborators, Lyssenko added |
| `data/positions.json` | Completed in Session 2026-03-14 16:30 CDT | isHiring=false, visiting scholar 6mo–3yr |
| `data/site.json` | Completed in Session 2026-03-14 16:30 CDT | Lab-wide config |
| **Admin Panel (port 8180)** | | |
| Admin server (`scripts/admin_server.py`) | Completed in Session 2026-03-25 14:39 CDT | Team reorder endpoint added |
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

---

## 5. Risks, Open Questions, and Assumptions

| Item | Status | Opened | Notes |
|---|---|---|---|
| HTTPS unreachable externally | Resolved | 2026-03-14 | Resolved 2026-04-08: port 443 opened, SSL certificate renewed |
| Tailwind Play CDN first-load delay | Open | 2026-03-14 | ~200-400ms, acceptable for academic site |
| Team member photos mostly missing | Open | 2026-03-14 | Only PI and Brett McGregor have photos; admin panel supports upload |
| Admin server not auto-started | Resolved | 2026-04-08 | systemd user service enabled with lingering |

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

**Recommended next actions** (all outstanding items and security findings are resolved):
1. Upload team member photos via admin panel (most still missing)
2. Monitor GA4 dashboard for traffic data
3. Consider Content-Security-Policy header for the admin panel (currently uses Tailwind CDN which requires unsafe-inline)
4. Consider adding WebP `<picture>` elements to HTML for browsers that support it
- **Last updated**: 2026-04-08 CDT
