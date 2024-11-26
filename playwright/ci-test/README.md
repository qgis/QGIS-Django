# Validation Tests

These tests are designed to run from GitHub action or CI.

They are intended to verify basic functionality is working during the building of the application(Just before deployment to staging or production).

## Essential reading:

* [https://playwright.dev/](https://playwright.dev/)
* [https://playwright.dev/docs/ci-intro](https://playwright.dev/docs/ci-intro)
* [https://direnv.net/docs/installation.html](https://direnv.net/docs/installation.html)

## Setting up your environment

Before you can run, you need to set up your environment.

Running these tests requires playwright set up on your local machine, as well as NodeJS.

### NixOS

If you are a NixOS user, you can set up direnv and then cd into this directory in your shell.

When you do so the first time, you will be prompted to allow direnv which you can do using this command:

```bash
direnv allow
```

>  This may take a while the first time as NixOS builds you a sandbox environment.

### Non-NixOS

For a non-NixOS user(Debian/Ubuntu) set up your environment by the following commands:

```bash
npm install
```

To install playwright browsers with OS-level dependencies use:

```bash
npx playwright install --with-deps chromium
```

**NOTE:** This only works with Debian/Ubuntu as they receive official support from playwright. It will also request your master password to install the dependencies.

## Recording a test

There is a bash helper script that will let you quickly create a new test:

```
Usage: ./record-test.sh TESTNAME
e.g. ./record-test.sh mytest
will write a new test to tests/mytest.spec.ts
Do not use spaces in your test name.
Test files MUST END in .spec.ts

After recording your test, close the test browser.
You can then run your test by doing:
./run-tests.sh
```

>  The first time you record a test, it will store your session credentials in a file ending in ``auth.json``. This file should **NEVER** be committed to git / shared publicly. There is a gitignore rule to ensure this.

## Running a test

By default, this will run in `headless` mode just as it is in CI.

```bash
./run-tests.sh
```

**NOTE:** To run it in `UI` mode, add the `--ui` tag to the script.

```bash
$PLAYWRIGHT \
    test \
    --ui \
    --project chromium
```

## Adding a CI test

To add tests for CI, use the recorded tests then modify it for CI.

The tests can be modified to include time-outs, and waiting for events/actions etc. For more look go through [playwright's documentation](https://playwright.dev/docs/writing-tests).

An example of a line-recorded test would look like:

```typescript
await page.getByRole('img', { name: 'image' }).click();
```

For the CI the line could be modified and turned into an assertion using `expect` to test if the specific element is visible.

```typescript
await expect(page.getByRole('img', { name: 'image' })).toBeVisible();
```
