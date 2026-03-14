# PROJECT_LOG.md

---

## Session 2026-03-14 13:23 CDT

- **Coding CLI used**: Claude Code CLI (Claude Opus 4.6, 1M context)

### Phase(s) worked on
- Phase 1: Foundation (directory structure, theme, shared components, home page)
- Phase 2: Data extraction (JSON data files from legacy HTML)
- Phase 3: Content pages (publications, research, tools)
- Phase 4: Secondary pages (people, positions, collaborators)
- Phase 5: Polish (partial — animations done, image/SEO/favicon remaining)

### Concrete changes implemented
1. Created `CLAUDE.md` at project root (initial creation, then updated to reflect v2 architecture)
2. Created complete `v2/` directory structure with 15 files:
   - 7 HTML pages: `index.html`, `research.html`, `publications.html`, `tools.html`, `people.html`, `positions.html`, `collaborators.html`
   - 4 JS files: `theme.js`, `components.js`, `publications.js`, `animations.js`
   - 1 CSS file: `custom.css`
   - 3 JSON data files: `tools.json`, `team.json`, `publications.json`
3. Fixed `components.js` from `DOMContentLoaded` listener to IIFE for proper Alpine.js compatibility

### Files/modules/functions touched
- `CLAUDE.md` — created then rewritten
- `v2/index.html` — home page with hero, research highlights, recent publications (Alpine.js PubMed fetch), featured tools, funding
- `v2/research.html` — 5 research areas with SVG icons, funded grants cards
- `v2/publications.html` — Alpine.js app with PubMed API, tabs, search, year filter, PI highlighting
- `v2/tools.html` — Alpine.js fetches tools.json, category filter, tool cards with launch/GitHub buttons
- `v2/people.html` — PI featured card, team grid with initials placeholders, collapsible alumni
- `v2/positions.html` — 3 position type cards, research areas, application instructions
- `v2/collaborators.html` — 4 category sections with colored borders, external links
- `v2/js/theme.js` — Tailwind Play CDN config (primary teal, accent indigo, surface colors, fonts)
- `v2/js/components.js` — Shared nav (glassmorphism, mobile hamburger) + footer injection as IIFE
- `v2/js/publications.js` — PubMed E-utilities API (esearch + esummary), sessionStorage cache (24h), PI name highlighting, recency detection
- `v2/js/animations.js` — AOS init, animated counter with IntersectionObserver
- `v2/css/custom.css` — x-cloak, float/pulse animations, hero-pattern, card-hover, gradient-text, gradient-border, pub-card, scrollbar, badges, focus styles
- `v2/data/tools.json` — 9 bioinformatics tools with metadata
- `v2/data/team.json` — PI + 9 current members + 2 alumni
- `v2/data/publications.json` — Profile links, 7 under-review papers, 1 patent

### Key technical decisions and rationale
- **Tailwind Play CDN** over compiled CSS: No build step needed, custom config inline, acceptable ~300ms overhead for academic site
- **Alpine.js over React/Vue**: Lightweight (15KB), declarative reactivity in HTML, no build pipeline, perfect for filtering/tabs/search
- **Multi-page over SPA**: Better for SEO, bookmarkable URLs, simpler maintenance, avoids routing complexity
- **IIFE for components.js**: Must execute before Alpine.js `defer` processes DOM; DOMContentLoaded had race condition
- **PubMed E-utilities direct fetch**: CORS-supported, no API key needed at low traffic, sessionStorage cache prevents redundant calls
- **JSON data files**: Content updates only require editing JSON, not HTML structure
- **v2/ subdirectory**: Allows parallel development without breaking live site

### Problems encountered and resolutions
1. **Playwright Chrome not found**: Playwright MCP server hardcodes `/opt/google/chrome/chrome`. Installed Chromium at `~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome` but cannot symlink to `/opt/google/chrome/` without root. **Unresolved** — visual testing blocked.
2. **Alpine.js + components.js race condition**: Nav HTML injected on DOMContentLoaded could fire after Alpine init. **Resolved** by changing to IIFE (synchronous execution during parse, before `defer` scripts).

### Items completed
- All Phase 1-4 deliverables (15 files)
- CLAUDE.md (created and updated)
- components.js race condition fix

### Items not completed
- Image optimization, OG meta tags, favicon, mobile testing, visual QA, root redirect

### Verification performed
- HTTP 200 status confirmed for all 7 HTML pages via curl
- File existence verified for all 15 v2/ files
- Script load order reviewed and confirmed correct across all pages
- No browser-based visual testing performed (Playwright blocked)
