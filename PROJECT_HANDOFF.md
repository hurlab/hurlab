# PROJECT_HANDOFF.md

## 1. Project Overview

**Purpose**: Modern, data-driven academic website for the Hur Lab (Dr. Junguk Hur, UND Biomedical Sciences). Fully redesigned from legacy HTML4 frameset site. All page content driven by JSON data files, with an admin panel for content management and a CV parser for automated publication/grant updates.

**Scope**: 9 HTML pages (8 public + 1 research detail), admin server (port 8180), CV parser script, 8 JSON data files. Deployed on Apache Tomcat 9.0.37 with nginx reverse proxy.

- **Last updated**: 2026-03-14 16:30 CDT
- **Last coding CLI used**: Claude Code CLI (Claude Opus 4.6)
- **Git repo**: https://github.com/hurlab/hurlab.git (branch: main)

---

## 2. Current State

| Feature / Component | Status | Notes |
|---|---|---|
| **Core Website** | | |
| Home page (`index.html`) | Completed in Session 2026-03-14 16:30 CDT | Dynamic stats from JSON, recent pubs, funding from grants.json |
| Research page (`research.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven from research.json + grants.json, "Learn more" links to detail pages |
| Research detail pages (`research-detail.html`) | Completed in Session 2026-03-14 16:30 CDT | Per-area detail with keyword-filtered publications, `?area=0-4` |
| Publications page (`publications.html`) | Completed in Session 2026-03-14 16:30 CDT | CV-parsed data, 6 tabs, sort (newest/oldest/CV), search, year filter, PMID+PMCID+DOI badges |
| Tools page (`tools.html`) | Completed in Session 2026-03-14 16:30 CDT | JSON-driven, category filter incl. R Shiny |
| People page (`people.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven, visibility toggles, FAC sections, GitHub (Personal + Lab) |
| Positions page (`positions.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven from positions.json, isHiring flag, "Future Openings" mode |
| Collaborators page (`collaborators.html`) | Completed in Session 2026-03-14 16:30 CDT | Data-driven from collaborators.json, all URLs updated |
| **Infrastructure** | | |
| Shared nav/footer (`js/components.js`) | Completed in Session 2026-03-14 16:30 CDT | IIFE, glassmorphism, admin link in footer, correct phone/email |
| Tailwind theme (`js/theme.js`) | Completed in Session 2026-03-14 13:23 CDT | Teal/indigo palette |
| Custom CSS (`css/custom.css`) | Completed in Session 2026-03-14 13:23 CDT | Animations, card hovers, gradient text |
| **Data Layer (JSON-as-Database)** | | |
| `data/publications.json` | Completed in Session 2026-03-14 16:30 CDT | 170 peer-reviewed (59 with PMCID), 9 under review, 5 in prep, 34 talks, 190 posters |
| `data/grants.json` | Completed in Session 2026-03-14 16:30 CDT | 5 current (with NIH Reporter/ARPA-H URLs), 12 pending, 18 previous. No effort % shown. |
| `data/team.json` | Completed in Session 2026-03-14 16:30 CDT | PI + 8 current + 17 alumni + 9 FAC + 10 FAC alumni + visibility settings |
| `data/tools.json` | Completed in Session 2026-03-14 13:23 CDT | 9 tools |
| `data/research.json` | Completed in Session 2026-03-14 16:30 CDT | 5 areas with details, keywords, collaborators |
| `data/collaborators.json` | Completed in Session 2026-03-14 16:30 CDT | 4 categories, 14 collaborators, all URLs updated |
| `data/positions.json` | Completed in Session 2026-03-14 16:30 CDT | isHiring=false, 3 position types |
| `data/site.json` | Completed in Session 2026-03-14 16:30 CDT | Lab-wide config |
| **Admin Panel (port 8180)** | | |
| Admin server (`scripts/admin_server.py`) | Completed in Session 2026-03-14 16:30 CDT | Python 3.12, no DNS delay, session auth |
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
| **Not Started** | | |
| Image optimization | Not started | PI and member photos are unoptimized JPGs |
| Open Graph / Twitter Card meta tags | Not started | For social sharing previews |
| Favicon | Not started | No favicon yet |
| Mobile responsiveness testing | Not started | Designed responsive but not formally tested |
| HTTPS | Blocked | University network blocks port 443 externally; nginx SSL configured but unreachable from outside |

---

## 3. Execution Plan Status

| Phase | Status | Last Updated | Notes |
|---|---|---|---|
| Phase 1: Foundation | Completed | 2026-03-14 13:23 CDT | |
| Phase 2: Data extraction | Completed | 2026-03-14 16:30 CDT | All content now in JSON |
| Phase 3: Content pages | Completed | 2026-03-14 16:30 CDT | All pages data-driven |
| Phase 4: Secondary pages | Completed | 2026-03-14 16:30 CDT | |
| Phase 5: Admin panel & CV automation | Completed | 2026-03-14 16:30 CDT | Full CRUD, CV parser, visibility toggles |
| Phase 6: Cutover & cleanup | Completed | 2026-03-14 16:30 CDT | v2→root, directory cleanup, git init |
| Phase 7: Polish (SEO, images, favicon) | Not started | 2026-03-14 16:30 CDT | |

---

## 4. Outstanding Work

| Item | Status | Last Updated | Reference |
|---|---|---|---|
| Image optimization (compress JPGs, add WebP) | Not started | 2026-03-14 16:30 CDT | Session 2026-03-14 16:30 CDT |
| Open Graph / Twitter Card meta tags | Not started | 2026-03-14 16:30 CDT | Session 2026-03-14 16:30 CDT |
| Favicon | Not started | 2026-03-14 16:30 CDT | Session 2026-03-14 16:30 CDT |
| Mobile responsiveness testing | Not started | 2026-03-14 16:30 CDT | Session 2026-03-14 16:30 CDT |
| HTTPS fix (university firewall blocks 443) | Blocked | 2026-03-14 16:30 CDT | Session 2026-03-14 16:30 CDT |
| Admin panel: collaborators/research/positions editors | Not started | 2026-03-14 16:30 CDT | Could add more admin tabs for editing these JSON files |
| Auto-start admin server on boot | Not started | 2026-03-14 16:30 CDT | Currently manual: `bash scripts/start_admin.sh` |

---

## 5. Risks, Open Questions, and Assumptions

| Item | Status | Opened | Notes |
|---|---|---|---|
| HTTPS unreachable externally | Open | 2026-03-14 | University firewall blocks port 443 from outside. Let's Encrypt also failed (port 80 blocked from internet). Contact UND IT. Site works via HTTP. |
| Tailwind Play CDN first-load delay | Open | 2026-03-14 | ~200-400ms, acceptable for academic site |
| Team member photos mostly missing | Open | 2026-03-14 | Only PI and Brett McGregor have photos; admin panel supports photo upload |
| Admin server not auto-started | Open | 2026-03-14 | Needs systemd service or cron @reboot entry |

---

## 6. Verification Status

| Item | Method | Result | Date/Time |
|---|---|---|---|
| All 8 HTML pages + data files served | `curl` HTTP 200 check | All pass | 2026-03-14 16:30 CDT |
| Publications data: 170 pubs, 59 with PMCID | Python JSON inspection | Correct | 2026-03-14 16:30 CDT |
| Grants data: 5 current with URLs | JSON inspection | Correct | 2026-03-14 16:30 CDT |
| Team data: 8 current, 17 alumni, 9 FAC, 10 FAC alumni | JSON inspection | Correct | 2026-03-14 16:30 CDT |
| Admin server response time | `curl` timing | 0.001s (was 56s before DNS fix) | 2026-03-14 16:30 CDT |
| CV parser full run | CLI execution | 170 pubs, 35 grants, git auto-commit | 2026-03-14 16:30 CDT |
| Google Scholar link | User-provided correction | Fixed to `Iug5mCsAAAAJ` | 2026-03-14 16:30 CDT |
| Script load order | Code audit by agents | Correct across all pages | 2026-03-14 16:30 CDT |
| Publication sort/filter/tabs | Code audit | Fixed: preprints in "all" tab, year reset on tab switch | 2026-03-14 16:30 CDT |
| Mobile responsiveness | Not verified | Not formally tested | 2026-03-14 16:30 CDT |
| Visual rendering | Not verified | Playwright blocked | 2026-03-14 16:30 CDT |

---

## 7. Restart Instructions

**Site URL**: `http://hurlab.med.und.edu/hurlab/`
**Admin panel**: `http://hurlab.med.und.edu:8180/` (credentials in `scripts/.admin_credentials`)
**Git repo**: `https://github.com/hurlab/hurlab.git`

**Starting the admin server** (if not running):
```bash
cd /home/hurlab/apache-tomcat-9.0.37/webapps/hurlab/scripts
bash start_admin.sh
```

**Directory structure**:
```
hurlab/           ← webroot (Tomcat webapp)
  *.html          ← 8 public pages + research-detail.html
  css/, js/       ← styles and scripts
  data/           ← 8 JSON data files (the "database")
  Images/         ← photos
  Personal/       ← CV PDF (symlinks)
  scripts/        ← admin_server.py, parse_cv.py, templates/
  cgi-bin/        ← active Perl CGI tools
  miRNA/          ← active miRNA BLAST tools
  v1/             ← legacy site + archived directories
```

**Recommended next actions**:
1. Add admin panel tabs for editing collaborators, research areas, and positions JSON
2. Image optimization (compress existing JPGs)
3. Add favicon
4. Add Open Graph meta tags
5. Set up admin server auto-start (systemd or cron)
6. Contact UND IT about HTTPS/port 443

- **Last updated**: 2026-03-14 16:30 CDT
