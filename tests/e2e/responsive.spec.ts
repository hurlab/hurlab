import { test, expect } from '@playwright/test';

const testPages = [
  { path: 'index.html', name: 'Home' },
  { path: 'publications.html', name: 'Publications' },
  { path: 'tools.html', name: 'Tools' },
];

test.describe('Mobile viewport (375x812)', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  for (const pg of testPages) {
    test(`${pg.name} — no horizontal overflow`, async ({ page }) => {
      await page.goto(pg.path);
      // Wait for content to load
      await page.waitForLoadState('networkidle');
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2); // allow 2px tolerance
    });

    test(`${pg.name} — hamburger menu is visible`, async ({ page }) => {
      await page.goto(pg.path);
      const hamburger = page.locator('nav button.md\\:hidden');
      await expect(hamburger).toBeVisible();
    });
  }
});

test.describe('Desktop viewport (1280x800)', () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  for (const pg of testPages) {
    test(`${pg.name} — hamburger menu is hidden`, async ({ page }) => {
      await page.goto(pg.path);
      const hamburger = page.locator('nav button.md\\:hidden');
      await expect(hamburger).toBeHidden();
    });

    test(`${pg.name} — desktop nav links are visible`, async ({ page }) => {
      await page.goto(pg.path);
      const desktopNav = page.locator('.hidden.md\\:flex');
      await expect(desktopNav).toBeVisible();
    });
  }
});
