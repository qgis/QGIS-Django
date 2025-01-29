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

  await page.getByRole('menuitem', { name: '3D Models' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS 3D Model');

  await expect(page.locator('#maincolumn')).toContainText('All 3D Models');

  await expect(page.locator('#maincolumn')).toContainText('24 records found.');

  await expect(page.getByRole('link', { name: ' Upload 3D Model' })).toBeVisible();

  await expect(page.getByRole('heading', { name: '3D Model', exact: true })).toBeVisible();

  await expect(page.locator('.frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(2) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('#maincolumn div').filter({ hasText: 'Car Sedan Klas Karlsson | 04' }).nth(3)).toBeVisible();

  await expect(page.locator('#maincolumn div').filter({ hasText: 'Tree Tall Pine-ish Klas' }).nth(3)).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(7) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.locator('#maincolumn')).toContainText('24 records found.');

  await expect(page.getByRole('row', { name: 'Style icon QGIS Logo A 3D' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS Logo' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon QGIS_logo_Q' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'QGIS_logo_Q' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon donut_03 Blender' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'donut_03' })).toBeVisible();
  
});