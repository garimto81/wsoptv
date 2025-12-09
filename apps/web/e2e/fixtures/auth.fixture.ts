/**
 * Auth Domain Test Fixture
 *
 * Auth 도메인 전용 테스트 픽스처
 *
 * @see apps/web/features/auth/AGENT_RULES.md
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test as base, expect, Page } from '@playwright/test';
import { test as baseTest, testUtils } from './base.fixture';

/**
 * Auth 테스트 픽스처 타입
 */
interface AuthFixtures {
  /** 로그인 페이지 */
  loginPage: Page;
  /** 비로그인 상태 보장 */
  loggedOutPage: Page;
  /** Auth API 모킹 헬퍼 */
  authMocks: AuthMocks;
}

/**
 * Auth API 모킹 헬퍼 타입
 */
interface AuthMocks {
  /** 로그인 성공 모킹 */
  mockLoginSuccess: () => Promise<void>;
  /** 로그인 실패 모킹 */
  mockLoginFailure: (message?: string) => Promise<void>;
  /** 토큰 갱신 성공 모킹 */
  mockRefreshSuccess: () => Promise<void>;
  /** 토큰 갱신 실패 모킹 */
  mockRefreshFailure: () => Promise<void>;
  /** 2FA 요청 모킹 */
  mock2FARequired: () => Promise<void>;
}

/**
 * Auth 도메인 테스트 픽스처
 */
export const test = baseTest.extend<AuthFixtures>({
  /**
   * 로그인 페이지 픽스처
   * 로그인 페이지로 이동한 상태의 페이지
   */
  loginPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await use(page);
  },

  /**
   * 비로그인 상태 보장 픽스처
   * 세션/토큰이 없는 상태
   */
  loggedOutPage: async ({ page, context }, use) => {
    // 스토리지 클리어
    await context.clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await use(page);
  },

  /**
   * Auth API 모킹 헬퍼
   */
  authMocks: async ({ page }, use) => {
    const mocks: AuthMocks = {
      async mockLoginSuccess() {
        await page.route('**/api/auth/login', (route) => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              success: true,
              data: {
                user: {
                  id: 'test-user-1',
                  email: 'test@wsoptv.com',
                  name: 'Test User',
                },
                tokens: {
                  accessToken: 'mock-access-token',
                  refreshToken: 'mock-refresh-token',
                  expiresIn: 3600,
                },
              },
            }),
          });
        });
      },

      async mockLoginFailure(message = '이메일 또는 비밀번호가 잘못되었습니다.') {
        await page.route('**/api/auth/login', (route) => {
          route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              success: false,
              error: {
                code: 'AUTH_INVALID_CREDENTIALS',
                message,
              },
            }),
          });
        });
      },

      async mockRefreshSuccess() {
        await page.route('**/api/auth/refresh', (route) => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              success: true,
              data: {
                accessToken: 'mock-new-access-token',
                expiresIn: 3600,
              },
            }),
          });
        });
      },

      async mockRefreshFailure() {
        await page.route('**/api/auth/refresh', (route) => {
          route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              success: false,
              error: {
                code: 'AUTH_TOKEN_EXPIRED',
                message: '세션이 만료되었습니다.',
              },
            }),
          });
        });
      },

      async mock2FARequired() {
        await page.route('**/api/auth/login', (route) => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              success: true,
              data: {
                requires2FA: true,
                tempToken: 'mock-temp-token',
              },
            }),
          });
        });
      },
    };

    await use(mocks);
  },
});

/**
 * Auth 도메인 테스트 헬퍼
 */
export const authHelpers = {
  /**
   * 로그인 폼 입력
   */
  async fillLoginForm(
    page: Page,
    credentials: { email: string; password: string }
  ): Promise<void> {
    await page.fill('[data-testid="email-input"]', credentials.email);
    await page.fill('[data-testid="password-input"]', credentials.password);
  },

  /**
   * 로그인 제출
   */
  async submitLogin(page: Page): Promise<void> {
    await page.click('[data-testid="login-submit"]');
  },

  /**
   * 로그인 성공 대기
   */
  async waitForLoginSuccess(page: Page): Promise<void> {
    await page.waitForURL(/\/(dashboard|home)/, { timeout: 10000 });
  },

  /**
   * 로그인 에러 확인
   */
  async expectLoginError(page: Page, message: string): Promise<void> {
    const error = page.locator('[data-testid="login-error"]');
    await expect(error).toContainText(message);
  },

  /**
   * 2FA 폼 대기
   */
  async waitFor2FAForm(page: Page): Promise<void> {
    await expect(page.locator('[data-testid="2fa-form"]')).toBeVisible();
  },

  /**
   * 2FA 코드 입력
   */
  async fill2FACode(page: Page, code: string): Promise<void> {
    await page.fill('[data-testid="2fa-code-input"]', code);
  },

  /**
   * 로그아웃 실행
   */
  async logout(page: Page): Promise<void> {
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    await page.waitForURL('/login');
  },
};

export { expect };
