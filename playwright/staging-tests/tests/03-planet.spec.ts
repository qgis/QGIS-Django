import { test, expect } from '@playwright/test';

let url = '/';

test.use({
  storageState: 'auth.json'
});

test('test', async ({ page }) => {
  await page.goto(url);

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: 'Planet' })).toBeVisible();

  await page.getByRole('link', { name: 'Planet' }).click();

  await expect(page.getByRole('heading', { name: 'QGIS Planet' })).toBeVisible();

  await expect(page.getByRole('link', { name: 'New point clouds and mesh' })).toBeVisible();

  await expect(page.locator('#render-point-clouds-as-a-surface-in-2d-map-views')).toContainText('Render point clouds as a surface in 2D map views');

  await expect(page.getByRole('img', { name: 'Point clouds as surface', exact: true })).toBeVisible();

  await expect(page.getByRole('img', { name: 'Point clouds as surface with' })).toBeVisible();

  await expect(page.getByText('Point clouds as surface with')).toBeVisible();

  await expect(page.getByRole('img', { name: 'Point clouds styling panel' })).toBeVisible();

  await expect(page.locator('#flexible-styling-of-classes')).toContainText('Flexible styling of classes');

  await expect(page.getByRole('img', { name: 'Assigning size and opacity to' })).toBeVisible();

  await expect(page.getByRole('img', { name: 'Point clouds with different' })).toBeVisible();

  await expect(page.locator('#set-3d-map-view-extent-in-2d-map')).toContainText('Set 3D map view extent in 2D map');

  await expect(page.getByRole('img', { name: 'Interactive selection of 3D' })).toBeVisible();

  await expect(page.locator('#python-api-for-3d-views')).toContainText('Python API for 3D views');

  await expect(page.getByRole('img', { name: 'Changing 3D view settings' })).toBeVisible();

  await expect(page.locator('#more-point-clouds-attributes')).toContainText('More point clouds attributes');

  await expect(page.locator('#performance-enhancement-for-rendering')).toContainText('Performance enhancement for rendering');

  await expect(page.locator('#labels-for-mesh-layer')).toContainText('Labels for mesh layer');

  await expect(page.getByRole('img', { name: 'Label settings for mesh layers' })).toBeVisible();

  await expect(page.getByRole('img', { name: 'Example of labels on a mesh' })).toBeVisible();

  await expect(page.locator('#want-more-changes-in-qgis')).toContainText('Want more changes in QGIS?');

  await expect(page.locator('section').filter({ hasText: 'Sustaining Members' })).toBeVisible();

  await expect(page.locator('header')).toContainText('Sustaining Members');

});
