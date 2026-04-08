import { test, expect } from '@playwright/test';

test.describe('Publications page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('publications.html');
  });

  test('loads and displays publication cards', async ({ page }) => {
    const firstCard = page.locator('.pub-card').first();
    await expect(firstCard).toBeVisible({ timeout: 15000 });
  });

  test('shows publication count after data loads', async ({ page }) => {
    // The count is rendered by Alpine in a div containing "Showing" and spans with x-text
    // Wait for the filteredCount span to have numeric content
    const countSpan = page.locator('span[x-text="filteredCount"]');
    await expect(countSpan).toHaveText(/\d+/, { timeout: 15000 });
  });

  test('tab switching works — peer-reviewed tab is active by default', async ({ page }) => {
    const peerReviewedBtn = page.locator('button').filter({ hasText: 'Peer-Reviewed' }).first();
    await expect(peerReviewedBtn).toBeVisible({ timeout: 15000 });
    await expect(peerReviewedBtn).toHaveClass(/bg-teal-600/);
  });

  test('tab switching works — clicking a different tab changes content', async ({ page }) => {
    await expect(page.locator('.pub-card').first()).toBeVisible({ timeout: 15000 });

    // Click a different tab
    const tabs = page.locator('button').filter({ hasText: /Under Review|Preprints|Book Chapters|Talks|All/ });
    const secondTab = tabs.first();
    await expect(secondTab).toBeVisible();
    await secondTab.click();

    // Verify the clicked tab is now active
    await expect(secondTab).toHaveClass(/bg-teal-600/);
  });

  test('search filter works', async ({ page }) => {
    // Wait for publications to load
    const countSpan = page.locator('span[x-text="filteredCount"]');
    await expect(countSpan).toHaveText(/\d+/, { timeout: 15000 });

    // Get initial count
    const initialCount = await countSpan.textContent();

    // Type in search box
    const searchInput = page.getByPlaceholder('Search publications...');
    await expect(searchInput).toBeVisible();
    await searchInput.fill('diabetes');

    // Wait for filtered count to change (fewer results)
    await expect(countSpan).not.toHaveText(initialCount!, { timeout: 5000 });
  });

  test('year filter dropdown is functional', async ({ page }) => {
    await expect(page.locator('.pub-card').first()).toBeVisible({ timeout: 15000 });

    // The year filter is a select element
    const yearSelect = page.locator('select').first();
    await expect(yearSelect).toBeVisible();

    // It should have "All Years" as the default option
    const options = yearSelect.locator('option');
    await expect(options.first()).toHaveText('All Years');

    // Verify there are year options available
    const optionCount = await options.count();
    expect(optionCount).toBeGreaterThan(1);
  });
});
