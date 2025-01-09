import { test, expect } from '@playwright/test';

test.use({
  storageState: 'auth.json'
});

let coffePluginUrl = '/plugins/CoffeePlugin/'

test.describe('plugins upload', () => {
    test.beforeEach(async ({ page }) => {
      // Go to the coffee plugin url before each test.
      await page.goto(coffePluginUrl);
    });

    test('Version feedback', async ({ page }) => {
        await expect(page.getByRole('link', { name: 'Versions' })).toBeVisible();
        await page.getByRole('link', { name: 'Versions' }).click();
        await expect(page.getByRole('link', { name: '1.4' })).toBeVisible();
        await expect(page.getByRole('link', { name: '1.3' })).toBeVisible();
        await expect(page.getByRole('link', { name: '1.2' })).toBeVisible();
        await expect(page.getByText('Nov 24, 2010').first()).toBeVisible();
        await expect(page.getByRole('row', { name: '1.4 yes yes 1.0.0 None 1' }).locator('#version_unapprove')).toBeVisible();
        await expect(page.getByRole('link', { name: '' }).first()).toBeVisible();
        await expect(page.getByRole('link', { name: '' }).first()).toBeVisible();
        await expect(page.getByRole('link', { name: '' }).first()).toBeVisible();
        await page.getByRole('row', { name: '1.4 yes yes 1.0.0 None 1' }).locator('#version_unapprove').click();
        await page.getByRole('link', { name: 'Versions' }).click();
        await page.getByRole('link', { name: '' }).first().click();
        await expect(page.getByRole('heading', { name: 'Feedback Plugin Coffee Plugin' })).toBeVisible();
        await expect(page.getByText('Please tick the checkbox when')).toBeVisible();
        await expect(page.getByText('New Feedback', { exact: true })).toBeVisible();
        await expect(page.getByPlaceholder('Please provide clear feedback')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Submit New Feedback' })).toBeVisible();
        await expect(page.getByPlaceholder('Please provide clear feedback')).toBeEmpty();
        await page.getByPlaceholder('Please provide clear feedback').click();
        await page.getByPlaceholder('Please provide clear feedback').fill('This is a new feedback');
        await page.getByRole('button', { name: 'Submit New Feedback' }).click();
        await expect(page.getByText('This is a new feedback').first()).toBeVisible();

    });

    test('Version edit', async ({ page }) => {
        await page.getByRole('link', { name: 'Versions' }).click();
        await page.getByRole('link', { name: '' }).first().click();
        await expect(page.getByText('required field.')).toBeVisible();
        await expect(page.getByText('Plugin package:')).toBeVisible();
        await expect(page.getByLabel('Plugin package:')).toBeVisible();
        await expect(page.getByText('Experimental flag')).toBeVisible();
        await expect(page.getByText('Check this box if this')).toBeVisible();
        await expect(page.getByText('Changelog:')).toBeVisible();
        await expect(page.getByLabel('Changelog:')).toBeVisible();
        // await expect(page.getByLabel('Changelog:')).toBeEmpty();
        await expect(page.getByText('Insert here a short')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
    });

    test('Version delete', async ({ page }) => {
        await page.getByRole('link', { name: 'Versions' }).click();
        await page.getByRole('link', { name: '' }).nth(2).click();
        await expect(page.getByRole('heading', { name: 'Delete version "1.2" of "' })).toBeVisible();
        await expect(page.getByText('You asked to delete one')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Ok' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Cancel' })).toBeVisible();
        await page.getByRole('button', { name: 'Ok' }).click();
    });

    test('Plugin edit', async ({ page }) => {
        await page.getByRole('link', { name: 'Manage' }).click();
        await expect(page.getByRole('link', { name: 'Edit' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Add version' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Tokens' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Set featured' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Delete' })).toBeVisible();
        await page.getByRole('link', { name: 'Edit' }).click();
        await expect(page.getByRole('heading', { name: 'Edit plugin [1] Coffee Plugin' })).toBeVisible();
        await expect(page.getByText('required field.')).toBeVisible();
        await expect(page.getByText('Description:')).toBeVisible();
        await expect(page.getByLabel('Description:')).toBeVisible();
        await expect(page.getByLabel('Description:')).toHaveValue('A Plugin for making coffee');
        await expect(page.getByText('About:')).toBeVisible();
        await expect(page.getByLabel('About:')).toBeVisible();
        await expect(page.getByLabel('About:')).toBeEmpty();
        await expect(page.getByText('Author:')).toBeVisible();
        await expect(page.getByLabel('Author:')).toBeEmpty();
        await expect(page.getByText('This is the plugin\'s original')).toBeVisible();
        await expect(page.getByText('Author email:')).toBeVisible();
        await expect(page.getByLabel('Author email:')).toBeVisible();
        await expect(page.getByLabel('Author email:')).toBeEmpty();
        await expect(page.getByText('Icon:')).toBeVisible();
        await expect(page.getByLabel('Icon:')).toBeVisible();
        await expect(page.getByLabel('Icon:')).toBeEmpty();
        await expect(page.locator('#maincolumn').getByText('Deprecated')).toBeVisible();
        await expect(page.getByLabel('Deprecated')).not.toBeChecked();
        await expect(page.getByText('Plugin homepage:')).toBeVisible();
        await expect(page.getByLabel('Plugin homepage:')).toBeVisible();
        await expect(page.getByLabel('Plugin homepage:')).toBeEmpty();
        await expect(page.getByText('Tracker:')).toBeVisible();
        await expect(page.getByLabel('Tracker:')).toBeEmpty();
        await expect(page.getByText('Code repository:')).toBeVisible();
        await expect(page.getByLabel('Code repository:')).toBeEmpty();
        await expect(page.locator('ul').filter({ hasText: 'creator' })).toBeVisible();
        await expect(page.getByText('Maintainer:')).toBeVisible();
        await expect(page.getByLabel('Maintainer:')).toBeVisible();
        await expect(page.getByLabel('Maintainer:')).toHaveValue('1');
        await expect(page.getByText('Display "Created by" in')).toBeVisible();
        await expect(page.getByLabel('Display "Created by" in')).toBeVisible();
        await expect(page.getByLabel('Display "Created by" in')).not.toBeChecked();
        await expect(page.getByText('Tags:')).toBeVisible();
        await expect(page.locator('#id_tags__tagautosuggest')).toBeVisible();
        await expect(page.locator('#id_tags__tagautosuggest')).toHaveValue('Enter Tag Here');
        await expect(page.getByText('Server', { exact: true })).toBeVisible();
        await expect(page.getByLabel('Server')).not.toBeChecked();
        await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
    });

    test('Add version', async ({ page }) => {
        await page.getByRole('link', { name: 'Manage' }).click();
        await page.getByRole('link', { name: 'Add version' }).click();
        await expect(page.getByRole('heading', { name: 'New version for plugin' })).toBeVisible();
        await expect(page.getByText('required field.')).toBeVisible();
        await expect(page.getByText('Plugin package:')).toBeVisible();
        await expect(page.getByLabel('Plugin package:')).toBeVisible();
        await expect(page.getByLabel('Plugin package:')).toBeEmpty();
        await expect(page.getByText('Experimental flag')).toBeVisible();
        await expect(page.getByLabel('Experimental flag')).not.toBeChecked();
        await expect(page.getByText('Check this box if this')).toBeVisible();
        await expect(page.getByText('Changelog:')).toBeVisible();
        await expect(page.getByLabel('Changelog:')).toBeVisible();
        await expect(page.getByLabel('Changelog:')).toBeEmpty();
        await expect(page.getByText('Insert here a short')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();

    });

    test('Add token', async ({ page }) => {
        await page.getByRole('link', { name: 'Manage' }).click();
        await page.getByRole('link', { name: 'Tokens' }).click();
        await expect(page.getByRole('heading', { name: 'Tokens for Coffee Plugin' })).toBeVisible();
        await expect(page.getByRole('button', { name: ' Generate a New Token' })).toBeVisible();
        await page.getByRole('button', { name: ' Generate a New Token' }).click();
        await expect(page.getByText('× To enhance the security of')).toBeVisible();
        await expect(page.locator('dd').filter({ hasText: 'admin' })).toBeVisible();
        await expect(page.getByText('User')).toBeVisible();
        await expect(page.getByText('Jti')).toBeVisible();
        await expect(page.getByText('Created at')).toBeVisible();
        await expect(page.getByText('Expires at')).toBeVisible();
        await expect(page.getByText('Access token')).toBeVisible();
        await expect(page.getByRole('link', { name: 'Back to the list' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Edit description' })).toBeVisible();
        await page.getByRole('link', { name: 'Edit description' }).click();
        await expect(page.getByRole('heading', { name: 'Edit token description' })).toBeVisible();
        await expect(page.getByText('Description:')).toBeVisible();
        await expect(page.getByLabel('Description:')).toBeVisible();
        await expect(page.getByLabel('Description:')).toBeEmpty();
        await expect(page.getByText('Describe this token so that')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
        await page.getByLabel('Description:').click();
        await page.getByLabel('Description:').fill('My new token');
        await page.getByRole('button', { name: 'Save' }).click();
        await expect(page.getByText('× The token description has')).toBeVisible();
        await expect(page.getByRole('cell', { name: 'admin' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'My new token' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'User' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'Description' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'Created at' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'Last used at' }).first()).toBeVisible();
        await expect(page.getByRole('cell', { name: 'Manage' }).first()).toBeVisible();
        await expect(page.getByRole('link', { name: '' }).first()).toBeVisible();
        await expect(page.getByRole('link', { name: '' }).first()).toBeVisible();
        await page.getByRole('link', { name: '' }).first().click();
        await expect(page.getByLabel('Description:')).toHaveValue('My new token');
    });

    test('Delete token', async ({ page }) => {
        await page.getByRole('link', { name: 'Manage' }).click();
        await page.getByRole('link', { name: 'Tokens' }).click();
        await page.getByRole('link', { name: '' }).first().click();
        await expect(page.getByText('You asked to delete a token.')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Ok' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Cancel' })).toBeVisible();
        await page.getByRole('button', { name: 'Ok' }).click();
        await expect(page.getByText('× The token has been')).toBeVisible();
        await expect(page.locator('#maincolumn')).toContainText('The token has been successfully deleted.');
    });

    test('Set featured', async ({ page }) => {
        await page.getByRole('link', { name: 'Manage' }).click();
        await page.getByRole('button', { name: 'Set featured' }).click();
        await expect(page.locator('#maincolumn')).toContainText('The plugin [1] Coffee Plugin is now a marked as featured.');
        await page.getByRole('link', { name: 'Manage' }).click();
        await page.getByRole('button', { name: 'Unset featured' }).click();
        await expect(page.locator('#maincolumn')).toContainText('The plugin [1] Coffee Plugin is not marked as featured anymore.');
    });

})