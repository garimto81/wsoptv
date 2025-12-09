/**
 * Base Test Fixture
 *
 * 모든 E2E 테스트의 기본 픽스처
 * 인증, 페이지 설정, 공통 유틸리티 제공
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test as base, expect, Page, BrowserContext } from '@playwright/test';

/**
 * 사용자 정보 타입
 */
interface TestUser {
  email: string;
  password: string;
  name?: string;
}

/**
 * 테스트 픽스처 타입 확장
 */
interface TestFixtures {
  /** 인증된 페이지 */
  authenticatedPage: Page;
  /** 테스트 사용자 정보 */
  testUser: TestUser;
  /** 인증된 컨텍스트 */
  authenticatedContext: BrowserContext;
}

/**
 * 테스트용 기본 사용자
 */
const DEFAULT_TEST_USER: TestUser = {
  email: process.env.TEST_USER_EMAIL || 'test@wsoptv.com',
  password: process.env.TEST_USER_PASSWORD || 'testPassword123!',
  name: 'Test User',
};

/**
 * 기본 테스트 픽스처 확장
 */
export const test = base.extend<TestFixtures>({
  /**
   * 테스트 사용자 정보
   */
  testUser: async ({}, use) => {
    await use(DEFAULT_TEST_USER);
  },

  /**
   * 인증된 페이지 픽스처
   *
   * 로그인이 완료된 상태의 페이지를 제공합니다.
   * 테스트 후 자동으로 로그아웃됩니다.
   */
  authenticatedPage: async ({ page, testUser }, use) => {
    // 로그인 페이지로 이동
    await page.goto('/login');

    // 로그인 폼 입력
    await page.fill('[data-testid="email-input"]', testUser.email);
    await page.fill('[data-testid="password-input"]', testUser.password);

    // 제출
    await page.click('[data-testid="login-submit"]');

    // 로그인 완료 대기
    await page.waitForURL(/\/(dashboard|home)/, { timeout: 10000 });

    // 인증된 페이지 제공
    await use(page);

    // 정리: 로그아웃 시도
    try {
      const logoutButton = page.locator('[data-testid="logout-button"]');
      if (await logoutButton.isVisible({ timeout: 1000 })) {
        await logoutButton.click();
        await page.waitForURL('/login', { timeout: 5000 });
      }
    } catch {
      // 로그아웃 실패해도 계속 진행
    }
  },

  /**
   * 인증된 브라우저 컨텍스트
   *
   * 스토리지 상태가 저장된 컨텍스트를 제공합니다.
   * 여러 페이지에서 인증 상태를 공유할 때 사용합니다.
   */
  authenticatedContext: async ({ browser, testUser }, use) => {
    // 새 컨텍스트 생성
    const context = await browser.newContext();
    const page = await context.newPage();

    // 로그인
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', testUser.email);
    await page.fill('[data-testid="password-input"]', testUser.password);
    await page.click('[data-testid="login-submit"]');
    await page.waitForURL(/\/(dashboard|home)/);

    // 스토리지 상태 저장
    await context.storageState({ path: '.auth/user.json' });

    await page.close();

    // 컨텍스트 제공
    await use(context);

    // 정리
    await context.close();
  },
});

/**
 * expect 재내보내기
 */
export { expect };

/**
 * 공통 테스트 유틸리티
 */
export const testUtils = {
  /**
   * API 응답 대기
   */
  async waitForApi(page: Page, urlPattern: string | RegExp): Promise<void> {
    await page.waitForResponse(
      (response) =>
        (typeof urlPattern === 'string'
          ? response.url().includes(urlPattern)
          : urlPattern.test(response.url())) && response.status() === 200
    );
  },

  /**
   * 로딩 상태 대기
   */
  async waitForLoading(page: Page): Promise<void> {
    // 로딩 인디케이터가 있으면 사라질 때까지 대기
    const loading = page.locator('[data-testid="loading"]');
    if (await loading.isVisible({ timeout: 500 })) {
      await loading.waitFor({ state: 'hidden', timeout: 30000 });
    }
  },

  /**
   * 토스트 메시지 확인
   */
  async expectToast(page: Page, message: string): Promise<void> {
    const toast = page.locator('[data-testid="toast"]');
    await expect(toast).toContainText(message);
  },

  /**
   * 에러 메시지 확인
   */
  async expectError(page: Page, message: string): Promise<void> {
    const error = page.locator('[data-testid="error-message"]');
    await expect(error).toContainText(message);
  },

  /**
   * 네트워크 요청 모킹
   */
  async mockApi(
    page: Page,
    urlPattern: string | RegExp,
    response: { status?: number; body?: unknown }
  ): Promise<void> {
    await page.route(urlPattern, (route) => {
      route.fulfill({
        status: response.status || 200,
        contentType: 'application/json',
        body: JSON.stringify(response.body || {}),
      });
    });
  },
};

/**
 * 테스트 데이터 생성 헬퍼
 */
export const testData = {
  /**
   * 랜덤 이메일 생성
   */
  randomEmail(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(7);
    return `test-${timestamp}-${random}@wsoptv.com`;
  },

  /**
   * 랜덤 문자열 생성
   */
  randomString(length: number = 10): string {
    return Math.random()
      .toString(36)
      .substring(2, 2 + length);
  },
};
