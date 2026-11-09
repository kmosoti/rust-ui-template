const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

async function observeSlowTimers(page) {
  await page.addInitScript(() => {
    const set = window.setTimeout.bind(window);
    const clear = window.clearTimeout.bind(window);
    const slow = new Set();
    window.__slowTimersCleared = 0;
    window.setTimeout = (callback, delay, ...args) => {
      const id = set(callback, delay, ...args);
      if (delay === 1500) slow.add(id);
      return id;
    };
    window.clearTimeout = id => {
      if (slow.delete(id)) window.__slowTimersCleared++;
      return clear(id);
    };
  });
}

test('latest result survives a stale completion and cancellation preserves it', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await observeSlowTimers(page);
  await page.goto('/');
  const input = page.getByLabel('Number');
  const status = page.getByRole('status');
  await input.fill('11');
  await page.getByRole('button', { name: 'Slow request' }).click();
  await expect(status).toContainText('Request pending');
  await input.fill('22');
  await page.getByRole('button', { name: 'Fast request' }).click();
  await expect(status).toContainText('Latest result: 22');
  await page.waitForTimeout(1700);
  await expect(status).toContainText('Latest result: 22');
  await input.fill('33');
  await page.getByRole('button', { name: 'Slow request' }).click();
  const clearedBeforeCancel = await page.evaluate(() => window.__slowTimersCleared);
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect.poll(() => page.evaluate(() => window.__slowTimersCleared)).toBeGreaterThan(clearedBeforeCancel);
  await expect(status).toContainText('Request cancelled');
  await page.waitForTimeout(1700);
  await expect(status).toContainText('Latest result: 22');
  expect(errors).toEqual([]);
});

test('direct navigation and owner cleanup while a request is pending', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await observeSlowTimers(page);
  await page.goto('/#/about');
  await expect(page.getByRole('heading', { name: 'About' })).toBeVisible();
  await page.getByRole('link', { name: 'Latest response' }).click();
  await page.getByRole('button', { name: 'Slow request' }).click();
  await page.getByRole('link', { name: 'About' }).click();
  await expect.poll(() => page.evaluate(() => window.__slowTimersCleared)).toBeGreaterThan(0);
  await page.waitForTimeout(1700);
  await page.getByRole('link', { name: 'Latest response' }).click();
  await expect(page.getByRole('status')).toContainText('No result yet');
  expect(errors).toEqual([]);
});

test('keyboard and accessibility smoke', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Number').focus();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: 'Slow request' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('status')).toContainText('Request pending');
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});

test('production assets load under a subpath', async ({ page }) => {
  const failed = [];
  page.on('response', response => { if (response.status() >= 400) failed.push(response.url()); });
  await page.goto('/sub/#/about');
  await expect(page.getByRole('heading', { name: 'About' })).toBeVisible();
  await page.getByRole('link', { name: 'Latest response' }).click();
  await expect(page.getByRole('button', { name: 'Fast request' })).toHaveCSS('background-color', 'rgb(49, 87, 183)');
  await page.getByLabel('Number').fill('42');
  await page.getByRole('button', { name: 'Fast request' }).click();
  await expect(page.getByRole('status')).toContainText('Latest result: 42');
  expect(failed).toEqual([]);
});
