import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('models', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('test models uploads', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Models', exact: true }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Models');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await expect(page.getByRole('link', { name: ' Upload Model' })).toBeVisible();

    await page.getByRole('link', { name: ' Upload Model' }).click();

    const fileChooserPromise = page.waitForEvent('filechooser');

    await page.getByLabel('Model file:').click();

    const fileChooser = await fileChooserPromise;

    //await page.getByLabel('Model file:').setInputFiles('example.model3');
    await fileChooser.setFiles('tests/fixtures/example.model3');

    const fileChooserPromise2 = page.waitForEvent('filechooser');

    await page.getByLabel('Thumbnail:').click();

    const fileChooser2 = await fileChooserPromise2;

    //await page.getByLabel('Thumbnail:').setInputFiles('qgis-icon.png');
    await fileChooser2.setFiles('tests/fixtures/thumbnail.png');

    await page.getByLabel('Name:').click();

    await page.getByLabel('Name:').fill('Test model');

    await page.getByLabel('Description:').click();

    await page.getByLabel('Description:').fill('This is a test file.');

    await page.getByLabel('I confirm that I own these').check();

    await page.getByRole('button', { name: 'Upload' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× Model was uploaded successfully.');

    await expect(page.getByText('Model was uploaded')).toBeVisible();

    await expect(page.locator('#maincolumn')).toContainText('Test model in review');

    await expect(page.getByRole('heading', { name: 'Test model in review' })).toBeVisible();

    await page.getByPlaceholder('Please provide clear feedback').click();

    await page.getByPlaceholder('Please provide clear feedback').fill('All good.');

    await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

    await page.getByRole('button', { name: 'Submit Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× The Model has been approved.');

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Models');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: 'Test model' })).toBeVisible();

    await expect(page.getByRole('img', { name: 'Style icon' })).toBeVisible();

  });

  test('test model delete', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Models', exact: true }).click();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Models');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: 'Test model' })).toBeVisible();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete Model: Test model');

    await expect(page.locator('#maincolumn')).toContainText('Are you sure you want to permanently remove this Model?');

    await page.getByRole('button', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All Models');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

  });

});