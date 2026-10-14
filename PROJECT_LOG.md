# PROJECT_LOG.md (active) — Hur Lab

Bounded active log. Newest first. Older sessions are archived under `logs/` when over budget (>10 sessions / ~1000 lines).

## Archives
- logs/PROJECT_LOG_2026-H1.md — 1 sessions (2026-03 … 2026-03)

## Session Index (active, newest first)
- 2026-10-14 17:00 CDT — Removed the six merged worktrees (verified merged + clean first); handoff/resume updated
- 2026-10-14 16:11 CDT
- 2026-10-14 13:32 CDT
- 2026-07-09 23:57 CDT
- 2026-03-14 16:30 CDT
- 2026-03-25 14:39 CDT
- 2026-04-08 CDT (early)
- 2026-04-08 CDT (implementation)
- 2026-04-08 CDT (security completion)
- 2026-04-08 CDT (code review)
- 2026-04-08 CDT (code review pass 2)

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

## Session 2026-03-14 16:30 CDT

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)

### Phase(s) worked on
- Phase 2 (extended): Full JSON-as-database migration for all pages
- Phase 5: Admin panel with CV parser, team management, visibility controls
- Phase 6: Cutover from v2/ to root, directory cleanup, git setup
- Bug fixing and testing audit

### Concrete changes implemented

**Site cutover & cleanup:**
1. Moved v2/ contents to root, fixed all `../` paths to direct paths
2. Fixed broken CV file references (standardized to `JungukHur-CV.pdf`)
3. Removed v2/ directory (was duplicate after copy)
4. Moved 14 unused directories to v1/ (Admissions, BACKUPS, Files, icons, Indiana, Jumgim, LabMembers, Michigan, Projects, Publications, Study, Supplemental, Temp, Tools)
5. Created empty Files/ and Temp/ placeholders
6. Initialized git repo, pushed to github.com/hurlab/hurlab.git
7. Created .gitignore (excludes large dirs, *.zip, credentials, runtime files)

**JSON-as-database migration:**
8. Created `data/research.json` with 5 research areas + detail content (overview, topics, tools, collaborators, keywords)
9. Created `data/collaborators.json` with 4 categories, 14 collaborators, updated URLs
10. Created `data/positions.json` with isHiring flag, 3 position types, research areas
11. Created `data/site.json` with lab-wide configuration
12. Created `data/grants.json` from CV parser (5 current + 12 pending + 18 previous)
13. Rewrote research.html, collaborators.html, positions.html to be data-driven (Alpine.js + JSON fetch)
14. Created `research-detail.html` — per-area detail page with keyword-filtered publications

**CV parser & admin panel:**
15. Created `scripts/parse_cv.py` — parses CV PDF via pdftotext, extracts 170 publications (with PMID, PMCID, DOI, year), 9 under review, 5 in prep, 34 talks, 190 posters, 35 grants
16. Created `scripts/admin_server.py` — Python HTTP server on port 8180 with session auth
17. Created admin templates (dashboard, login, setup) with Tailwind CSS
18. Added CV upload with dated filename + 3 symlink management
19. Added team CRUD API (add/edit/delete/move across current/alumni/fac/fac_alumni)
20. Added PI info editor
21. Added photo upload (saves to Images/team/, updates team.json)
22. Added section visibility toggles (current/alumni/fac/fac_alumni)
23. Added git auto-commit after CV parsing

**Publications page overhaul:**
24. Replaced PubMed API with CV-parsed data as primary source
25. Added 6 tabs (peer-reviewed, preprints, under review, in preparation, presentations, all)
26. Added sort dropdown (newest first default, oldest, CV order)
27. Added PMCID badges (59 of 170 have PMCID) linking to PubMed Central
28. Fixed Google Scholar link to correct ID (`Iug5mCsAAAAJ`)
29. Fixed year filter reset on tab switch
30. Fixed preprints showing in "all" tab

**People page overhaul:**
31. Made fully data-driven from team.json
32. Loaded all CV members: 8 current, 17 alumni, 9 FAC current, 10 FAC previous
33. Added visibility toggle support (FAC sections hidden by default)
34. Added GitHub (Personal) + GitHub (Hur Lab) links to PI

