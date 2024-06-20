import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test.describe('projects', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto(url);
  });

  test('test projects upload', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Projects' }).click();

    await expect(page.locator('#maincolumn')).toContainText('QGIS GeoPackage');

    await expect(page.locator('#maincolumn')).toContainText('All GeoPackages');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

    await expect(page.getByRole('link', { name: ' Upload GeoPackage' })).toBeVisible();

    await page.getByRole('link', { name: ' Upload GeoPackage' }).click();

    const fileChooserPromise = page.waitForEvent('filechooser');
    
    await page.getByLabel('GeoPackage file:').click();

    //page.once('dialog', dialog => {
      //console.log(`Dialog message: ${dialog.message()}`);
      //dialog.dismiss().catch(() => { });
    //});

    const fileChooser = await fileChooserPromise;

    await fileChooser.setFiles('tests/fixtures/spiky_polygons.gpkg');

    //await page.getByLabel('GeoPackage file:').setInputFiles('spiky_polygons.gpkg');

    const fileChooserPromise2 = page.waitForEvent('filechooser');

    await page.getByLabel('Thumbnail:').click();

    const fileChooser2 = await fileChooserPromise2;

    //await page.getByLabel('Thumbnail:').setInputFiles('qgis-icon.png');
    await fileChooser2.setFiles('tests/fixtures/thumbnail.png');

    await page.getByLabel('Name:').click();

    await page.getByLabel('Name:').fill('Test gpkg');

    await page.getByLabel('Description:').click();

    await page.getByLabel('Description:').fill('This is a test file.');

    await page.getByLabel('I confirm that I own these').check();

    await page.getByRole('button', { name: 'Upload' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× GeoPackage was uploaded successfully.');

    await expect(page.getByText('GeoPackage was uploaded')).toBeVisible();

    await expect(page.locator('#maincolumn')).toContainText('Test gpkg in review');

    await expect(page.getByRole('img', { name: 'image' })).toBeVisible();

    await expect(page.getByText('Test gpkg', { exact: true })).toBeVisible();

    await page.getByPlaceholder('Please provide clear feedback').click();

    await page.getByPlaceholder('Please provide clear feedback').fill('All good.');

    await page.getByRole('button', { name: 'Submit Review' }).click();

    await expect(page.locator('#maincolumn')).toContainText('× The GeoPackage has been approved.');

    await expect(page.getByRole('heading', { name: 'Test gpkg' })).toBeVisible();

    await page.getByRole('link', { name: 'Approved' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All GeoPackages');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: 'Test gpkg' })).toBeVisible();

    await expect(page.getByRole('img', { name: 'Style icon' })).toBeVisible();

  });

  test('test projects delete', async ({ page }) => {
    await page.goto(url);

    await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

    await expect(page.getByRole('button', { name: 'Hub' })).toBeVisible();

    await page.getByRole('button', { name: 'Hub' }).click();

    await page.getByRole('menuitem', { name: 'Projects' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All GeoPackages');

    await expect(page.locator('#maincolumn')).toContainText('1 record found.');

    await expect(page.getByRole('link', { name: '' })).toBeVisible();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.getByRole('link', { name: 'Test gpkg' })).toBeVisible();

    await page.getByRole('link', { name: 'Test gpkg' }).click();

    await expect(page.getByRole('heading', { name: 'Test gpkg' })).toBeVisible();

    await page.getByRole('link', { name: '' }).click();

    await expect(page.locator('#maincolumn')).toContainText('Delete GeoPackage: Test gpkg');

    await expect(page.locator('#maincolumn')).toContainText('Are you sure you want to permanently remove this GeoPackage?');

    await page.getByRole('button', { name: 'Delete' }).click();

    await expect(page.locator('#maincolumn')).toContainText('All GeoPackages');

    await expect(page.locator('#maincolumn')).toContainText('No data.');

  });

});