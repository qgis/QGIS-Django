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

  await page.getByRole('menuitem', { name: 'Styles' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.locator('#maincolumn')).toContainText('163 records found.');

  await expect(page.getByRole('heading', { name: 'All Styles' })).toBeVisible();

  await expect(page.locator('.frame-image-demo > a:nth-child(2)').first()).toBeVisible();

  await expect(page.locator('div:nth-child(2) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(3) > .galery > .frame-image-demo').first()).toBeVisible();

  await expect(page.locator('#maincolumn div').filter({ hasText: 'Функціональне Призначення Територій Проектне Території Закладів З Обслуговування' }).nth(3)).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(2) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.locator('div:nth-child(6) > div:nth-child(3) > .galery > .frame-image-demo')).toBeVisible();

  await expect(page.getByRole('link', { name: ' Upload Style' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Style', exact: true })).toBeVisible();

  await page.getByRole('link', { name: 'Approved' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.getByRole('cell', { name: 'Name  ' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Type  ' })).toBeVisible();

  await expect(page.getByRole('cell', { name: '  ' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Creator  ' })).toBeVisible();

  await expect(page.getByRole('cell', { name: 'Upload Date  ' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Elevation Ramp' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Elevation Ramp' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Bite Of My' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Bite Of My Sandwich' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Bite Of My' }).getByRole('link').nth(1)).toBeVisible();

  const downloadPromise = page.waitForEvent('download');

  await page.getByRole('row', { name: 'Style icon Elevation Ramp' }).getByRole('link').nth(1).click();

  const download = await downloadPromise;

  await expect(page.getByRole('heading', { name: 'Style Type' })).toBeVisible();

  await page.getByRole('link', { name: 'Color Ramp' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.getByRole('heading', { name: 'Color Ramp Styles' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('14 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Elevation Ramp' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Elevation Ramp' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Elevation Ramp' }).getByRole('link').nth(1)).toBeVisible();

  await page.getByRole('link', { name: '' }).click();

  await page.getByRole('link', { name: '' }).click();

  await expect(page.locator('.frame-image-demo').first()).toBeVisible();

  await expect(page.locator('div:nth-child(2) > .galery > .frame-image-demo').first()).toBeVisible();

  await page.getByRole('link', { name: '' }).click();

  await page.getByRole('link', { name: 'Elevation Ramp' }).click();

  await expect(page.getByRole('heading', { name: 'Elevation Ramp' })).toBeVisible();

  await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

  await expect(page.getByRole('link', { name: ' Download' })).toBeVisible();

  await page.getByRole('heading', { name: 'QGIS Style' }).click();

  await page.getByRole('link', { name: 'Fill' }).click();

  await expect(page.getByRole('heading', { name: 'QGIS Style' })).toBeVisible();

  await expect(page.getByRole('heading', { name: 'Fill Styles' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('81 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Dormido Rough Fill' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Dormido Rough' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Bricks Fill 1506' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Bricks' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Denim Fill 943' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Denim' })).toBeVisible();

  await page.getByRole('link', { name: 'Line' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.getByRole('heading', { name: 'Line Styles' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('29 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Barb Wire Line' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Barb Wire' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Measure Line Line' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Measure Line' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Pen, Pencil and' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Pen, Pencil and more' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Zipper Line 1070' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Zipper' })).toBeVisible();

  await page.getByRole('link', { name: 'Legend Patch' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.getByRole('heading', { name: 'Legend Patch Styles' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('6 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Bite Of My' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Bite Of My Sandwich' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Italian regions' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Italian regions' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Basic Legend' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Basic Legend Patches Set' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon States Brazil' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'States Brazil' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Brasilian Biomes' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Brasilian Biomes' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon Philippines' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Philippines Administrative' })).toBeVisible();

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await page.getByRole('link', { name: 'Marker' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await expect(page.getByRole('heading', { name: 'Marker Styles' })).toBeVisible();

  await expect(page.locator('#maincolumn')).toContainText('33 records found.');

  await expect(page.getByRole('row', { name: 'Style icon Summer Travel' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'Summer Travel Vectors -' })).toBeVisible();

  await expect(page.locator('tr:nth-child(2) > td').first()).toBeVisible();

  await expect(page.getByRole('link', { name: '国土空间总体规划样式库：用地用海分类配色指引表' })).toBeVisible();

  await expect(page.getByRole('row', { name: 'Style icon ABK Symbole NRW' }).getByRole('img')).toBeVisible();

  await expect(page.getByRole('link', { name: 'ABK Symbole NRW' })).toBeVisible();

  await page.getByRole('link', { name: 'Labelsetting' }).click();

  await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

  await page.getByRole('heading', { name: 'Labelsetting Styles' }).click();

  await expect(page.locator('#maincolumn')).toContainText('No data.');
});
