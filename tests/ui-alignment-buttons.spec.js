import { test, expect } from '@playwright/test';

test.describe('RIMBERIO Supply Chain Twin - UI, Buttons & Alignment Suite', () => {

  test('1. Landing Page: Verify Black Typography, Alignment & Navigation Buttons', async ({ page }) => {
    await page.goto('/');

    // Check main title presence & text (Matches research paper & PPT)
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText('SUPPLY CHAIN TWIN');
    await expect(heading).toContainText('ENTERPRISES');

    // Verify heading computed font color is black (rgb(0, 0, 0))
    const headingColor = await heading.evaluate((el) => window.getComputedStyle(el).color);
    expect(headingColor).toBe('rgb(0, 0, 0)');

    // Verify Sign In button is visible and clickable
    const signInBtn = page.getByRole('button', { name: 'Sign In' }).first();
    await expect(signInBtn).toBeVisible();

    // Verify Launch Platform / Get Started button is visible
    const launchBtn = page.getByRole('button', { name: /Launch Platform/i }).first();
    await expect(launchBtn).toBeVisible();

    // Verify Features Grid alignment (6 capability cards)
    const cards = page.locator('section:has-text("Core Platform Capabilities") .grid > div');
    const cardCount = await cards.count();
    expect(cardCount).toBeGreaterThanOrEqual(6);
  });

  test('2. Authentication Flow: Login Form, Controls & Transition to Dashboard', async ({ page }) => {
    await page.goto('/');

    // Click Sign In on landing page
    await page.getByRole('button', { name: 'Sign In' }).first().click();

    // Verify Login Page elements
    await expect(page.getByRole('heading', { name: 'ENTERPRISE SIGN IN' })).toBeVisible();
    const loginHeaderColor = await page.getByRole('heading', { name: 'ENTERPRISE SIGN IN' }).evaluate(el => window.getComputedStyle(el).color);
    expect(loginHeaderColor).toBe('rgb(0, 0, 0)');

    // Verify inputs
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toHaveValue('elena.rostova@rimberio.ai');

    // Verify password field & toggle
    const passInput = page.locator('input[placeholder="Enter your password"]');
    await expect(passInput).toBeVisible();
    await passInput.fill('securepass123');

    // Click submit
    const authBtn = page.getByRole('button', { name: /Authenticate & Launch Platform/i });
    await expect(authBtn).toBeVisible();
    await authBtn.click();

    // Should transition to Dashboard
    await expect(page.getByRole('heading', { name: 'SUPPLY CHAIN INTELLIGENCE DASHBOARD' })).toBeVisible();
  });

  test('3. Clean Navigation & Sidebar: Unwanted Features Removed', async ({ page }) => {
    await page.goto('/');
    // Login to access sidebar and header
    await page.getByRole('button', { name: 'Sign In' }).first().click();
    await page.getByRole('button', { name: /Authenticate & Launch Platform/i }).click();

    // Verify Header has NO Download ZIP button
    await expect(page.getByRole('button', { name: /Download Source/i })).toHaveCount(0);
    await expect(page.getByRole('button', { name: /Download Hub/i })).toHaveCount(0);

    // Verify Sidebar has NO "Auth Screens" section
    await expect(page.getByText('Auth Screens')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Download React Source' })).toHaveCount(0);

    // Verify only the 6 core platform tools are present in Sidebar
    const expectedSidebarItems = [
      'Intelligence Dashboard',
      'AI Negotiation Console',
      'Counterfactual Twin Sim',
      'Supplier Workspace',
      'Adaptive Decision Center',
      'Customer Impact & Notices',
      'Learning Loop & Confusion Mat',
      'Reports & Architecture',
    ];

    for (const item of expectedSidebarItems) {
      await expect(page.getByRole('button', { name: new RegExp(item, 'i') })).toBeVisible();
    }
  });

  test('4. Full Interactive Workspace: Buttons, Sliders, Views & Roles', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).first().click();
    await page.getByRole('button', { name: /Authenticate & Launch Platform/i }).click();

    // ─── Test Role Switcher in Header ───
    const roleBtn = page.getByRole('button', { name: /ROLE:/i });
    await expect(roleBtn).toBeVisible();
    await roleBtn.click();
    await expect(page.getByText('MULTI-AGENT ROLE ARCHITECTURE')).toBeVisible();
    await page.getByRole('button', { name: /Customer Impact Agent/i }).click();
    await expect(page.getByText(/ROLE: Customer Impact Agent/i)).toBeVisible();

    // ─── Test Customer Impact & Notices (Steps 7 & 8) ───
    await page.getByRole('button', { name: /Customer Impact & Notices/i }).click();
    await expect(page.getByRole('heading', { name: 'CUSTOMER IMPACT & NOTIFICATION ENGINE' })).toBeVisible();
    const batchNoticeBtn = page.getByRole('button', { name: /Dispatch All Pending Notices/i });
    await expect(batchNoticeBtn).toBeVisible();
    await batchNoticeBtn.click();
    await expect(page.getByText(/Batch Customer Notifications Dispatched/i)).toBeVisible();

    // ─── Test Learning Loop & Confusion Matrix (Step 9) ───
    await page.getByRole('button', { name: /Learning Loop & Confusion Mat/i }).click();
    await expect(page.getByRole('heading', { name: /PREDICTED VS. ACTUAL PERFORMANCE/i })).toBeVisible();
    await expect(page.getByText('Fig. 1: Confusion Matrix')).toBeVisible();
    const retrainBtn = page.getByRole('button', { name: /Retrain Twin Policy/i });
    await expect(retrainBtn).toBeVisible();
    await retrainBtn.click();
    await expect(page.getByText(/Model Feedback Applied/i)).toBeVisible();

    // ─── Test AI Negotiation Console ───
    await page.getByRole('button', { name: /AI Negotiation Console/i }).click();
    await expect(page.getByRole('heading', { name: 'AI NEGOTIATION CONSOLE' })).toBeVisible();

    const resumeBtn = page.getByRole('button', { name: /Agent Active|Resume Agent/i });
    await expect(resumeBtn).toBeVisible();
    await resumeBtn.click();

    const forceBtn = page.getByRole('button', { name: /Force Next Concession/i });
    await expect(forceBtn).toBeVisible();
    await forceBtn.click();

    // ─── Test Simulation Page ───
    await page.getByRole('button', { name: /Counterfactual Twin Sim/i }).click();
    await expect(page.getByRole('heading', { name: 'COUNTERFACTUAL TWIN SIMULATION' })).toBeVisible();
    const applyRecBtn = page.getByRole('button', { name: /Apply Recommended Mitigation/i });
    await expect(applyRecBtn).toBeVisible();

    // ─── Test Supplier Workspace ───
    await page.getByRole('button', { name: /Supplier Workspace/i }).click();
    await expect(page.getByRole('heading', { name: 'SUPPLIER INTELLIGENCE WORKSPACE' })).toBeVisible();
    const warningFilter = page.getByRole('button', { name: 'WARNING', exact: true });
    await expect(warningFilter).toBeVisible();
    await warningFilter.click();
    await expect(page.getByText('Shenzhen PCB Manufacturing')).toBeVisible();

    // ─── Test Decision Center ───
    await page.getByRole('button', { name: /Adaptive Decision Center/i }).click();
    await expect(page.getByRole('heading', { name: 'ADAPTIVE DECISION CENTER' })).toBeVisible();
    const applyOptionABtn = page.getByRole('button', { name: /Apply Option A/i });
    await expect(applyOptionABtn).toBeVisible();
    await applyOptionABtn.click();
    await expect(page.getByText('Mitigation Option A Applied Successfully')).toBeVisible();

    // ─── Test Reports Page ───
    await page.getByRole('button', { name: /Reports & Architecture/i }).click();
    await expect(page.getByRole('heading', { name: 'REPORTS & PLATFORM ARCHITECTURE' })).toBeVisible();
  });

  test('5. Precise Badge Alignment, Dimensions & Vertical Centering Checks', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).first().click();
    await page.getByRole('button', { name: /Authenticate & Launch Platform/i }).click();

    // Inspect the LIVE badge on the sidebar
    const liveBadge = page.locator('aside nav span.badge-healthy').first();
    await expect(liveBadge).toBeVisible();
    await expect(liveBadge).toHaveText('LIVE');

    // Verify computed styles: flex centering, rounded pill, single line nowrap
    const badgeStyles = await liveBadge.evaluate(el => {
      const computed = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const parentRect = el.parentElement.getBoundingClientRect();
      const label = el.parentElement.querySelector('span.truncate');
      const labelRect = label.getBoundingClientRect();
      const badgeCenterY = rect.top + rect.height / 2;
      const labelCenterY = labelRect.top + labelRect.height / 2;
      return {
        display: computed.display,
        alignItems: computed.alignItems,
        justifyContent: computed.justifyContent,
        whiteSpace: computed.whiteSpace,
        borderRadius: computed.borderRadius,
        lineHeight: computed.lineHeight,
        height: rect.height,
        centerYDiff: Math.abs(badgeCenterY - labelCenterY),
      };
    });

    expect(['inline-flex', 'flex']).toContain(badgeStyles.display);
    expect(badgeStyles.alignItems).toBe('center');
    expect(badgeStyles.justifyContent).toBe('center');
    expect(badgeStyles.whiteSpace).toBe('nowrap');
    expect(badgeStyles.borderRadius).toBe('999px');
    expect(badgeStyles.centerYDiff).toBeLessThan(1); // perfectly centered vertically with label
    expect(badgeStyles.height).toBeLessThan(24);    // single-line compact pill height

    // Take screenshot of sidebar navigation
    await page.locator('aside nav').screenshot({ path: 'tests/sidebar-badges.png' });
  });

});
