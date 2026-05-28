# Hur Lab Website Improvement Plan

**URL:** https://hurlab.med.und.edu/hurlab/  
**Date:** 2026-03-24  
**Author:** Bench (Virtual Lab Architect)

---

## 1. Current State Assessment

### 1.1 Pages Found & Status

| Page | URL | Status | Notes |
|------|-----|--------|-------|
| Home | `/hurlab/` | ✅ 200 | SPA-like with Alpine.js |
| Research | `/hurlab/research.html` | ⚠️ 200 | Minimal content (just heading) |
| Publications | `/hurlab/publications.html` | ⚠️ 200 | Shows categories but **data fails to load** |
| Tools | `/hurlab/tools.html` | ⚠️ 200 | Very sparse — just one line + GitHub link |
| Team | `/hurlab/team.html` | ❌ 404 | **Missing** |
| Contact | `/hurlab/contact.html` | ❌ 404 | **Missing** |
| Join | `/hurlab/join.html` | ❌ 404 | **Missing** |

### 1.2 Technology Stack

- **Server:** Apache Tomcat 9.0.37
- **Frontend:** Alpine.js + Tailwind CSS + AOS (Animate on Scroll)
- **Data:** Static JSON files (`data/publications.json`, `data/grants.json`, `data/tools.json`)
- **Hosting:** UND School of Medicine server

### 1.3 Design Quality — **C (Needs Improvement)**

**Strengths:**
- Modern tech choices (Alpine.js, Tailwind, AOS animations)
- Clean color scheme and typography (Inter font family)
- Dynamic stats counters on homepage
- Good research highlight cards

**Issues:**
- JavaScript template code is **leaking into rendered output** — `r.json()).then(d=>{` fragments visible in the page
- Stats counters show "..." placeholder instead of actual numbers (JSON fetch may be failing)
- Research page is essentially empty
- Publications page fails to load data
- Tools page shows almost no content despite 10+ tools in the JSON
- Navigation links to team/contact/join pages that don't exist

### 1.4 Content Completeness — **D (Incomplete)**

**Existing content (from JSON data):**
- **Publications:** ~30+ peer-reviewed publications (2004–present)
- **Grants:** 5 current active grants totaling ~$37.8M, 3 pending
- **Tools:** 10 tools (SciMiner, PubChemSR, DNMKB2, VennDetail, richR, Tox21 Enricher, richStudio, richCluster, scGEN, Ignet)

**Missing content:**
- Team member profiles and photos
- Lab mission/vision statement
- Join/apply information
- News/blog section
- Contact information (email, office, map)
- Lab alumni tracking
- Teaching/mentoring information
- PI biography on homepage

### 1.5 User Experience (UX) — **D**

- Broken navigation links erode trust immediately
- Publications page shows error message ("Could not load publications data")
- Stats section doesn't render numbers
- No consistent way to contact the lab
- No call-to-action for prospective students/postdocs

### 1.6 Mobile Responsiveness — **C**

- Tailwind CSS provides responsive foundation
- Cannot fully verify without browser testing, but Tailwind defaults are generally good
- Need to verify navigation hamburger menu works on mobile

### 1.7 Loading Speed — **B**

- Static JSON files load fast (~100-300ms per fetch)
- External dependencies: Google Fonts, Tailwind CDN, Alpine.js, AOS
- No image optimization concerns (few images)
- Overall acceptable for an academic lab site

### 1.8 SEO — **C**

- Title tag present: "Hur Lab | Computational Biology & AI"
- No structured data (schema.org) for Organization, Person, or ResearchOrganization
- No sitemap.xml detected
- No robots.txt detected
- Meta description may be missing or generic
- No Open Graph tags for social sharing

---

## 2. Improvement Plan

### 2.1 Priority 1: Fix Broken Features (1-2 days)

#### 2.1.1 Fix JavaScript Rendering Bugs
- **Issue:** Alpine.js template expressions leaking into page content
- **Cause:** Improper `x-data` or `x-text` binding; template code rendered as text
- **Fix:** Review all `x-data` attributes and ensure `x-text` or `x-html` directives are properly used instead of raw template strings

#### 2.1.2 Fix Publications Data Loading
- **Issue:** "Could not load publications data" error
- **Cause:** Likely CORS issue, incorrect path, or JSON parsing error
- **Fix:** Check `data/publications.json` accessibility and response headers; verify fetch URL path

#### 2.1.3 Fix Stats Counter
- **Issue:** Shows "..." instead of numbers
- **Fix:** Same as 2.1.1 — ensure Alpine.js reactivity is working for `pubs`, `grants`, `tools` variables

#### 2.1.4 Fix Broken Navigation Links
- Remove or redirect links to team.html, contact.html, join.html until those pages exist
- Or create minimal placeholder pages

### 2.2 Priority 2: Complete Missing Content (3-5 days)

#### 2.2.1 Create Team Page (`team.html`)
```
Required content:
- PI: Junguk Hur, Ph.D. — photo, bio, research interests
- Current members: photos, roles, research focus
- Lab alumni: optional but recommended
- Collaboration network
```

