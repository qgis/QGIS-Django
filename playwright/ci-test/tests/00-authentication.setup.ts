import { test, expect } from '@playwright/test';

let url = '/';
const username = 'admin';
const password = 'admin';
const authFile = 'auth.json';

test('authentication-setup', async ({ page }) => {
  await page.goto(url);

  const initialURL = page.url();

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: 'Login' })).toBeVisible();

  await page.getByRole('link', { name: 'Login' }).click();

  await page.waitForURL('**/accounts/login/');

  await expect(page.locator('#maincolumn')).toContainText('Login using your OSGEO id.');

  await expect(page.locator('#maincolumn')).toContainText('Please note that you do not need a login to download a plugin.');

  await expect(page.locator('#maincolumn')).toContainText('You can create a new OSGEO id on OSGEO web portal.');

  await expect(page.getByRole('link', { name: 'OSGEO web portal.' })).toBeVisible();

  await page.getByLabel('User name:').click();

  await page.getByLabel('User name:').fill(username);

  await page.getByLabel('Password:').click();

  await page.getByLabel('Password:').fill(password);

  await expect(page.getByRole('button', { name: 'login' })).toBeVisible();

  await page.getByRole('button', { name: 'login' }).click();

  const finalURL = page.url();

  await expect(initialURL).toBe(finalURL);

  await expect(page.getByRole('link', { name: 'Logout' })).toBeVisible();

  await expect(page.locator('h2')).toContainText('QGIS plugins web portal');

  await expect(page.getByRole('link', { name: '' })).toBeVisible();

  await page.context().storageState({path: authFile});

});