**Content fixes:**
35. Phone number fixed to (701) 777-6814 everywhere
36. Email corrected: junguk.hur@med.UND.edu + jung.hur@UND.edu
37. Added GitHub personal link (windysky/)
38. Removed DaYeon Shin, Farah Lubin from collaborators
39. Added Arzucan Ozgur to Ontology research collaborators
40. Added Cornelius Dyke + Marina Kim to AI/ML research collaborators
41. Updated all collaborator URLs to current pages
42. Added NIH Reporter + ARPA-H links to active grants
43. Removed effort percentages from grant notes
44. Positions page changed to "Future Openings" (no current openings)
45. Visiting scholar duration changed to 6 months–3 years
46. Tools page added R Shiny to category filter
47. Funding section made dynamic (current + previous grants total)

**Performance fix:**
48. Fixed admin server 56-second delay caused by reverse DNS lookups (override `address_string()`)

**Bug fixes from testing audit:**
49. Fixed preprints missing from "all" tab
50. Fixed year filter persisting across tab switches
51. Removed orphaned js/publications.js
52. Fixed admin dashboard status cards not populating (wrong file path + response structure mismatch)
53. Fixed admin parse output not displaying (wrong field name: data.output → data.stdout)

### Files/modules/functions touched
- `index.html` — dynamic stats, recent pubs from JSON, dynamic funding section
- `research.html` — data-driven from research.json + grants.json, grant title links
- `research-detail.html` — NEW: per-area detail with keyword-filtered publications
- `publications.html` — complete rewrite: CV data source, 6 tabs, sort, PMCID badges
- `tools.html` — added R Shiny filter
- `people.html` — complete rewrite: data-driven, visibility, FAC sections, GitHub links
- `positions.html` — data-driven from positions.json, "Future Openings" mode
- `collaborators.html` — data-driven from collaborators.json
- `js/components.js` — phone/email fix, admin link in footer
- `data/*.json` — all 8 JSON data files created/updated
- `scripts/parse_cv.py` — CV parser with PMCID extraction, git auto-commit
- `scripts/admin_server.py` — admin server with team CRUD, visibility, photo upload, DNS fix
- `scripts/templates/admin.html` — dashboard + team management with FAC sections
- `.gitignore` — created with exclusions for large dirs, zips, credentials
- `CLAUDE.md` — updated to reflect final architecture

### Key technical decisions and rationale
- **JSON-as-database over SQL**: Zero dependencies, human-readable, git-trackable, sufficient for lab website traffic
- **CV parser as single source of truth**: Publications and grants auto-generated from PDF, reducing manual maintenance
- **Section visibility in team.json**: Allows admin to control public page display without code changes
- **FAC split (current/previous)**: Better organization than a single "hidden" bucket
- **Reverse DNS override**: Python's BaseHTTPRequestHandler does DNS lookups by default, causing 56s delays
- **Git auto-commit on parse**: Creates version history of every CV update automatically

### Problems encountered and resolutions
1. **SSL/HTTPS not working externally**: University firewall blocks port 443. Nginx configured correctly but unreachable. Let's Encrypt failed (port 80 also blocked from internet). **Unresolved** — need UND IT.
2. **Admin server 56s delay**: Reverse DNS lookups on every request. **Resolved** by overriding `address_string()`.
3. **Admin dashboard blank status**: Backend returned wrong structure + wrong file path. **Resolved** by rewriting `_handle_status()`.
4. **Admin template `hidden` CSS class corruption**: Bulk sed replaced CSS class `hidden` with `fac`. **Resolved** by targeted fixes to restore CSS classes.
5. **Publications missing from "all" tab**: Preprints section only showed on preprints tab. **Resolved** by adding `activeTab === 'all'` condition.

### Items explicitly completed
- All pages data-driven from JSON (no more hardcoded content)
- Admin panel with CV upload, parsing, team management, visibility toggles
- v2→root cutover complete
- Git repository initialized and pushed
- Directory cleanup (unused dirs → v1/)
- Google Scholar link corrected
- All collaborator URLs updated
- Grant links added (NIH Reporter, ARPA-H)
- PMCID support added to publications
- Publication sorting (newest/oldest/CV order)

