/**
 * Visual Regression Tests
 *
 * 시각적 회귀 테스트 - 스크린샷 비교
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test, expect } from '@playwright/test';

test.describe('시각적 회귀 테스트', () => {
  test.describe('인증 페이지', () => {
    test('로그인 페이지 스냅샷', async ({ page }) => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('login-page.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });
    });

    test('회원가입 페이지 스냅샷', async ({ page }) => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('register-page.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });
    });
  });

  test.describe('메인 페이지', () => {
    test('홈페이지 스냅샷', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('home-page.png', {
        maxDiffPixels: 200,
        fullPage: true,
      });
    });
  });

  test.describe('콘텐츠 페이지', () => {
    test('콘텐츠 목록 스냅샷', async ({ page }) => {
      await page.goto('/contents');
      await page.waitForLoadState('networkidle');

      // 동적 콘텐츠 로드 대기
      await page.waitForSelector('[data-testid="content-card"]');

      await expect(page).toHaveScreenshot('content-list.png', {
        maxDiffPixels: 300, // 동적 콘텐츠 허용
      });
    });

    test('콘텐츠 상세 스냅샷', async ({ page }) => {
      await page.goto('/contents/1');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('content-detail.png', {
        maxDiffPixels: 200,
      });
    });
  });

  test.describe('검색 페이지', () => {
    test('검색 결과 스냅샷', async ({ page }) => {
      await page.goto('/search?q=poker');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('search-results.png', {
        maxDiffPixels: 300,
      });
    });

    test('빈 검색 결과 스냅샷', async ({ page }) => {
      await page.goto('/search?q=xyznonexistent');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('search-no-results.png', {
        maxDiffPixels: 100,
      });
    });
  });

  test.describe('플레이어 페이지', () => {
    test('플레이어 UI 스냅샷', async ({ page }) => {
      await page.goto('/player/1');
      await page.waitForLoadState('networkidle');

      // 비디오 로드 대기
      await page.waitForSelector('[data-testid="video-player"]');

      // 컨트롤 표시를 위해 마우스 이동
      await page.hover('[data-testid="video-player"]');

      await expect(page).toHaveScreenshot('player-ui.png', {
        maxDiffPixels: 500, // 비디오 프레임 변동 허용
        mask: [page.locator('[data-testid="video-element"]')], // 비디오 영역 마스킹
      });
    });
  });

  test.describe('반응형 레이아웃', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1280, height: 720 },
    ];

    for (const viewport of viewports) {
      test(`홈페이지 - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({
          width: viewport.width,
          height: viewport.height,
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot(`home-${viewport.name}.png`, {
          maxDiffPixels: 200,
          fullPage: true,
        });
      });
    }
  });

  test.describe('다크 모드', () => {
    test('다크 모드 홈페이지 스냅샷', async ({ page }) => {
      // 다크 모드 설정
      await page.emulateMedia({ colorScheme: 'dark' });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('home-dark-mode.png', {
        maxDiffPixels: 200,
      });
    });

    test('다크 모드 로그인 페이지 스냅샷', async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'dark' });

      await page.goto('/login');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('login-dark-mode.png', {
        maxDiffPixels: 100,
      });
    });
  });
});
