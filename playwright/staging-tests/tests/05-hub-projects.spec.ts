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

  await page.getByRole('menuitem', { name: 'Projects' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS GeoPackage');

  await expect(page.getByRole('heading', { name: 'All GeoPackages' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('10 records found.');

  await expect(page.locator('.frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(2) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(3) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(8) > .span4 > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload GeoPackage' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'GeoPackage', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.getByRole('heading', { name: 'All GeoPackages' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('10 records found.');

});
