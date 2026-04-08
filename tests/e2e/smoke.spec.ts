import { test, expect } from '@playwright/test';

const pages = [
  { path: 'index.html', name: 'Home' },
  { path: 'research.html', name: 'Research' },
  { path: 'publications.html', name: 'Publications' },
  { path: 'tools.html', name: 'Tools' },
  { path: 'people.html', name: 'People' },
  { path: 'positions.html', name: 'Positions' },
  { path: 'collaborators.html', name: 'Collaborators' },
  { path: 'research-detail.html', name: 'Research Detail' },
];

for (const page of pages) {
  test.describe(`${page.name} page (${page.path})`, () => {
    test('loads with HTTP 200', async ({ page: p }) => {
      const response = await p.goto(page.path);
      expect(response?.status()).toBe(200);
    });

    test('has a title element', async ({ page: p }) => {
      await p.goto(page.path);
      const title = await p.title();
      expect(title.length).toBeGreaterThan(0);
    });

    test('has the nav bar visible', async ({ page: p }) => {
      await p.goto(page.path);
      const nav = p.locator('nav');
      await expect(nav).toBeVisible();
    });

    test('has footer visible', async ({ page: p }) => {
      await p.goto(page.path);
      const footer = p.locator('footer');
      await expect(footer).toBeVisible();
    });

    test('has Google Analytics tag', async ({ page: p }) => {
      await p.goto(page.path);
      const gaScript = p.locator('script[src*="googletagmanager.com/gtag"]');
      await expect(gaScript).toHaveCount(1);
    });
  });
}
