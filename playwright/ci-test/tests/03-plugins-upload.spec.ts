import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('plugins upload', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('plugins upload', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('link', { name: 'Plugins', exact: true })).toBeVisible();

    await page.getByRole('link', { name: 'Plugins', exact: true }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS Python Plugins Repository');

    await expect(page.locator('#maincolumn')).toContainText('All plugins');

    await expect(page.locator('#list_commands')).toContainText('1 records found');

    await expect(page.getByRole('link', { name: 'Coffee Plugin' })).toBeVisible();

    await expect(page.getByRole('link', { name: ' Upload a plugin' })).toBeVisible();

    await page.getByRole('link', { name: ' Upload a plugin' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS Python Plugins Repository');

    await expect(page.locator('#maincolumn')).toContainText('Upload a plugin');

    const fileChooserPromise = page.waitForEvent('filechooser');

    await page.getByLabel('Plugin package:').click();

    const fileChooser = await fileChooserPromise;

    await fileChooser.setFiles('tests/fixtures/valid_plugin.zip_');

    //await page.getByLabel('Plugin package:').setInputFiles('valid_plugin.zip_');

    await page.getByRole('button', { name: 'Upload' }).click();

    await page.waitForLoadState('load');

    await expect(page.getByText('× The Plugin has been')).toBeVisible();

    await expect(page.locator('#maincolumn')).toContainText('The Plugin has been successfully created.');

    await expect(page.locator('#maincolumn')).toContainText('Test Plugin');

    await expect(page.getByRole('link', { name: ' Download latest' })).toBeVisible();

    await expect(page.getByRole('blockquote')).toContainText('I am here for testing purpose');

    await expect(page.getByRole('link', { name: 'About', exact: true })).toBeVisible();

    await expect(page.locator('#plugin-about')).toContainText('I was built for testing purpose');

    await page.getByRole('link', { name: 'Details' }).click();

    await expect(page.getByText('Author', { exact: true })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Kartoza', exact: true })).toBeVisible();

    await page.getByRole('link', { name: 'Versions' }).click();

    await expect(page.getByRole('link', { name: '0.0.1' })).toBeVisible();

    await page.getByRole('link', { name: 'Manage' }).click();

    await expect(page.getByRole('link', { name: 'Edit' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Add version' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Tokens' })).toBeVisible();

    await expect(page.getByRole('button', { name: 'Set featured' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Delete' })).toBeVisible();

    await page.getByRole('button', { name: '×' }).click();

    await page.getByRole('link', { name: 'My plugins' }).click();

    await expect(page.locator('#list_commands')).toContainText('3 records found');

    await expect(page.getByRole('link', { name: 'Coffee Plugin' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Pizza Plugin' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Test Plugin', exact: true })).toBeVisible();

    await page.getByRole('link', { name: 'All' }).click();

    await page.getByRole('link', { name: 'Stable' }).click();

    await expect(page.locator('#list_commands')).toContainText('2 records found');

    await page.getByRole('link', { name: 'New Plugins' }).click();

    await expect(page.locator('#list_commands')).toContainText('1 records found');

    await expect(page.getByRole('link', { name: 'Test Plugin', exact: true })).toBeVisible();

    await page.getByRole('link', { name: 'My plugins' }).click();

  });

  test('test plugin delete', async ({ page }) => {
    await page.goto(url);

    await page.getByRole('link', { name: 'Plugins', exact: true }).click();

    await page.waitForURL('**/plugins/');

    await expect(page.locator('#list_commands')).toContainText('2 records found');

    await page.getByRole('link', { name: 'Test Plugin', exact: true }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS Python Plugins Repository');

    await expect(page.getByRole('heading', { name: 'Test Plugin' })).toBeVisible();

    await expect(page.getByRole('link', { name: ' Download latest' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Manage' })).toBeVisible();

    await page.getByRole('link', { name: 'Manage' }).click();

    await expect(page.getByRole('link', { name: 'Delete' })).toBeVisible();

    await page.getByRole('link', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete plugin:');

    await expect(page.locator('#maincolumn')).toContainText('You asked to delete the plugin and all its versions. The plugin will be permanently deleted. This action cannot be undone. Please confirm.');

    await page.getByRole('button', { name: 'Ok' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× The Plugin has been successfully deleted.');

    await expect(page.locator('#maincolumn')).toContainText('All plugins');

    await expect(page.locator('#list_commands')).toContainText('1 records found');

    await expect(page.getByRole('link', { name: 'Coffee Plugin' })).toBeVisible();
  });

});