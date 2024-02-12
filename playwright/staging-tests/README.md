# Validation Tests

These tests are designed to run from your local machine (i.e. not from a GitHub action or CI).
The are intended to verify basic functionality is working after a deployment is made to staging, and prior to deployment to production.

## Essential reading:

* https://playwright.dev/
* https://direnv.net/docs/installation.html

## Setting up your environment

Before you can run or record tests, you need to set up your environment.

Running these tests require playwright set up on your local machine, as well as NodeJS.

**NixOS**

If you are a NixOS user, you can set up direnv and then cd into this directory in your shell.

When you do so the first time, you will be prompted to allow direnv which you can do using this command:


```
direnv allow
```

>  This may take a while the first time as NixOS builds you a sandbox environment.

**NON-NixOS**

For a non-NixOS user(Debian/Ubuntu) set up your environment by the following commands:

```bash
npm install
```

To install playwright browsers with OS-level dependencies use:


```bash
npm playwright install --with-deps chromium
```

**NOTE:** This only works with Debian/Ubuntu as they recieve official support from playwright. It will also request your master password to install the dependencies.

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


```
./run-tests.sh
```

