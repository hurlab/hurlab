# PROJECT_HANDOFF.md

## 1. Project Overview

**Purpose**: Complete redesign of the Hur Lab academic website (Dr. Junguk Hur, UND Biomedical Sciences) from a legacy HTML4 frameset site to a modern, responsive bioinformatics/AI research lab website.

**Scope**: 7-page static site with dynamic PubMed publication integration, deployed on Apache Tomcat 9.0.37. All new work lives in the `v2/` subdirectory; the legacy site is preserved at root level.

- **Last updated**: 2026-03-14 13:23 CDT
- **Last coding CLI used**: Claude Code CLI (Claude Opus 4.6)

---

## 2. Current State

| Feature / Component | Status | Notes |
|---|---|---|
| CLAUDE.md creation & update | Completed in Session 2026-03-14 13:23 CDT | Reflects both legacy and v2 architecture |
| v2/ directory structure | Completed in Session 2026-03-14 13:23 CDT | `css/`, `js/`, `data/`, `assets/images/` |
| Tailwind theme config (`js/theme.js`) | Completed in Session 2026-03-14 13:23 CDT | Teal/indigo palette, Inter + JetBrains Mono |
| Shared nav/footer (`js/components.js`) | Completed in Session 2026-03-14 13:23 CDT | IIFE injection, glassmorphism nav, mobile hamburger |
| PubMed API integration (`js/publications.js`) | Completed in Session 2026-03-14 13:23 CDT | E-utilities fetch, sessionStorage cache, PI highlighting |
| Animations (`js/animations.js`) | Completed in Session 2026-03-14 13:23 CDT | AOS init + counter animations |
| Custom CSS (`css/custom.css`) | Completed in Session 2026-03-14 13:23 CDT | Animations, card hovers, gradient text, scrollbar |
| JSON data files (tools, team, publications) | Completed in Session 2026-03-14 13:23 CDT | 9 tools, 12 team members, static pub fallback |
| Home page (`v2/index.html`) | Completed in Session 2026-03-14 13:23 CDT | Hero, research highlights, recent pubs, featured tools, funding |
| Research page (`v2/research.html`) | Completed in Session 2026-03-14 13:23 CDT | 5 research areas + funded grants |
| Publications page (`v2/publications.html`) | Completed in Session 2026-03-14 13:23 CDT | Dynamic PubMed, tabs, search, year filter |
| Tools page (`v2/tools.html`) | Completed in Session 2026-03-14 13:23 CDT | JSON-driven cards, category filter |
| People page (`v2/people.html`) | Completed in Session 2026-03-14 13:23 CDT | PI card, team grid, collapsible alumni |
| Positions page (`v2/positions.html`) | Completed in Session 2026-03-14 13:23 CDT | 3 position types, research areas |
| Collaborators page (`v2/collaborators.html`) | Completed in Session 2026-03-14 13:23 CDT | 4 categories, 17 collaborators |
| Image optimization | Not started | Existing images are unoptimized JPGs |
| SEO meta tags / Open Graph | Not started | Basic meta descriptions exist, no OG tags |
| Favicon | Not started | No favicon created yet |
| Playwright visual testing | Blocked | Chrome not available at `/opt/google/chrome/chrome` (requires root). Chromium installed at `~/.cache/ms-playwright/chromium-1208/` but Playwright MCP server hardcodes Chrome path. |
| Root-level redirect to v2/ | Not started | Awaiting user approval to make v2/ the primary site |

---

## 3. Execution Plan Status

| Phase | Status | Last Updated | Notes |
|---|---|---|---|
| Phase 1: Foundation (dirs, theme, nav/footer, home) | Completed | 2026-03-14 13:23 CDT | |
| Phase 2: Data extraction (JSON files) | Completed | 2026-03-14 13:23 CDT | |
| Phase 3: Content pages (publications, research, tools) | Completed | 2026-03-14 13:23 CDT | |
| Phase 4: Secondary pages (people, positions, collaborators) | Completed | 2026-03-14 13:23 CDT | |
| Phase 5: Polish (animations, mobile testing, SEO, images) | In progress | 2026-03-14 13:23 CDT | AOS animations done; image opt, SEO, favicon remain |
| Phase 6: Cutover (redirect root to v2/) | Not started | 2026-03-14 13:23 CDT | Needs user approval |