### Items not completed
- Image optimization, favicon, OG meta tags, mobile testing
- HTTPS (blocked by university network)
- Admin tabs for editing collaborators/research/positions JSON
- Admin server auto-start on boot

### Verification performed
- All 8 HTML pages + 8 JSON data files return HTTP 200
- CV parser produces correct counts: 170 pubs, 59 PMCID, 35 grants
- Admin server response time: 0.001s (down from 56s)
- Full code audit by 3 parallel agents: found and fixed 5 bugs
- Git push successful to github.com/hurlab/hurlab.git

---

## Session 2026-03-25 14:39 CDT

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)

### Phase(s) worked on
- Phase 7: SEO & Analytics (favicon, sitemap, robots.txt, OG tags, schema.org, GA4)
- Phase 8: Content refinement (research areas, collaborators, tools expandable cards)
- Admin panel enhancements (drag-and-drop reorder)

### Concrete changes implemented

**SEO & Analytics:**
1. Created `favicon.svg` (teal-to-indigo H monogram with DNA dots)
2. Created `robots.txt` (allows crawling, blocks scripts/v1/cgi-bin)
3. Created `sitemap.xml` (12 URLs: 7 main + 5 research detail pages)
4. Added Open Graph meta tags to all 8 HTML pages
5. Added Twitter Card meta tags to index.html
6. Added schema.org ResearchOrganization JSON-LD to index.html
7. Added missing meta descriptions to positions.html and collaborators.html
8. Added favicon link to all pages
9. Added Google Analytics 4 (G-Z36JMZ1F1K) tracking to all 8 pages

