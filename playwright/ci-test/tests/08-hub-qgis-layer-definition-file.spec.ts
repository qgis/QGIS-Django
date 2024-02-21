import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('qgis layer definition file', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('test qgis layer definition file upload', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'QGIS Layer Definition File' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS Layer Definition File');

    await expect(page.locator('#maincolumn')).toContainText('All Layer Definition Files');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await expect(page.getByRole('link', { name: ' Upload Layer Definition File' })).toBeVisible();

    await page.getByRole('link', { name: ' Upload Layer Definition File' }).click();

    await expect(page.getByRole('heading', { name: 'Upload Layer Definition File' })).toBeVisible();

    const fileChooserPromise = page.waitForEvent('filechooser');

    await page.getByLabel('Layer Definition file:').click();

    const fileChooser = await fileChooserPromise;

    await fileChooser.setFiles('tests/fixtures/my-vapour-pressure.qlr');

    const fileChooserPromise2 = page.waitForEvent('filechooser');

    await page.getByLabel('Thumbnail:').click();

    const fileChooser2 = await fileChooserPromise2;

    //await page.getByLabel('Thumbnail:').setInputFiles('qgis-icon.png');
    await fileChooser2.setFiles('tests/fixtures/qgis_thumbnail.png');

    await page.getByLabel('Name:').click();

    await page.getByLabel('Name:').fill('Test layer definition file');

    await page.getByLabel('Description:').click();

    await page.getByLabel('Description:').fill('This is a test.');

    await page.getByLabel('I confirm that I own these').check();

    await page.getByRole('button', { name: 'Upload' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Layer Definition File was uploaded successfully.');

    await expect(page.locator('#maincolumn')).toContainText('Test layer definition file in review');

    await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

    await expect(page.getByPlaceholder('Please provide clear feedback')).toBeVisible();

    await page.getByPlaceholder('Please provide clear feedback').click();

    await page.getByPlaceholder('Please provide clear feedback').fill('All good.');

    await page.getByRole('button', { name: 'Submit Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× The Layer Definition File has been approved.');

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Layer Definition Files');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: 'Test layer definition file' })).toBeVisible();

    await expect(page.getByRole('img', { name: 'Style icon' })).toBeVisible();

    await page.getByRole('link', { name: 'Waiting Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Waiting Review');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await page.getByRole('link', { name: 'Requiring Update' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Requiring Update');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await page.getByRole('link', { name: 'Approved' }).click();
  });

  test('test qgis layer definition delete', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'QGIS Layer Definition File' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Layer Definition Files');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await page.getByRole('link', { name: '' }).click();

    await expect(page.getByRole('link', { name: 'Test layer definition file' })).toBeVisible();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete Layer Definition File: Test layer definition file');

    await expect(page.locator('#maincolumn')).toContainText('Are you sure you want to permanently remove this Layer Definition File?');

    await page.getByRole('button', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Layer Definition Files');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

  });

});