#### 2.2.2 Create Contact/Join Page
```
Required content:
- Lab email address
- Office location (UND SMHS building, room number)
- Google Maps embed
- Open positions / how to apply
- Required materials for applicants
```

#### 2.2.3 Complete Research Page
- Currently only shows "# Research" heading
- Should mirror the 5 research highlights from homepage:
  1. Bioinformatics & Systems Biology
  2. Ontology-Based Knowledge Systems
  3. AI & Machine Learning
  4. Neurological Disorders
  5. Host-Pathogen Interactions
- Add project descriptions, representative publications per area

#### 2.2.4 Complete Tools Page
- `tools.json` contains 10 tools — display all of them
- For each tool: name, description, version, status, links (GitHub, live URL)
- Categorize: R Packages, Web Tools, Desktop, Shiny Apps

### 2.3 Priority 3: Design Enhancement (5-7 days)

#### 2.3.1 Visual Identity
- Add UND branding elements (colors, logo)
- Create a lab logo or wordmark
- Consistent header/footer across all pages
- Hero image on homepage (lab photo, campus, or abstract bioinformatics visualization)

#### 2.3.2 Homepage Layout
```
[Header: Hur Lab logo | Navigation]
[Hero: Lab name + tagline + background image]
[Stats: X Publications | X Active Grants | X Tools | $X+ Funding]
[Research Highlights: 5 cards in grid]
[Featured Tools: 3 tools with descriptions]
[Recent Publications: 5 latest with PMIDs]
[Funding: Grant logos/badges]
[Footer: Contact | Links | UND branding]
```

#### 2.3.3 Publications Page Enhancement
- Filterable by year, category, keyword
- Links to PubMed, DOI
- Citation count badges (via CrossRef API)
- Export as BibTeX functionality
- Group by year with collapsible sections

### 2.4 Priority 4: SEO & Technical (2-3 days)

#### 2.4.1 SEO Improvements
- Add schema.org `ResearchOrganization` structured data
- Create `sitemap.xml`
- Create `robots.txt`
- Add Open Graph and Twitter Card meta tags
- Ensure all images have alt text
- Add canonical URLs

#### 2.4.2 Technical Improvements
- Add SSL certificate (HTTPS) — currently HTTP only
- Add favicon
- Minify HTML/CSS/JS for production
- Add basic analytics (Google Analytics or Plausible)
- Set up CI/CD for content updates

---

## 3. Implementation Plan

### 3.1 Recommended Approach: Static Site Generator

**Why:** Current site is essentially static content with JSON data. A static site generator provides:
- Better performance
- SEO out of the box
- Version control for content
- Easy deployment
- No server maintenance

**Recommended Stack:**
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Framework | **Astro** or **11ty (Eleventy)** | Lightweight, no JS required for content pages |
| Styling | **Tailwind CSS** (keep existing) | Already in use, consistent |
| Animations | **AOS** (keep existing) | Already integrated |
| Data | **JSON + Markdown** | Publications in JSON, pages in Markdown |
| Build | Node.js | Existing ecosystem |
| Hosting | **GitHub Pages** or **Netlify** | Free, CDN-backed, auto-HTTPS |
| CI/CD | GitHub Actions | Auto-deploy on push |

### 3.2 Alternative: Keep Tomcat + Fix Current Site

If staying on UND servers is required:
1. Fix the 4 critical bugs (Section 2.1) — **1-2 days**
2. Add missing pages (Section 2.2) — **3-5 days**
3. Enhance design (Section 2.3) — **5-7 days**
4. SEO/technical (Section 2.4) — **2-3 days**

**Total estimated time: 2-3 weeks**

### 3.3 Recommended: Hybrid Approach

1. **Phase 1 (Week 1):** Fix all bugs, add missing pages on current Tomcat server
2. **Phase 2 (Week 2-3):** Build parallel Astro static site
3. **Phase 3 (Week 4):** Migrate to GitHub Pages with custom domain redirect

---

## 4. Cost Estimate

| Approach | Developer Time | Hosting/Year | Total |
|----------|---------------|-------------|-------|
| Fix current site | 2-3 weeks | $0 (UND server) | Developer time only |
| Static site rebuild | 3-4 weeks | $0 (GitHub Pages) | Developer time only |
| Professional web designer | $3,000-8,000 | $0-200/yr | $3,000-8,200 |
| WordPress + academic theme | 1 week setup | $100-300/yr | $100-300/yr |

**Recommendation:** Fix current site in Phase 1, migrate to Astro static site in Phase 2. Total time: 3-4 weeks part-time.

---

## 5. Quick Wins (< 1 hour each)

1. ✅ Fix broken nav links (remove or comment out)
2. ✅ Fix JSON template rendering bug
3. ✅ Add meta description
4. ✅ Add favicon
5. ✅ Fix publications data loading
6. ✅ Add a minimal team section to homepage
7. ✅ Add email contact in footer
