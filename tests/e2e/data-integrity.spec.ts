import { test, expect } from '@playwright/test';

test.describe('Data integrity — JSON files', () => {
  test('publications.json has peerReviewed array with >100 items', async ({ request }) => {
    const response = await request.get('data/publications.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.peerReviewed)).toBe(true);
    expect(data.peerReviewed.length).toBeGreaterThan(100);
  });

  test('team.json has pi object with name', async ({ request }) => {
    const response = await request.get('data/team.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.pi).toBeDefined();
    expect(data.pi.name).toBeTruthy();
  });

  test('tools.json has >5 tools', async ({ request }) => {
    const response = await request.get('data/tools.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThan(5);
  });

  test('grants.json has current array', async ({ request }) => {
    const response = await request.get('data/grants.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.current)).toBe(true);
  });

  test('research.json has areas array with 5 items', async ({ request }) => {
    const response = await request.get('data/research.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.areas)).toBe(true);
    expect(data.areas.length).toBe(5);
  });

  test('collaborators.json has categories array', async ({ request }) => {
    const response = await request.get('data/collaborators.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.categories)).toBe(true);
    expect(data.categories.length).toBeGreaterThan(0);
  });

  test('positions.json has positionTypes array', async ({ request }) => {
    const response = await request.get('data/positions.json');
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(Array.isArray(data.positionTypes)).toBe(true);
    expect(data.positionTypes.length).toBeGreaterThan(0);
  });
});
