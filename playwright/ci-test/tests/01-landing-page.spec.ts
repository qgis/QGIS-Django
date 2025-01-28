import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('landing page', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.locator('#maincolumn')).toContainText('There is a collection of plugins ready to be used, available to download. These plugins can also be installed directly from the QGIS Plugin Manager within the QGIS application.');

  await expect(page.getByRole('link', { name: 'available to download' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('Notes for plugin users');

  await expect(page.getByRole('link', { name: 'Developer mailing-list' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('Resources for plugin authors');

  await expect(page.getByRole('link', { name: 'pyQGIS cookbook' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Python API' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS C++ API' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'publish your plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Home' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'About plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Plugins', exact: true })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Planet' })).toBeVisible();

  await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Logout' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Popular plugins' })).toBeVisible();

  const pluginTags =  page.getByRole('button', { name: ' Plugin Tags ' });

  await expect(pluginTags).toBeVisible();

  await pluginTags.click();

  await expect(page.locator('#tagcloudModal').getByText('Plugin Tags')).toBeVisible();

  await page.getByText('×').click();

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.locator('header')).toContainText('Sustaining Members');

  await expect(page.locator('#mastodon').getByRole('link')).toBeVisible();

  await expect(page.locator('#facebook').getByRole('link')).toBeVisible();

  await expect(page.locator('#github').getByRole('link')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Creative Commons Attribution-' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'The Noun Project collection' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Alessandro Pasotti' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Kartoza iconKartoza' })).toBeVisible();

  await expect(page.getByRole('contentinfo')).toBeVisible();

  await expect(page.getByPlaceholder('Search')).toBeEmpty();

  await expect(page.getByText('QGIS QGIS Home About plugins')).toBeVisible();

});