---

## 4. Outstanding Work

| Item | Status | Last Updated | Reference |
|---|---|---|---|
| Image optimization (compress JPGs, add WebP) | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Open Graph / Twitter Card meta tags | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Favicon (DNA helix or "H" monogram) | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Mobile responsiveness testing & fixes | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Visual testing with Playwright | Blocked | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Root index.html redirect to v2/ | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Verify PubMed API works in browser | Not started | 2026-03-14 13:23 CDT | Session 2026-03-14 13:23 CDT |
| Google Scholar profile link accuracy | Not started | 2026-03-14 13:23 CDT | publications.html uses `?user=k9PYv_EAAAAJ` — needs verification |

---

## 5. Risks, Open Questions, and Assumptions

| Item | Status | Opened | Notes |
|---|---|---|---|
| Tailwind Play CDN adds ~200-400ms processing on first load | Open | 2026-03-14 | Acceptable for academic site; could pre-compile if needed |
| PubMed CORS support for browser fetch | Open | 2026-03-14 | NCBI E-utilities should support CORS; static JSON fallback exists |
| Playwright MCP needs Chrome at `/opt/google/chrome/chrome` | Open | 2026-03-14 | Requires root to symlink; Chromium is installed but at different path |
| Google Scholar user ID (`k9PYv_EAAAAJ`) unverified | Open | 2026-03-14 | Was generated by agent; needs manual verification |
| Team member photos mostly missing | Open | 2026-03-14 | Only PI and Brett McGregor have photos; others use initials placeholders |

---

## 6. Verification Status

| Item | Method | Result | Date/Time |
|---|---|---|---|
| All 7 HTML pages served by Tomcat | `curl` HTTP status check | All return 200 | 2026-03-14 13:23 CDT |
| All 15 v2/ files exist | `find` directory listing | All present | 2026-03-14 13:23 CDT |
| Script load order (components.js before Alpine defer) | Manual code review | Correct across all pages | 2026-03-14 13:23 CDT |
| components.js IIFE execution | Code review after fix | Fixed from DOMContentLoaded to IIFE | 2026-03-14 13:23 CDT |
| Visual rendering in browser | Not verified | Playwright blocked (no Chrome) | 2026-03-14 13:23 CDT |
| PubMed API live fetch | Not verified | Requires browser test | 2026-03-14 13:23 CDT |
| Mobile responsiveness | Not verified | Requires browser test | 2026-03-14 13:23 CDT |

---

## 7. Restart Instructions

**Starting point**: All v2/ pages are built and served. The site is accessible at `http://localhost:8080/hurlab/v2/`.

**Recommended next actions** (in priority order):
1. **Fix Playwright**: Either get root access to symlink Chrome, or configure the Playwright MCP server to use `~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome`. Then take screenshots of all pages for visual QA.
2. **Browser-test PubMed API**: Navigate to `v2/publications.html` and verify the live PubMed fetch works (check console for errors).
3. **Verify Google Scholar link**: Confirm `k9PYv_EAAAAJ` is Dr. Hur's actual Google Scholar ID.
4. **Image optimization**: Compress `Images/Junguk-3.jpg` and `Images/mcgregor_brett.jpg`.
5. **Add favicon**: Create a simple SVG favicon.
6. **Add Open Graph meta tags** for social sharing previews.
7. **Mobile testing**: Test all pages at 375px and 768px widths.
8. **Cutover**: When approved, update root `index.html` to redirect to `v2/index.html`.

- **Last updated**: 2026-03-14 13:23 CDT
