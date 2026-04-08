# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Hur Lab** academic website for Dr. Junguk Hur, Associate Professor at the Department of Biomedical Sciences, UND School of Medicine and Health Sciences. It is deployed as a webapp under Apache Tomcat 9.0.37.

The site serves as a research portal, combining lab information, publications, bioinformatics web tools, and archival course materials.

## Deployment

- **Server**: Apache Tomcat 9.0.37 at `/home/hurlab/apache-tomcat-9.0.37/`
- **Webapp root**: `/home/hurlab/apache-tomcat-9.0.37/webapps/hurlab/`
- **Site URL**: `https://hurlab.med.und.edu/hurlab/`
- **Modern site**: Root-level HTML files — the redesigned data-driven website
- **Legacy site**: Archived in `v1/` subdirectory (frameset-based, kept for reference)
- **CGI scripts**: `cgi-bin/` — Perl-based bioinformatics tools (still active)
- **Admin panel**: Port 8180 (credentials in `scripts/.admin_credentials`)
- No build system or package manager — all CDN-based, served directly by Tomcat

## Site Architecture

### Tech Stack (all via CDN, no build step)
- **CSS**: Tailwind CSS Play CDN — configured in `js/theme.js`
- **JS Interactivity**: Alpine.js 3.x (deferred) — tabs, filters, search, mobile menu
- **Animations**: AOS (Animate on Scroll)
- **Fonts**: Inter (body) + JetBrains Mono (code/tool names) via Google Fonts
- **Data layer**: 8 JSON files in `data/` serve as the database

### File Structure
```
hurlab/                   ← webroot (Tomcat webapp)
  *.html                  # 8 public pages + research-detail.html
  css/custom.css          # Custom animations, card effects, scrollbar
  js/
    theme.js              # Tailwind Play CDN config (colors, fonts)
    components.js         # Shared nav + footer injection (runs as IIFE)
    animations.js         # AOS init + counter animations
  data/
    publications.json     # 170 peer-reviewed + preprints + talks + posters
    grants.json           # Current + pending + previous grants
    team.json             # PI + current + alumni + FAC + visibility settings
    tools.json            # 11 tools with expandable details
    research.json         # 5 research areas with detail content
    collaborators.json    # 4 categories, 15 collaborators
    positions.json        # Position types, isHiring flag
    site.json             # Lab-wide configuration
  Images/                 # Photos (team/, etc.)
  Personal/               # CV PDF (symlinks)
  scripts/
    admin_server.py       # Admin panel server (port 8180)
    parse_cv.py           # CV parser → publications.json + grants.json
    start_admin.sh        # Admin server launcher
    templates/            # Admin panel HTML templates
  cgi-bin/                # Active Perl CGI tools
  miRNA/                  # Active miRNA BLAST tools
  v1/                     # Legacy site + archived directories
```

### Key Patterns
- **Navigation**: Injected by `components.js` IIFE (runs before Alpine.js `defer` init). Fixed top glassmorphism nav with mobile hamburger.
- **Script order**: `components.js` must load as regular script at bottom of body BEFORE Alpine processes `x-data` attributes. Alpine is loaded with `defer` in head.
- **Data-driven pages**: All pages fetch from `data/*.json` via Alpine.js `x-init`, making content updates JSON-only.
- **Publications**: Primary source is CV-parsed data in `data/publications.json`. 6 tabs, sort, search, year filter, PMID+PMCID+DOI badges.
- **Color palette**: Teal primary (#0F766E), indigo accent (#6366F1), surface (#F0FDFA). Defined in `js/theme.js`.
- **Hero sections**: Use `bg-hero-pattern` (teal-to-indigo gradient) defined in Tailwind config.

### Adding/Updating Content
- **Team members**: Edit `data/team.json` or use admin panel
- **Tools**: Edit `data/tools.json`
- **Publications/Grants**: Upload CV via admin panel → `parse_cv.py` auto-updates JSON + git commits
- **Research areas**: Edit `data/research.json`
- **Collaborators**: Edit `data/collaborators.json`
- **New pages**: Copy head/body pattern from any existing page, ensure `components.js` loads at bottom

## CGI/Perl Tools (`cgi-bin/`)

Server-side bioinformatics tools (still active):
- **WebTools/SeqAlign/** — Sequence alignment
- **WebTools/LODCalc/** — LOD score calculation
- **miRNA/** — miRNA BLAST tools with platform-specific binaries
- Shared subroutines in `commonsubs.pl`

## Large Data Directories (avoid scanning)

- **Files/** (~21GB), **Temp/** (~49GB) — research data and archives
