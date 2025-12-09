/**
 * Auth Domain - Login E2E Tests
 *
 * 로그인 기능 E2E 테스트
 *
 * AGENT_RULES 참조: apps/web/features/auth/AGENT_RULES.md
 * 자동화 레벨: 100%
 * 브라우저: Chromium, Firefox, WebKit
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test, expect, authHelpers } from '../../fixtures/auth.fixture';

test.describe('로그인 기능', () => {
  test.beforeEach(async ({ loginPage }) => {
    // 로그인 페이지 로드 확인
    await expect(loginPage.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('유효한 자격증명으로 로그인 성공', async ({ loginPage, authMocks }) => {
    // Given: 로그인 API 성공 모킹
    await authMocks.mockLoginSuccess();

    // When: 유효한 자격증명 입력 및 제출
    await authHelpers.fillLoginForm(loginPage, {
      email: 'test@wsoptv.com',
      password: 'validPassword123!',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 대시보드로 리다이렉트
    await authHelpers.waitForLoginSuccess(loginPage);
    await expect(loginPage).toHaveURL(/\/(dashboard|home)/);
  });

  test('잘못된 비밀번호로 로그인 실패', async ({ loginPage, authMocks }) => {
    // Given: 로그인 API 실패 모킹
    await authMocks.mockLoginFailure('이메일 또는 비밀번호가 잘못되었습니다.');

    // When: 잘못된 자격증명 입력 및 제출
    await authHelpers.fillLoginForm(loginPage, {
      email: 'test@wsoptv.com',
      password: 'wrongPassword',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 에러 메시지 표시
    await authHelpers.expectLoginError(
      loginPage,
      '이메일 또는 비밀번호가 잘못되었습니다.'
    );
  });

  test('빈 이메일로 제출 시 검증 오류', async ({ loginPage }) => {
    // When: 이메일 비우고 제출
    await authHelpers.fillLoginForm(loginPage, {
      email: '',
      password: 'somePassword',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 이메일 검증 에러
    const emailError = loginPage.locator('[data-testid="email-error"]');
    await expect(emailError).toContainText('이메일을 입력해주세요');
  });

  test('빈 비밀번호로 제출 시 검증 오류', async ({ loginPage }) => {
    // When: 비밀번호 비우고 제출
    await authHelpers.fillLoginForm(loginPage, {
      email: 'test@wsoptv.com',
      password: '',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 비밀번호 검증 에러
    const passwordError = loginPage.locator('[data-testid="password-error"]');
    await expect(passwordError).toContainText('비밀번호를 입력해주세요');
  });

  test('잘못된 이메일 형식으로 제출 시 검증 오류', async ({ loginPage }) => {
    // When: 잘못된 이메일 형식 입력
    await authHelpers.fillLoginForm(loginPage, {
      email: 'invalid-email',
      password: 'somePassword',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 이메일 형식 에러
    const emailError = loginPage.locator('[data-testid="email-error"]');
    await expect(emailError).toContainText('올바른 이메일 형식');
  });

  test('2FA 필요 시 2FA 폼 표시', async ({ loginPage, authMocks }) => {
    // Given: 2FA 필요 응답 모킹
    await authMocks.mock2FARequired();

    // When: 로그인 제출
    await authHelpers.fillLoginForm(loginPage, {
      email: 'test@wsoptv.com',
      password: 'validPassword123!',
    });
    await authHelpers.submitLogin(loginPage);

    // Then: 2FA 폼 표시
    await authHelpers.waitFor2FAForm(loginPage);
  });

  test('비밀번호 찾기 링크 동작', async ({ loginPage }) => {
    // When: 비밀번호 찾기 링크 클릭
    await loginPage.click('[data-testid="forgot-password-link"]');

    // Then: 비밀번호 찾기 페이지로 이동
    await expect(loginPage).toHaveURL(/\/forgot-password/);
  });

  test('회원가입 링크 동작', async ({ loginPage }) => {
    // When: 회원가입 링크 클릭
    await loginPage.click('[data-testid="register-link"]');

    // Then: 회원가입 페이지로 이동
    await expect(loginPage).toHaveURL(/\/register/);
  });
});

test.describe('로그인 접근성', () => {
  test('키보드로만 로그인 가능', async ({ loginPage, authMocks }) => {
    // Given
    await authMocks.mockLoginSuccess();

    // When: Tab으로 이동하며 입력
    await loginPage.keyboard.press('Tab'); // email 필드로
    await loginPage.keyboard.type('test@wsoptv.com');
    await loginPage.keyboard.press('Tab'); // password 필드로
    await loginPage.keyboard.type('validPassword123!');
    await loginPage.keyboard.press('Tab'); // submit 버튼으로
    await loginPage.keyboard.press('Enter');

    // Then: 로그인 성공
    await authHelpers.waitForLoginSuccess(loginPage);
  });

  test('폼 필드에 적절한 ARIA 레이블', async ({ loginPage }) => {
    // 이메일 필드
    const emailInput = loginPage.locator('[data-testid="email-input"]');
    await expect(emailInput).toHaveAttribute('aria-label', /이메일/);

    // 비밀번호 필드
    const passwordInput = loginPage.locator('[data-testid="password-input"]');
    await expect(passwordInput).toHaveAttribute('aria-label', /비밀번호/);
  });
});
