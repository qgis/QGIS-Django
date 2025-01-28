import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('test planet tab', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: 'Planet' })).toBeVisible();

  await page.getByRole('link', { name: 'Planet' }).click();

  await expect(page.locator('h2')).toContainText('QGIS Planet');

  await expect(page.getByRole('link', { name: 'QGIS Annual General Meeting –' })).toBeVisible();

  await expect(page.locator('#content')).toContainText('December 23, 2023 QGIS Project blog');

  await expect(page.locator('#content')).toContainText('This is a content example');

  await expect(page.locator('#content')).toContainText('by underdark at 10:00 PM under web development');

  await expect(page.getByRole('link', { name: ' Back to Top' })).toBeVisible();

  await expect(page.locator('#feed_list')).toContainText('Blog List');

  await expect(page.getByRole('link', { name: 'QGIS Project blog' })).toBeVisible();

  await expect(page.locator('#tags')).toContainText('Tags');

  await expect(page.getByTitle('post')).toBeVisible();

  await expect(page.locator('#collapse-related-plugins')).toContainText('Sun Feb 11 18:50:20 2024');

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.locator('h3')).toContainText('Sustaining Members');

  await expect(page.locator('#mastodon').getByRole('link')).toBeVisible();

  await expect(page.locator('#facebook').getByRole('link')).toBeVisible();

  await expect(page.locator('#github').getByRole('link')).toBeVisible();

  await expect(page.getByRole('contentinfo')).toContainText('All content is licensed under Creative Commons Attribution-ShareAlike 3.0 licence (CC BY-SA).');

  await expect(page.getByRole('contentinfo')).toContainText('Select graphics from The Noun Project collection.');

  await expect(page.getByRole('contentinfo')).toContainText('This web application was developed by: Alessandro Pasotti and Kartoza. Version:');

  await expect(page.getByRole('link', { name: 'Creative Commons Attribution-' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'The Noun Project collection' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Alessandro Pasotti' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Kartoza iconKartoza' })).toBeVisible();
});