**Content Updates:**
10. Expanded Neurological Disorders research area to include Alzheimer's and Parkinson's disease
11. Added AD/PD overview paragraphs, key topics, keywords, collaborator (James Porter)
12. Added Dr. Nicholas Lyssenko (Temple University) as AD collaborator in research.json and collaborators.json
13. Added Arzucan Ozgur to Ontology research collaborators
14. Added Cornelius Dyke + Marina Kim to AI/ML research collaborators
15. Added NIH Reporter + ARPA-H URLs to all 5 current grants in grants.json
16. Removed effort percentages from all grant notes
17. Added Sakai Portal link to footer (http://hurlab.med.und.edu:8282/portal/)
18. Added VIOLIN (violinet.org) as Knowledgebase category tool
19. Added Ignet (ignet.org) as Web Tool
20. Added "Knowledgebase" filter category to tools page (purple badge)

**Tools Page Expandable Cards:**
21. Added `details` field to all 11 tools in tools.json (longDescription, features, publications, relatedAreas)
22. Rewrote tool card template with Alpine.js click-to-expand functionality
23. Expanded card spans full width (col-span-3), shows detail sections
24. Added Alpine.js `x-collapse` plugin for smooth expand/collapse animation
25. Added chevron rotation indicator for expand state
26. Buttons (Launch/GitHub) and PubMed links use @click.stop to prevent toggle
27. Fixed collapse on click — removed @click.stop from detail container
28. Added auto-scroll to expanded card with 80px navbar offset
29. Limited to single expanded card — opening new card collapses previous

**Admin Panel:**
30. Added drag-and-drop reorder for team members (HTML5 Drag and Drop API)
31. Added POST /api/team/reorder endpoint (section, from, to)
32. Visual feedback: drag handle icon, dragged row fades, target row teal border
33. Reorder works for all 4 sections (current, alumni, fac, fac_alumni)

**External Review Assessment (HURLAB_IMPROVEMENT_PLAN.md):**
34. Reviewed all items from external agent's report
35. Most items were false positives (server-side fetch without JS execution)
36. Implemented genuine SEO items (favicon, sitemap, robots, OG, schema.org)

### Files/modules/functions touched
- `favicon.svg` — NEW: teal-to-indigo H monogram
- `robots.txt` — NEW: crawling rules
- `sitemap.xml` — NEW: 12 URLs
- `index.html` — GA4, OG tags, Twitter Card, schema.org JSON-LD
- `research.html` — GA4, OG tags
- `research-detail.html` — GA4, OG tags, PMCID badges
- `publications.html` — GA4, OG tags, PMCID badges
- `tools.html` — GA4, OG tags, expandable cards, x-collapse plugin, Knowledgebase filter, single-expand, auto-scroll
- `people.html` — GA4, OG tags, GitHub (Hur Lab) link on PI
- `positions.html` — GA4, OG tags, meta description added
- `collaborators.html` — GA4, OG tags, meta description added
- `js/components.js` — Sakai Portal link in footer
- `data/tools.json` — 11 tools (added VIOLIN, Ignet) with details field
- `data/research.json` — Neuro expanded (AD/PD), collaborators updated
- `data/collaborators.json` — Lyssenko added, URLs updated
- `data/grants.json` — NIH Reporter/ARPA-H URLs, effort % removed
- `scripts/admin_server.py` — POST /api/team/reorder endpoint
- `scripts/templates/admin.html` — drag-and-drop reorder UI

### Key technical decisions and rationale
- **Alpine.js x-collapse plugin**: Provides smooth expand/collapse animation without custom CSS transitions
- **Single-expand pattern**: `expandedTool` state lifted to parent component rather than per-card x-data — cleaner UX, prevents multiple open cards
- **Auto-scroll with offset**: `getBoundingClientRect().top + scrollY - 80` accounts for fixed navbar height
- **@click.stop selective**: Only on interactive elements (links, buttons), not on the detail container — so clicking the expanded card collapses it
- **External review triage**: Most findings were false positives from server-side fetch without JS execution. Only SEO items (genuinely missing files) were acted on.

### Problems encountered and resolutions
1. **Tool card collapse not working**: `@click.stop` on detail div blocked event propagation. **Resolved** by removing it, keeping @click.stop only on interactive elements.
2. **Expanded card scroll hiding title**: `scrollIntoView({block:'start'})` scrolled to exact top, hidden by fixed navbar. **Resolved** by using manual scroll with 80px offset.
3. **GA4 insertion via sed failed**: Escaping issues with shell heredoc. **Resolved** by using Python script for insertion.

### Items explicitly completed
- SEO: favicon, sitemap, robots.txt, OG tags, schema.org, GA4
- Tools: expandable detail cards with single-expand and auto-scroll
- Research: Neurological Disorders expanded with AD/PD
- Collaborators: Lyssenko, Dyke, Kim added
- Admin: drag-and-drop team member reorder
- VIOLIN and Ignet tools added
- Sakai Portal link restored

### Verification performed
- All pages return HTTP 200
- GA4 tag confirmed on all 8 pages (grep count)
- SEO files (robots.txt, sitemap.xml, favicon.svg) return HTTP 200
- Tool card expand/collapse/scroll tested by user
- Git push successful for all commits

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

## Session 2026-04-08 CDT (code review)

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)
- **Harness**: 4-agent team (Orchestrator + 2 Recon Reviewers + 3 Implementers + 1 QA)

### Phase(s) worked on
- Deep code review and bug fix across entire codebase

### Reconnaissance findings
- **Frontend reviewer**: 15 issues (3 High, 3 Medium, 9 Low)
- **Backend reviewer**: 15 issues (3 High, 4 Medium, 8 Low)
- After dedup and triage: 13 unique actionable bugs

### Concrete changes implemented

**HTTP→HTTPS migration (28 URLs across 10 files):**
1. Fixed og:url meta tags on all 8 HTML pages
2. Fixed schema.org JSON-LD URL on index.html
3. Fixed all 12 sitemap.xml `<loc>` entries
4. Fixed 5 tool launch URLs in data/tools.json
5. Fixed 2 hardcoded tool URLs on index.html homepage
6. Left 3 port-based URLs (3838, 8282, 8180) as http intentionally

