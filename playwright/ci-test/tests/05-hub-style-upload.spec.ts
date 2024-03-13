import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('style uploads', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('test style upload', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Styles' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS Style');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await page.getByRole('link', { name: ' Upload Style' }).click();

    const fileChooserPromise = page.waitForEvent('filechooser');

    await page.getByLabel('Style file:').click();

    const fileChooser = await fileChooserPromise;

    //await page.getByLabel('Style file:').setInputFiles('point.xml');

    await fileChooser.setFiles('tests/fixtures/point.xml');

    const fileChooserPromise2 = page.waitForEvent('filechooser');

    await page.getByLabel('Thumbnail:').click();

    const fileChooser2 = await fileChooserPromise2;

    //await page.getByLabel('Thumbnail:').setInputFiles('qgis-icon.png');
    await fileChooser2.setFiles('tests/fixtures/qgis_thumbnail.png');

    await page.getByLabel('Description:').click();

    await page.getByLabel('Description:').fill('This is a test file.');

    await page.getByLabel('I confirm that I own these').check();

    await page.getByRole('button', { name: 'Upload' }).click();

    await page.waitForLoadState('load');

    await expect(page.getByText('× The Style has been')).toBeVisible();

    await expect(page.locator('#maincolumn')).toContainText('× The Style has been successfully created.');

    await expect(page.getByRole('heading', { name: 'Custompoint in review' })).toBeVisible();

    await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

    await expect(page.getByText('Custompoint', { exact: true })).toBeVisible();

    await page.getByPlaceholder('Please provide clear feedback').click();

    await page.getByPlaceholder('Please provide clear feedback').fill('All good.');

    await page.getByRole('button', { name: 'Submit Review' }).click();

    await expect(page.getByText('× The Style has been approved.')).toBeVisible();

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.getByRole('link', { name: 'Custompoint' })).toBeVisible();

    await expect(page.getByRole('link', { name: 'Marker' })).toBeVisible();

    await page.getByRole('link', { name: 'Marker' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Marker Styles');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Styles');

    await expect(page.locator('#maincolumn')).toContainText('2 records found.');

  });

  test('test style delete', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Styles' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Styles');

    await expect(page.locator('#maincolumn')).toContainText('2 records found.');

    await page.getByRole('link', { name: 'Custompoint Admin' }).click();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete Style: Custompoint');

    await expect(page.locator('#maincolumn')).toContainText('Are you sure you want to permanently remove this Style?');

    await expect(page.getByRole('button', { name: 'Delete' })).toBeVisible();

    await page.getByRole('button', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Styles');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');
  });

});
