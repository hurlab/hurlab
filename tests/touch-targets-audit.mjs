import { chromium } from 'playwright';

const BASE_URL = 'https://hurlab.med.und.edu/hurlab';
const PAGES = [
  { name: 'index', url: `${BASE_URL}/index.html` },
  { name: 'publications', url: `${BASE_URL}/publications.html` },
  { name: 'collaborators', url: `${BASE_URL}/collaborators.html` },
  { name: 'research-detail', url: `${BASE_URL}/research-detail.html?area=0` },
  { name: 'people', url: `${BASE_URL}/people.html` },
];

async function main() {
  const browser = await chromium.launch({ headless: true });

  for (const page of PAGES) {
    const context = await browser.newContext({
      viewport: { width: 375, height: 812 },
      ignoreHTTPSErrors: true,
    });
    const tab = await context.newPage();
    await tab.goto(page.url, { waitUntil: 'networkidle', timeout: 30000 });
    await tab.waitForTimeout(1500);

    const targets = await tab.evaluate(() => {
      const results = [];
      document.querySelectorAll('a, button').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0 && el.offsetParent !== null) {
          if (rect.width < 30 || rect.height < 30) {
            const text = el.textContent.trim().substring(0, 40);
            const tag = el.tagName.toLowerCase();
            const cls = (typeof el.className === 'string' ? el.className : '').substring(0, 100);
            const href = el.getAttribute('href') || '';
            results.push({
              tag, text, href: href.substring(0, 60),
              w: Math.round(rect.width), h: Math.round(rect.height),
              cls: cls.substring(0, 80)
            });
          }
        }
      });
      return results;
    });

    console.log(`\n=== ${page.name} (${targets.length} small targets) ===`);
    // Group by similar class patterns
    const groups = {};
    for (const t of targets) {
      const key = t.cls.substring(0, 50) || t.tag;
      if (!groups[key]) groups[key] = [];
      groups[key].push(t);
    }
    for (const [cls, items] of Object.entries(groups)) {
      console.log(`  [${items.length}x] ${items[0].w}x${items[0].h} cls="${cls}" text="${items[0].text.substring(0,30)}"`);
    }

    await context.close();
  }

  await browser.close();
}

main().catch(console.error);
