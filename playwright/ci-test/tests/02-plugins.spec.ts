import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('plugins', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: 'Plugins', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Plugins', exact: true }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Python Plugins Repository');

  await expect(page.locator('#maincolumn')).toContainText('All plugins');

  await expect(page.locator('#list_commands')).toContainText('1 records found');

  await expect(page.getByRole('cell', { name: 'Name' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Approved' })).toBeVisible();

  await expect(page.getByRole('img', { name: 'Approved' })).toBeVisible();

  await expect(page.getByTitle('Featured')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Downloads', exact: true })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Author' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Latest Plugin Version' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Created on' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Stars (votes)' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Stable' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Exp.' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Manage' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Plugin icon' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Coffee Plugin' })).toBeVisible();

  await expect(page.getByRole('link', { name: '1.3' })).toBeVisible();

  await expect(page.getByRole('link', { name: '1.4' })).toBeVisible();

  await expect(page.getByRole('link', { name: '' })).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload a plugin' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'My plugins' })).toBeVisible();

  await expect(page.locator('#collapse-related-plugins')).toContainText('Plugins');

  await expect(page.getByRole('link', { name: 'Unapproved' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Reviewed Plugins (Resolved)' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Reviewed Plugins (Pending)' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Awaiting review' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Deprecated' })).toBeVisible();

  await expect(page.getByText('Featured')).toBeVisible();

  await expect(page.getByRole('link', { name: 'All' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'New Plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Updated Plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Experimental' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Popular' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Most voted' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Top downloads' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Most rated' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Server plugins' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('× Deprecated plugins are printed in red.');

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.locator('header')).toContainText('Sustaining Members');

  await expect(page.getByRole('contentinfo')).toBeVisible();

  await expect(page.locator('#mastodon').getByRole('link')).toBeVisible();

  await expect(page.locator('#facebook').getByRole('link')).toBeVisible();

  await expect(page.locator('#github').getByRole('link')).toBeVisible();
});