import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('styles', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

  await page.getByRole('button', { name: 'Hub' }).click();

  await page.getByRole('menuitem', { name: 'Styles' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.locator('#maincolumn')).toContainText('All Styles');

  await expect(page.locator('#maincolumn')).toContainText('1 record found.');

  await expect(page.locator('.frame-image-demo')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Cube Creator | 17 November' })).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload Style' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Approved' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Waiting Review' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Requiring Update' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'Cube Creator' })).toBeVisible();

  //await page.waitForURL('**/styles/?order_by=-upload_date&&is_gallery=true');

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.getByRole('link', { name: 'Cube' })).toBeVisible();

  await page.getByRole('link', { name: 'Waiting Review' }).click();

  await expect(page.locator('#maincolumn')).toContainText('1 record found.');

  //await page.getByRole('link', { name: 'New Cube Style' }).click();

  await expect(page.getByRole('link', { name: 'New Cube Style' })).toBeVisible();

  await page.getByRole('link', { name: 'Requiring Update' }).click();

  await expect(page.locator('#maincolumn')).toContainText('Requiring Update');

  await expect(page.locator('#maincolumn')).toContainText('1 record found.');

  await expect(page.getByRole('link', { name: 'Another Cube' })).toBeVisible();

  await expect(page.locator('#collapse-related-plugins')).toContainText('Style Type');

  //await page.getByRole('link', { name: 'Symbol 3D' }).click();

  await expect(page.getByRole('link', { name: 'Cube' })).toBeVisible();
});
