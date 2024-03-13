import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('upload 3D models', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('test upload 3D models', async ({ page }) => {

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: '3D Models' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS 3D Model');

    await expect(page.locator('#maincolumn')).toContainText('All 3D Models');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await expect(page.getByRole('link', { name: ' Upload 3D Model' })).toBeVisible();

    await page.getByRole('link', { name: ' Upload 3D Model' }).click();

    const fileChooserPromise = page.waitForEvent('filechooser');

    await page.getByLabel('3D Model file:').click();

    const fileChooser = await fileChooserPromise;

    //await page.getByLabel('3D Model file:').setInputFiles('qgis-logo.zip');
    await fileChooser.setFiles('tests/fixtures/qgis-logo.zip');

    const fileChooserPromise2 = page.waitForEvent('filechooser');

    await page.getByLabel('Thumbnail:').click();

    const fileChooser2 = await fileChooserPromise2;

    await fileChooser2.setFiles('tests/fixtures/qgis_thumbnail.png');

    await page.getByLabel('Name:').click();

    await page.getByLabel('Name:').fill('Test 3D model');

    await page.getByLabel('Description:').click();

    await page.getByLabel('Description:').fill('This is a test.');

    await page.getByLabel('I confirm that I own these').check();

    await page.getByRole('button', { name: 'Upload' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× 3D Model was uploaded successfully.');

    await page.getByRole('button', { name: '×' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Test 3D model in review');

    await expect(page.getByRole('img', { name: 'image' }).first()).toBeVisible();

    await page.getByPlaceholder('Please provide clear feedback').click();

    await page.getByPlaceholder('Please provide clear feedback').fill('All good.');

    await page.getByRole('button', { name: 'Submit Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× The 3D Model has been approved.');

    await page.getByRole('button', { name: '×' }).click();

    await expect(page.getByRole('img', { name: 'image' }).first()).toBeVisible();

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All 3D Models');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: 'Test 3D model' })).toBeVisible();

    await expect(page.getByRole('img', { name: 'Style icon' })).toBeVisible();

    await page.getByRole('link', { name: 'Waiting Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Waiting Review');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await page.getByRole('link', { name: 'Requiring Update' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Requiring Update');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

    await expect(page.locator('header')).toContainText('Sustaining Members');

  });

  test('test delete 3D models', async ({ page }) => {

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: '3D Models' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS 3D Model');

    await expect(page.locator('#maincolumn')).toContainText('All 3D Models');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await page.getByRole('link', { name: '' }).click();

    await expect(page.getByRole('link', { name: 'Test 3D model' })).toBeVisible();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete 3D Model: Test 3D model');

    await expect(page.locator('#maincolumn')).toContainText('Are you sure you want to permanently remove this 3D Model?');

    await page.getByRole('button', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All 3D Models');

    await expect(page.locator('#maincolumn')).toContainText('No data.');
    
  });

});
