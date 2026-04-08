import { chromium } from 'playwright';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const BASE_URL = 'https://hurlab.med.und.edu/hurlab';
const SCREENSHOT_DIR = join(import.meta.dirname, 'screenshots');

const PAGES = [
  { name: 'index', url: `${BASE_URL}/index.html` },
  { name: 'research', url: `${BASE_URL}/research.html` },
  { name: 'publications', url: `${BASE_URL}/publications.html` },
  { name: 'tools', url: `${BASE_URL}/tools.html` },
  { name: 'people', url: `${BASE_URL}/people.html` },
  { name: 'positions', url: `${BASE_URL}/positions.html` },
  { name: 'collaborators', url: `${BASE_URL}/collaborators.html` },
  { name: 'research-detail', url: `${BASE_URL}/research-detail.html?area=0` },
];

const VIEWPORTS = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1280, height: 800 },
];

if (!existsSync(SCREENSHOT_DIR)) mkdirSync(SCREENSHOT_DIR, { recursive: true });

const issues = [];

function report(page, viewport, msg) {
  const entry = `[${page}][${viewport}] ${msg}`;
  issues.push(entry);
  console.log(`  ⚠ ${entry}`);
}

async function main() {
  const browser = await chromium.launch({ headless: true });

  for (const page of PAGES) {
    console.log(`\n=== Testing: ${page.name} ===`);

    for (const vp of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        ignoreHTTPSErrors: true,
      });
      const tab = await context.newPage();

      try {
        await tab.goto(page.url, { waitUntil: 'networkidle', timeout: 30000 });
        // Wait for Alpine.js to initialize
        await tab.waitForTimeout(1500);

        // Take full-page screenshot
        const ssPath = join(SCREENSHOT_DIR, `${page.name}-${vp.name}.png`);
        await tab.screenshot({ path: ssPath, fullPage: true });
        console.log(`  ✓ Screenshot: ${page.name}-${vp.name}.png`);

        // Check 1: Horizontal overflow
        const scrollWidth = await tab.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await tab.evaluate(() => document.documentElement.clientWidth);
        if (scrollWidth > clientWidth + 2) {
          report(page.name, vp.name, `Horizontal overflow: scrollWidth=${scrollWidth} > clientWidth=${clientWidth} (diff=${scrollWidth - clientWidth}px)`);

          // Find which elements overflow
          const overflowers = await tab.evaluate((vpWidth) => {
            const results = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
              const rect = el.getBoundingClientRect();
              if (rect.right > vpWidth + 2) {
                const tag = el.tagName.toLowerCase();
                const cls = el.className ? (typeof el.className === 'string' ? el.className.substring(0, 80) : '') : '';
                const id = el.id || '';
                results.push({ tag, id, cls: cls, right: Math.round(rect.right), width: Math.round(rect.width) });
              }
            }
            // Deduplicate by keeping unique tag+class combos
            const seen = new Set();
            return results.filter(r => {
              const key = `${r.tag}.${r.cls.substring(0,30)}`;
              if (seen.has(key)) return false;
              seen.add(key);
              return true;
            }).slice(0, 10);
          }, vp.width);

          if (overflowers.length > 0) {
            report(page.name, vp.name, `Overflowing elements: ${JSON.stringify(overflowers, null, 0)}`);
          }
        }

        // Check 2: Mobile-specific checks
        if (vp.name === 'mobile') {
          // Hamburger menu visible?
          const hamburger = await tab.$('button.md\\:hidden');
          if (hamburger) {
            const isVisible = await hamburger.isVisible();
            if (!isVisible) {
              report(page.name, vp.name, 'Hamburger menu button NOT visible');
            } else {
              console.log(`  ✓ Hamburger menu visible`);

              // Click hamburger and check mobile menu opens
              await hamburger.click();
              await tab.waitForTimeout(500);

              const mobileMenu = await tab.$('.md\\:hidden.border-t');
              if (mobileMenu) {
                const menuVisible = await mobileMenu.isVisible();
                if (!menuVisible) {
                  report(page.name, vp.name, 'Mobile menu did NOT open after hamburger click');
                } else {
                  console.log(`  ✓ Mobile menu opens on click`);
                  // Take screenshot of open menu
                  await tab.screenshot({ path: join(SCREENSHOT_DIR, `${page.name}-mobile-menu-open.png`), fullPage: false });
                }
              }
            }
          } else {
            report(page.name, vp.name, 'Hamburger menu button NOT found in DOM');
          }

          // Check for text too small
          const tinyText = await tab.evaluate(() => {
            const elements = document.querySelectorAll('p, span, a, li, td, th');
            let count = 0;
            for (const el of elements) {
              const style = window.getComputedStyle(el);
              const size = parseFloat(style.fontSize);
              if (size < 12 && el.textContent.trim().length > 0 && el.offsetHeight > 0) {
                count++;
              }
            }
            return count;
          });
          if (tinyText > 5) {
            report(page.name, vp.name, `${tinyText} elements with font-size < 12px`);
          }

          // Check for touch target sizes (buttons/links too small)
          const smallTargets = await tab.evaluate(() => {
            const targets = document.querySelectorAll('a, button');
            let count = 0;
            for (const t of targets) {
              const rect = t.getBoundingClientRect();
              if (rect.width > 0 && rect.height > 0 && (rect.width < 30 || rect.height < 30) && t.offsetParent !== null) {
                count++;
              }
            }
            return count;
          });
          if (smallTargets > 3) {
            report(page.name, vp.name, `${smallTargets} touch targets smaller than 30x30px`);
          }
        }

      } catch (err) {
        report(page.name, vp.name, `ERROR: ${err.message}`);
      }

      await context.close();
    }
  }

  await browser.close();

  // Summary
  console.log('\n\n========== MOBILE QA SUMMARY ==========');
  if (issues.length === 0) {
    console.log('ALL PAGES PASS — No issues found!');
  } else {
    console.log(`Found ${issues.length} issue(s):\n`);
    issues.forEach(i => console.log(`  ⚠ ${i}`));
  }
  console.log('========================================\n');

  // Write JSON report
  writeFileSync(join(SCREENSHOT_DIR, 'report.json'), JSON.stringify({ timestamp: new Date().toISOString(), issues }, null, 2));
}

main().catch(err => { console.error('Fatal:', err); process.exit(1); });
