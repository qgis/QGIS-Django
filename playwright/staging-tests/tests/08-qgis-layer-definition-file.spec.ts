import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('test', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

  await page.getByRole('button', { name: 'Hub' }).click();

  await page.getByRole('menuitem', { name: 'QGIS Layer Definition File' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Layer Definition File');

  await expect(page.locator('#maincolumn')).toContainText('All Layer Definition Files');

  await expect(page.locator('#maincolumn')).toContainText('1 record found.');

  await expect(page.getByRole('link', { name: ' Upload Layer Definition File' })).toBeVisible();

  await expect(page.locator('.frame-image-demo')).toBeVisible();

  await page.locator('.frame-image-demo').click();

  await expect(page.locator('#maincolumn')).toContainText('swisstopo Vector Tiles');

  await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'https://vectortiles.geo.admin' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Layer Definition File', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.locator('#maincolumn')).toContainText('1 record found.');

  await expect(page.getByRole('img', { name: 'Style icon' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'swisstopo Vector Tiles' })).toBeVisible();
  
});