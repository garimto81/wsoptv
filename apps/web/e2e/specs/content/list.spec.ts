/**
 * Content Domain - List E2E Tests
 *
 * 콘텐츠 목록 기능 E2E 테스트
 *
 * AGENT_RULES 참조: apps/web/features/content/AGENT_RULES.md
 * 자동화 레벨: 100%
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test, expect, testUtils } from '../../fixtures/base.fixture';

test.describe('콘텐츠 목록', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // 콘텐츠 목록 페이지로 이동
    await authenticatedPage.goto('/contents');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('콘텐츠 목록 로드', async ({ authenticatedPage }) => {
    // Then: 콘텐츠 목록 표시
    const contentList = authenticatedPage.locator(
      '[data-testid="content-list"]'
    );
    await expect(contentList).toBeVisible();

    // 최소 1개 이상의 콘텐츠 카드 표시
    const contentCards = authenticatedPage.locator(
      '[data-testid="content-card"]'
    );
    await expect(contentCards.first()).toBeVisible();
  });

  test('콘텐츠 카드에 필수 정보 표시', async ({ authenticatedPage }) => {
    // Given: 첫 번째 콘텐츠 카드
    const firstCard = authenticatedPage
      .locator('[data-testid="content-card"]')
      .first();

    // Then: 필수 정보 확인
    await expect(firstCard.locator('[data-testid="content-title"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="content-thumbnail"]')).toBeVisible();
    await expect(firstCard.locator('[data-testid="content-duration"]')).toBeVisible();
  });

  test('콘텐츠 클릭 시 상세 페이지 이동', async ({ authenticatedPage }) => {
    // Given: 첫 번째 콘텐츠 카드
    const firstCard = authenticatedPage
      .locator('[data-testid="content-card"]')
      .first();

    // When: 클릭
    await firstCard.click();

    // Then: 상세 페이지로 이동
    await expect(authenticatedPage).toHaveURL(/\/contents\/\d+/);
  });

  test('무한 스크롤로 추가 콘텐츠 로드', async ({ authenticatedPage }) => {
    // Given: 초기 콘텐츠 수 확인
    const initialCards = await authenticatedPage
      .locator('[data-testid="content-card"]')
      .count();

    // When: 페이지 하단으로 스크롤
    await authenticatedPage.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });

    // API 응답 대기
    await testUtils.waitForApi(authenticatedPage, '/api/contents');

    // Then: 추가 콘텐츠 로드
    const afterScrollCards = await authenticatedPage
      .locator('[data-testid="content-card"]')
      .count();

    expect(afterScrollCards).toBeGreaterThan(initialCards);
  });
});

test.describe('콘텐츠 필터링', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/contents');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('카테고리 필터 적용', async ({ authenticatedPage }) => {
    // When: 카테고리 선택
    await authenticatedPage.click('[data-testid="category-filter"]');
    await authenticatedPage.click('[data-testid="category-option-wsop"]');

    // Then: URL 파라미터 변경
    await expect(authenticatedPage).toHaveURL(/category=wsop/);

    // 필터링된 결과 표시
    await testUtils.waitForLoading(authenticatedPage);
    const contentCards = authenticatedPage.locator(
      '[data-testid="content-card"]'
    );
    await expect(contentCards.first()).toBeVisible();
  });

  test('등급 필터 적용', async ({ authenticatedPage }) => {
    // When: 등급 필터 선택
    await authenticatedPage.click('[data-testid="rating-filter"]');
    await authenticatedPage.click('[data-testid="rating-option-4plus"]');

    // Then: URL 파라미터 변경
    await expect(authenticatedPage).toHaveURL(/rating=4/);
  });

  test('필터 초기화', async ({ authenticatedPage }) => {
    // Given: 필터 적용
    await authenticatedPage.click('[data-testid="category-filter"]');
    await authenticatedPage.click('[data-testid="category-option-wsop"]');
    await expect(authenticatedPage).toHaveURL(/category=wsop/);

    // When: 필터 초기화
    await authenticatedPage.click('[data-testid="filter-reset"]');

    // Then: URL 파라미터 제거
    await expect(authenticatedPage).not.toHaveURL(/category=/);
  });
});

test.describe('콘텐츠 정렬', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/contents');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('최신순 정렬', async ({ authenticatedPage }) => {
    // When: 정렬 변경
    await authenticatedPage.click('[data-testid="sort-select"]');
    await authenticatedPage.click('[data-testid="sort-option-latest"]');

    // Then: URL 파라미터 변경
    await expect(authenticatedPage).toHaveURL(/sort=latest/);
  });

  test('인기순 정렬', async ({ authenticatedPage }) => {
    // When: 정렬 변경
    await authenticatedPage.click('[data-testid="sort-select"]');
    await authenticatedPage.click('[data-testid="sort-option-popular"]');

    // Then: URL 파라미터 변경
    await expect(authenticatedPage).toHaveURL(/sort=popular/);
  });
});

test.describe('콘텐츠 목록 반응형', () => {
  test('모바일 뷰에서 그리드 변경', async ({ authenticatedPage }) => {
    // Given: 모바일 뷰포트
    await authenticatedPage.setViewportSize({ width: 375, height: 667 });
    await authenticatedPage.goto('/contents');

    // Then: 단일 열 그리드
    const contentList = authenticatedPage.locator(
      '[data-testid="content-list"]'
    );
    await expect(contentList).toHaveCSS('grid-template-columns', /1fr/);
  });

  test('태블릿 뷰에서 그리드 변경', async ({ authenticatedPage }) => {
    // Given: 태블릿 뷰포트
    await authenticatedPage.setViewportSize({ width: 768, height: 1024 });
    await authenticatedPage.goto('/contents');

    // Then: 2열 그리드
    const contentList = authenticatedPage.locator(
      '[data-testid="content-list"]'
    );
    await expect(contentList).toHaveCSS(
      'grid-template-columns',
      /repeat\(2/
    );
  });
});
