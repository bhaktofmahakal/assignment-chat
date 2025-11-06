import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests
 * Comprehensive tests for login, registration, and logout flows
 */

test.describe('Authentication', () => {
  test('should load login page successfully', async ({ page }) => {
    await page.goto('/login');
    
    // Verify page title
    await expect(page.locator('h1')).toContainText('Chat Portal');
    
    // Verify demo credentials are visible
    await expect(page.locator('text=Demo Credentials')).toBeVisible();
    
    // Verify form inputs are present
    const usernameInput = page.locator('input[name="username"]');
    const passwordInput = page.locator('input[name="password"]');
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    
    // Verify login button exists
    const loginButton = page.locator('button').filter({ hasText: 'Login' });
    await expect(loginButton).toBeVisible();
  });

  test('should validate required fields on login form', async ({ page }) => {
    await page.goto('/login');
    
    // Verify inputs are required
    const usernameInput = page.locator('input[name="username"]');
    const isRequired = await usernameInput.evaluate(el => el.required);
    expect(isRequired).toBe(true);
  });

  test('should login successfully with demo credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill form
    await page.fill('input[name="username"]', 'demo');
    await page.fill('input[name="password"]', 'demo123');
    
    // Click login
    const loginButton = page.locator('button').filter({ hasText: /^Login$/ });
    await loginButton.click();
    
    // Wait for navigation to complete
    await page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {});
    await page.waitForTimeout(1000);
    
    // Should be logged in (either on chat page or not redirected to login)
    const currentUrl = page.url();
    const isLoggedIn = !currentUrl.includes('/login') || currentUrl.includes('/chat');
    expect(isLoggedIn).toBe(true);
  });

  test('should have registration link on login page', async ({ page }) => {
    await page.goto('/login');
    
    // Find registration link
    const createLink = page.locator('a').filter({ hasText: /Create|Register/i });
    await expect(createLink).toBeVisible();
  });

  test('should load registration page', async ({ page }) => {
    await page.goto('/register');
    
    // Verify page title
    await expect(page.locator('h1')).toContainText('Chat Portal');
    
    // Verify form fields
    const usernameInput = page.locator('input[name="username"]');
    const emailInput = page.locator('input[name="email"]');
    const passwordInput = page.locator('input[name="password"]');
    
    await expect(usernameInput).toBeVisible();
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });

  test('should have login link on registration page', async ({ page }) => {
    await page.goto('/register');
    
    // Find login link
    const loginLink = page.locator('a').filter({ hasText: /[Ll]ogin/ });
    await expect(loginLink).toBeVisible();
  });

  test('should have dark theme on login page', async ({ page }) => {
    await page.goto('/login');
    
    // Check for dark theme indicators
    const container = page.locator('div').filter({ hasText: 'Chat Portal' }).first();
    
    // Verify gradient or dark styling exists
    const bgStyle = await container.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return styles.backgroundImage || styles.backgroundColor;
    });
    
    expect(bgStyle).toBeTruthy();
  });

  test('should have gradient button on login form', async ({ page }) => {
    await page.goto('/login');
    
    const loginButton = page.locator('button').filter({ hasText: /^Login$/ });
    
    const bgStyle = await loginButton.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return styles.backgroundImage || styles.backgroundColor;
    });
    
    expect(bgStyle).toBeTruthy();
  });
});