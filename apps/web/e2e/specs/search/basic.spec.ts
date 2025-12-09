/**
 * Search Domain - Basic Search E2E Tests
 *
 * 기본 검색 기능 E2E 테스트
 *
 * AGENT_RULES 참조: apps/web/features/search/AGENT_RULES.md
 * 자동화 레벨: 100%
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test, expect, testUtils } from '../../fixtures/base.fixture';

test.describe('검색 기본 기능', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('검색창 표시', async ({ authenticatedPage }) => {
    // Then: 검색창 표시
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await expect(searchInput).toBeVisible();
  });

  test('검색어 입력 및 검색 실행', async ({ authenticatedPage }) => {
    // Given: 검색창
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );

    // When: 검색어 입력 및 Enter
    await searchInput.fill('WSOP 2024');
    await searchInput.press('Enter');

    // Then: 검색 결과 페이지로 이동
    await expect(authenticatedPage).toHaveURL(/\/search\?q=WSOP/);
  });

  test('검색 버튼 클릭으로 검색', async ({ authenticatedPage }) => {
    // Given: 검색어 입력
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('포커');

    // When: 검색 버튼 클릭
    await authenticatedPage.click('[data-testid="search-button"]');

    // Then: 검색 결과 페이지로 이동
    await expect(authenticatedPage).toHaveURL(/\/search\?q=/);
  });

  test('빈 검색어 제출 시 검색 안됨', async ({ authenticatedPage }) => {
    // Given: 빈 검색창
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );

    // When: Enter
    await searchInput.press('Enter');

    // Then: 페이지 이동 없음
    await expect(authenticatedPage).not.toHaveURL(/\/search/);
  });
});

test.describe('검색 결과', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/search?q=WSOP');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('검색 결과 표시', async ({ authenticatedPage }) => {
    // Then: 검색 결과 목록 표시
    const results = authenticatedPage.locator('[data-testid="search-results"]');
    await expect(results).toBeVisible();
  });

  test('검색 결과 카운트 표시', async ({ authenticatedPage }) => {
    // Then: 결과 수 표시
    const resultCount = authenticatedPage.locator(
      '[data-testid="result-count"]'
    );
    await expect(resultCount).toBeVisible();
    await expect(resultCount).toContainText(/\d+개/);
  });

  test('검색어 하이라이트', async ({ authenticatedPage }) => {
    // Then: 검색어가 하이라이트됨
    const highlight = authenticatedPage
      .locator('[data-testid="search-highlight"]')
      .first();
    await expect(highlight).toBeVisible();
    await expect(highlight).toContainText(/WSOP/i);
  });

  test('검색 결과 클릭 시 상세 페이지 이동', async ({ authenticatedPage }) => {
    // Given: 첫 번째 결과
    const firstResult = authenticatedPage
      .locator('[data-testid="search-result-item"]')
      .first();

    // When: 클릭
    await firstResult.click();

    // Then: 상세 페이지로 이동
    await expect(authenticatedPage).toHaveURL(/\/contents\/\d+/);
  });

  test('검색 결과 없음 처리', async ({ authenticatedPage }) => {
    // Given: 결과 없는 검색어
    await authenticatedPage.goto('/search?q=xyznonexistent12345');
    await testUtils.waitForLoading(authenticatedPage);

    // Then: 결과 없음 메시지
    const noResults = authenticatedPage.locator(
      '[data-testid="no-results"]'
    );
    await expect(noResults).toBeVisible();
    await expect(noResults).toContainText('검색 결과가 없습니다');
  });
});

test.describe('자동완성', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('입력 시 자동완성 표시', async ({ authenticatedPage }) => {
    // Given: 검색창
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );

    // When: 검색어 입력
    await searchInput.fill('WS');

    // Then: 자동완성 드롭다운 표시
    const autocomplete = authenticatedPage.locator(
      '[data-testid="autocomplete-dropdown"]'
    );
    await expect(autocomplete).toBeVisible({ timeout: 2000 });
  });

  test('자동완성 항목 선택', async ({ authenticatedPage }) => {
    // Given: 검색어 입력
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('WS');

    // 자동완성 대기
    const autocomplete = authenticatedPage.locator(
      '[data-testid="autocomplete-dropdown"]'
    );
    await expect(autocomplete).toBeVisible({ timeout: 2000 });

    // When: 첫 번째 항목 클릭
    const firstSuggestion = authenticatedPage
      .locator('[data-testid="autocomplete-item"]')
      .first();
    await firstSuggestion.click();

    // Then: 검색 결과 페이지로 이동
    await expect(authenticatedPage).toHaveURL(/\/search\?q=/);
  });

  test('키보드로 자동완성 탐색', async ({ authenticatedPage }) => {
    // Given: 검색어 입력
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('WS');

    // 자동완성 대기
    await authenticatedPage.waitForSelector(
      '[data-testid="autocomplete-dropdown"]'
    );

    // When: 아래 화살표로 선택
    await searchInput.press('ArrowDown');
    await searchInput.press('Enter');

    // Then: 검색 실행
    await expect(authenticatedPage).toHaveURL(/\/search\?q=/);
  });

  test('ESC로 자동완성 닫기', async ({ authenticatedPage }) => {
    // Given: 검색어 입력 및 자동완성 표시
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('WS');

    const autocomplete = authenticatedPage.locator(
      '[data-testid="autocomplete-dropdown"]'
    );
    await expect(autocomplete).toBeVisible({ timeout: 2000 });

    // When: ESC
    await searchInput.press('Escape');

    // Then: 자동완성 닫힘
    await expect(autocomplete).not.toBeVisible();
  });
});

test.describe('검색 필터', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/search?q=포커');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('카테고리 필터 적용', async ({ authenticatedPage }) => {
    // When: 카테고리 필터 선택
    await authenticatedPage.click('[data-testid="filter-category"]');
    await authenticatedPage.click('[data-testid="filter-category-wsop"]');

    // Then: URL 파라미터 추가
    await expect(authenticatedPage).toHaveURL(/category=wsop/);
  });

  test('날짜 범위 필터 적용', async ({ authenticatedPage }) => {
    // When: 날짜 필터 선택
    await authenticatedPage.click('[data-testid="filter-date"]');
    await authenticatedPage.click('[data-testid="filter-date-week"]');

    // Then: URL 파라미터 추가
    await expect(authenticatedPage).toHaveURL(/date=week/);
  });

  test('여러 필터 동시 적용', async ({ authenticatedPage }) => {
    // When: 카테고리 필터
    await authenticatedPage.click('[data-testid="filter-category"]');
    await authenticatedPage.click('[data-testid="filter-category-wsop"]');

    // 날짜 필터
    await authenticatedPage.click('[data-testid="filter-date"]');
    await authenticatedPage.click('[data-testid="filter-date-month"]');

    // Then: 두 파라미터 모두 존재
    await expect(authenticatedPage).toHaveURL(/category=wsop/);
    await expect(authenticatedPage).toHaveURL(/date=month/);
  });

  test('필터 초기화', async ({ authenticatedPage }) => {
    // Given: 필터 적용
    await authenticatedPage.click('[data-testid="filter-category"]');
    await authenticatedPage.click('[data-testid="filter-category-wsop"]');

    // When: 초기화 버튼 클릭
    await authenticatedPage.click('[data-testid="filter-reset"]');

    // Then: 필터 파라미터 제거
    await expect(authenticatedPage).not.toHaveURL(/category=/);
  });
});

test.describe('최근 검색어', () => {
  test('최근 검색어 저장', async ({ authenticatedPage }) => {
    // Given: 검색 실행
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('테스트 검색어');
    await searchInput.press('Enter');

    // When: 다시 검색창으로
    await authenticatedPage.goto('/');
    await searchInput.click();

    // Then: 최근 검색어 표시
    const recentSearches = authenticatedPage.locator(
      '[data-testid="recent-searches"]'
    );
    await expect(recentSearches).toContainText('테스트 검색어');
  });

  test('최근 검색어 삭제', async ({ authenticatedPage }) => {
    // Given: 최근 검색어 존재
    const searchInput = authenticatedPage.locator(
      '[data-testid="search-input"]'
    );
    await searchInput.fill('삭제할 검색어');
    await searchInput.press('Enter');

    await authenticatedPage.goto('/');
    await searchInput.click();

    // When: 삭제 버튼 클릭
    const deleteButton = authenticatedPage
      .locator('[data-testid="recent-search-delete"]')
      .first();
    await deleteButton.click();

    // Then: 해당 검색어 제거
    const recentSearches = authenticatedPage.locator(
      '[data-testid="recent-searches"]'
    );
    await expect(recentSearches).not.toContainText('삭제할 검색어');
  });
});
