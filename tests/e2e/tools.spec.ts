import { test, expect } from '@playwright/test';

test.describe('Tools page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('tools.html');
  });

  test('loads and shows tool cards', async ({ page }) => {
    // Tool cards contain tool names rendered by Alpine from tools.json
    const toolCards = page.locator('.gradient-border');
    await expect(toolCards.first()).toBeVisible({ timeout: 15000 });
    const count = await toolCards.count();
    expect(count).toBeGreaterThan(5);
  });

  test('clicking a tool card expands it', async ({ page }) => {
    const toolCards = page.locator('.gradient-border');
    await expect(toolCards.first()).toBeVisible({ timeout: 15000 });

    // Click the first tool card
    await toolCards.first().click();

    // Expanded card should have the ring-2 class and span full width
    await expect(toolCards.first()).toHaveClass(/ring-2/, { timeout: 5000 });
  });

  test('clicking another card collapses the first (single-expand)', async ({ page }) => {
    const toolCards = page.locator('.gradient-border');
    await expect(toolCards.first()).toBeVisible({ timeout: 15000 });

    // Expand first card
    await toolCards.first().click();
    await expect(toolCards.first()).toHaveClass(/ring-2/, { timeout: 5000 });

    // Click second card
    await toolCards.nth(1).click();

    // First card should no longer be expanded
    await expect(toolCards.first()).not.toHaveClass(/ring-2/, { timeout: 5000 });
    // Second card should be expanded
    await expect(toolCards.nth(1)).toHaveClass(/ring-2/, { timeout: 5000 });
  });

  test('expanded card shows long description', async ({ page }) => {
    const toolCards = page.locator('.gradient-border');
    await expect(toolCards.first()).toBeVisible({ timeout: 15000 });

    // Click to expand
    await toolCards.first().click();
    await expect(toolCards.first()).toHaveClass(/ring-2/, { timeout: 5000 });

    // The expanded section should show detail content (longDescription is in a bg-gray-50 div)
    const detailSection = toolCards.first().locator('.bg-gray-50');
    await expect(detailSection).toBeVisible({ timeout: 5000 });
  });

  test('expanded card shows key features', async ({ page }) => {
    const toolCards = page.locator('.gradient-border');
    await expect(toolCards.first()).toBeVisible({ timeout: 15000 });

    // Click to expand
    await toolCards.first().click();
    await expect(toolCards.first()).toHaveClass(/ring-2/, { timeout: 5000 });

    // Should show "Key Features" heading
    const features = toolCards.first().getByText('Key Features');
    await expect(features).toBeVisible({ timeout: 5000 });
  });
});
