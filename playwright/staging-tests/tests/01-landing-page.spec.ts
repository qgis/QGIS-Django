import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('test', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: 'QGIS', exact: true })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Home' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'About plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Plugins', exact: true })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Planet' })).toBeVisible();

  await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Login' })).toBeVisible();

  await expect(page.getByPlaceholder('Search')).toBeVisible();

  await expect(page.getByPlaceholder('Search')).toBeEmpty();

  await expect(page.locator('#collapse-related-plugins')).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Featured plugins' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Processing R Provider' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Data Plotly' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Shape Tools' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Split Features On Steroids' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Plugin Builder' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Resource Sharing' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Lat Lon Tools' }).first()).toBeVisible();

  await expect(page.getByRole('link', { name: 'Serval' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'qgis2web' }).first()).toBeVisible();

  await expect(page.getByRole('link', { name: 'QuickMapServices' }).first()).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Updated plugins' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('QGIS plugins add additional functionality to the QGIS application.');

  await expect(page.locator('#maincolumn')).toContainText('There is a collection of plugins ready to be used, available to download. These plugins can also be installed directly from the QGIS Plugin Manager within the QGIS application.');

  await expect(page.getByRole('link', { name: 'available to download' })).toBeVisible();

  await page.getByRole('link', { name: 'available to download' }).click();

  await expect(page.getByRole('heading', { name: 'QGIS Python Plugins Repository' })).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload a plugin' })).toBeVisible();

  await page.getByRole('heading', { name: 'All plugins' }).click();

  await page.goto(url);

  await expect(page.locator('#maincolumn')).toContainText('Notes for plugin users');

  await expect(page.getByRole('link', { name: 'Developer mailing-list' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('Resources for plugin authors');

  await expect(page.getByRole('link', { name: 'pyQGIS cookbook' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Python API' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS C++ API' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'publish your plugins' })).toBeVisible();

  await expect(page.locator('#collapse-related-plugins')).toContainText('Popular plugins');

  await expect(page.getByRole('link', { name: 'QuickMapServices' }).nth(1)).toBeVisible();

  await expect(page.getByRole('link', { name: 'OpenLayers Plugin' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Semi-Automatic Classification' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'QuickOSM' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'mmqgis' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Profile tool' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Lat Lon Tools' }).nth(1)).toBeVisible();

  await expect(page.getByRole('link', { name: 'qgis2web' }).nth(1)).toBeVisible();

  await expect(page.getByRole('link', { name: 'Qgis2threejs' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'HCMGIS' })).toBeVisible();

  await expect(page.getByRole('button', { name: ' Plugin Tags ' })).toBeVisible();

  await expect(page.locator('#main_bg div').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Sustaining Members' })).toBeVisible();

  //await expect(page.getByRole('link', { name: 'Sustaining member logos' })).toBeVisible();
  await expect(page.locator('#twitter').getByRole('link')).toBeVisible();

  await expect(page.locator('#facebook').getByRole('link')).toBeVisible();

  await expect(page.locator('#github').getByRole('link')).toBeVisible();
  
  await expect(page.getByRole('contentinfo')).toBeVisible();
});
