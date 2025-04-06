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

  await page.getByRole('menuitem', { name: 'Models', exact: true }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Model');

  await expect(page.getByRole('heading', { name: 'All Models' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('23 records found.');

  await expect(page.locator('#maincolumn')).toContainText('QGIS Model');

  await expect(page.locator('.frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(2) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(3) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div > .galery > .frame-image-demo').first()).toBeVisible();
  
  await expect(page.locator('div:nth-child(6) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload Model' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Model', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.locator('#maincolumn')).toContainText('23 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Generate Global' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Generate Global MGRS GZD' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon MGRS 100km squares' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'MGRS 100km squares for' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'MGRS 100km squares for' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Generate Global' }).getByRole('link').nth(1)).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon MGRS 100km squares' }).getByRole('link').nth(1)).toBeVisible();

});