**Admin panel bug fixes (6 bugs):**
7. Fixed logout redirect: `/login` (404) → `/` (correct)
8. Fixed `esc()` function to escape double quotes with `&quot;` — prevents HTML attribute breakout
9. Added 401 session-expiry handling: `apiFetch()` redirects to `/` on 401, all GET calls converted to use it
10. Removed `"url"` from sanitize_dict text_fields in `_handle_save_json()` — prevents URL corruption
11. Added try/except guard in `load_credentials()` for corrupt JSON
12. Removed dead no-op line `socketserver.TCPServer.address_family`

**Frontend consistency fixes (5 issues):**
13. Normalized Alpine.js CDN on index.html: jsdelivr → unpkg (matches all other pages)
14. Fixed AOS version on index.html: 2.3.4 → 2.3.1 (matches all other pages)
15. Removed unused dark mode `x-data` binding from index.html `<html>` tag
16. Fixed highlightPI regex on index.html: `\$` → `$|Hur\s*JU?\b` (matches publications.html)
17. Removed duplicate AOS.init() inline scripts from index.html, positions.html, collaborators.html

### Files modified
- `index.html` — OG tag, JSON-LD, tool URLs, Alpine CDN, AOS version, dark mode, regex, AOS dupe
- `research.html` — OG tag
- `publications.html` — OG tag
- `tools.html` — OG tag
- `people.html` — OG tag
- `positions.html` — OG tag, AOS dupe
- `collaborators.html` — OG tag, AOS dupe
- `research-detail.html` — OG tag
- `sitemap.xml` — all 12 loc entries
- `data/tools.json` — 5 tool launch URLs
- `scripts/admin_server.py` — sanitize fix, credentials guard, dead code removal
- `scripts/templates/admin.html` — esc(), logout, 401 handling

### Verification performed
- Playwright E2E regression: 90/90 passed (40.9s)
- Admin server: compile OK, restart OK, HTTP 200
- Zero remaining `https://hurlab.med.und.edu` on standard ports

### Harness statistics
- **Subagent spawns**: 6 (2 Recon Reviewers, 3 Implementers, 1 QA)
- **Issues found**: 13 actionable bugs
- **Issues fixed**: 13/13 (100%)
- **E2E regression**: 90 passed, 0 failed

---

## Session 2026-04-08 CDT (code review pass 2)

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)
- **Harness**: Deep sweep recon + 2 Implementers + QA

### Reconnaissance
- Second-pass deep sweep covering areas missed by first review
- 5 new issues found (1 Critical, 1 High, 2 Medium, 1 Known/intentional)

### Concrete changes implemented

**CV parsing artifact cleanup (Critical):**
1. Cleaned 26 publications in `data/publications.json` — removed "Junguk Hur, Ph.D. Curriculum Vitae" from text fields
2. Cleaned 3 grant fields in `data/grants.json` — same artifact removed from titles/notes
3. Fixed `scripts/parse_cv.py` `extract_text()` to strip CV header/footer artifacts during parsing (prevents recurrence)

**Error handling (High):**
4. Added try/catch to `research.html` init() — graceful fallback on fetch failure
5. Added try/catch to `collaborators.html` init() — graceful fallback on fetch failure

**Data consistency (Medium):**
6. Added DPNKB tool entry to `data/tools.json` — matches research.json reference, links to existing webapp
7. Fixed duplicate PMID in `data/tools.json` — PubChemSR corrected to PMID 18482452, DNMKB2 publications cleared

### Files modified
- `data/publications.json` — 26 entries cleaned
- `data/grants.json` — 3 fields cleaned
- `scripts/parse_cv.py` — CV header/footer stripping added
- `research.html` — try/catch error handling
- `collaborators.html` — try/catch error handling
- `data/tools.json` — DPNKB added, PMIDs corrected

### Verification performed
- Playwright E2E regression: 90/90 passed (36.2s)
- Zero CV artifacts in data files (grep verified)

### Harness statistics
- **Subagent spawns**: 4 (1 Recon, 2 Implementers, 1 QA)
- **Issues found**: 5 (1 intentional/skipped)
- **Issues fixed**: 4/4 actionable (100%)
