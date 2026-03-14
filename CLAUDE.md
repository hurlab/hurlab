# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Hur Lab** academic website for Dr. Junguk Hur, Associate Professor at the Department of Biomedical Sciences, UND School of Medicine and Health Sciences. It is deployed as a webapp under Apache Tomcat 9.0.37.

The site serves as a research portal, combining lab information, publications, bioinformatics web tools, and archival course materials.

## Deployment

- **Server**: Apache Tomcat 9.0.37 at `/home/hurlab/apache-tomcat-9.0.37/`
- **Webapp root**: `/home/hurlab/apache-tomcat-9.0.37/webapps/hurlab/`
- **Modern site**: `v2/` subdirectory — the redesigned website
- **Legacy site**: Root-level HTML files (frameset-based, kept for reference)
- **CGI scripts**: `cgi-bin/` — Perl-based bioinformatics tools (still active)
- No build system or package manager — all CDN-based, served directly by Tomcat

## Modern Site Architecture (`v2/`)

### Tech Stack (all via CDN, no build step)
- **CSS**: Tailwind CSS Play CDN — configured in `js/theme.js`
- **JS Interactivity**: Alpine.js 3.x (deferred) — tabs, filters, search, mobile menu
- **Animations**: AOS (Animate on Scroll)
- **Fonts**: Inter (body) + JetBrains Mono (code/tool names) via Google Fonts
- **Publications**: NCBI PubMed E-utilities API + static JSON fallback

### File Structure
```
v2/
  index.html              # Home: hero + research highlights + recent pubs + tools
  research.html           # 5 research areas + funded grants
  publications.html       # Dynamic PubMed + filterable list + tabs
  tools.html              # Tool cards with filters, fetched from JSON
  people.html             # PI profile + team grid + alumni
  positions.html          # Open positions
  collaborators.html      # Grouped by research area
  css/custom.css          # Custom animations, card effects, scrollbar
  js/
    theme.js              # Tailwind Play CDN config (colors, fonts)
    components.js         # Shared nav + footer injection (runs as IIFE)
    publications.js       # PubMed API integration with sessionStorage cache
    animations.js         # AOS init + counter animations
  data/
    tools.json            # 9 tool definitions
    team.json             # PI + current members + alumni
    publications.json     # Static fallback + non-PubMed entries
```

### Key Patterns
- **Navigation**: Injected by `components.js` IIFE (runs before Alpine.js `defer` init). Fixed top glassmorphism nav with mobile hamburger.
- **Script order**: `components.js` must load as regular script at bottom of body BEFORE Alpine processes `x-data` attributes. Alpine is loaded with `defer` in head.
- **Data-driven pages**: Tools and People pages fetch from `data/*.json` via Alpine.js `x-init`, making content updates JSON-only.
- **Publications**: Primary source is live PubMed API (cached in sessionStorage for 24h). Falls back to `data/publications.json` for non-PubMed entries (under review, presentations, patent).
- **Color palette**: Teal primary (#0F766E), indigo accent (#6366F1), surface (#F0FDFA). Defined in `js/theme.js`.
- **Hero sections**: Use `bg-hero-pattern` (teal-to-indigo gradient) defined in Tailwind config.

### Adding/Updating Content
- **Team members**: Edit `data/team.json`
- **Tools**: Edit `data/tools.json`
- **Publications**: Non-PubMed entries in `data/publications.json`; PubMed papers auto-fetched
- **New pages**: Copy head/body pattern from any existing page, ensure `components.js` loads at bottom

## Legacy Site (root-level files)

The original frameset-based site remains at root level for reference:
- `index.html` — frameset entry point
- `menu.html` — sidebar nav
- Individual content pages: `home.html`, `people.html`, etc.

## CGI/Perl Tools (`cgi-bin/`)

Server-side bioinformatics tools (still active):
- **WebTools/SeqAlign/** — Sequence alignment
- **WebTools/LODCalc/** — LOD score calculation
- **miRNA/** — miRNA BLAST tools with platform-specific binaries
- Shared subroutines in `commonsubs.pl`

## Large Data Directories (avoid scanning)

- **Files/** (~21GB), **Temp/** (~49GB), **BACKUPS/** — research data and archives
