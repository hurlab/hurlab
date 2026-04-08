import { test, expect } from '@playwright/test';

const navLinks = [
  { label: 'Home', href: 'index.html' },
  { label: 'Research', href: 'research.html' },
  { label: 'Publications', href: 'publications.html' },
  { label: 'Tools', href: 'tools.html' },
  { label: 'People', href: 'people.html' },
  { label: 'Positions', href: 'positions.html' },
  { label: 'Collaborators', href: 'collaborators.html' },
];

test.describe('Desktop navigation', () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  for (const link of navLinks) {
    test(`nav link "${link.label}" resolves to ${link.href}`, async ({ page }) => {
      await page.goto('index.html');
      // Desktop nav links are inside the hidden md:flex div
      const desktopNav = page.locator('.hidden.md\\:flex');
      const navLink = desktopNav.getByText(link.label, { exact: true });
      await expect(navLink).toBeVisible();
      await navLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain(link.href);
    });
  }
});

test.describe('Mobile navigation', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('hamburger menu button is visible', async ({ page }) => {
    await page.goto('index.html');
    const menuButton = page.locator('nav button.md\\:hidden');
    await expect(menuButton).toBeVisible();
  });

  test('hamburger menu opens on click', async ({ page }) => {
    await page.goto('index.html');
    const menuButton = page.locator('nav button.md\\:hidden');
    await menuButton.click();
    // Mobile menu panel with x-show="open" becomes visible
    const mobileMenu = page.locator('nav div[x-show="open"]');
    await expect(mobileMenu).toBeVisible();
  });

  test('hamburger menu closes on second click', async ({ page }) => {
    await page.goto('index.html');
    const menuButton = page.locator('nav button.md\\:hidden');
    await menuButton.click();
    const mobileMenu = page.locator('nav div[x-show="open"]');
    await expect(mobileMenu).toBeVisible();
    // Close it
    await menuButton.click();
    await expect(mobileMenu).toBeHidden();
  });

  for (const link of navLinks) {
    test(`mobile nav link "${link.label}" works`, async ({ page }) => {
      await page.goto('index.html');
      const menuButton = page.locator('nav button.md\\:hidden');
      await menuButton.click();
      const mobilePanel = page.locator('nav div[x-show="open"]');
      const navLink = mobilePanel.getByText(link.label, { exact: true });
      await expect(navLink).toBeVisible();
      await navLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain(link.href);
    });
  }
});

test.describe('Footer links', () => {
  test('footer contains quick links section', async ({ page }) => {
    await page.goto('index.html');
    const footer = page.locator('footer');
    await expect(footer.getByText('Quick Links')).toBeVisible();
  });

  test('footer contains contact section', async ({ page }) => {
    await page.goto('index.html');
    const footer = page.locator('footer');
    await expect(footer.getByText('Contact')).toBeVisible();
  });

  test('footer contains affiliations section', async ({ page }) => {
    await page.goto('index.html');
    const footer = page.locator('footer');
    await expect(footer.getByText('Affiliations')).toBeVisible();
  });
});
