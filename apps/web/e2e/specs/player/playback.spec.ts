/**
 * Stream Domain - Player Playback E2E Tests
 *
 * 비디오 플레이어 재생 기능 E2E 테스트
 *
 * AGENT_RULES 참조: apps/web/features/player/AGENT_RULES.md
 * 자동화 레벨: 100%
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 */

import { test, expect, testUtils } from '../../fixtures/base.fixture';

test.describe('비디오 재생', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // 플레이어 페이지로 이동
    await authenticatedPage.goto('/player/1');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('비디오 플레이어 로드', async ({ authenticatedPage }) => {
    // Then: 플레이어 표시
    const player = authenticatedPage.locator('[data-testid="video-player"]');
    await expect(player).toBeVisible();
  });

  test('재생/일시정지 토글', async ({ authenticatedPage }) => {
    // Given: 플레이어 대기
    const player = authenticatedPage.locator('[data-testid="video-player"]');
    await expect(player).toBeVisible();

    const playButton = authenticatedPage.locator('[data-testid="play-button"]');

    // When: 재생 버튼 클릭
    await playButton.click();

    // Then: 재생 상태로 변경
    await expect(playButton).toHaveAttribute('data-playing', 'true');

    // When: 다시 클릭
    await playButton.click();

    // Then: 일시정지 상태로 변경
    await expect(playButton).toHaveAttribute('data-playing', 'false');
  });

  test('볼륨 조절', async ({ authenticatedPage }) => {
    // Given: 볼륨 슬라이더
    const volumeSlider = authenticatedPage.locator(
      '[data-testid="volume-slider"]'
    );

    // When: 볼륨 50%로 조절
    await volumeSlider.fill('50');

    // Then: 볼륨 상태 표시 업데이트
    const volumeIcon = authenticatedPage.locator('[data-testid="volume-icon"]');
    await expect(volumeIcon).toHaveAttribute('data-level', 'medium');
  });

  test('음소거 토글', async ({ authenticatedPage }) => {
    // Given: 음소거 버튼
    const muteButton = authenticatedPage.locator('[data-testid="mute-button"]');

    // When: 음소거 클릭
    await muteButton.click();

    // Then: 음소거 상태
    await expect(muteButton).toHaveAttribute('data-muted', 'true');

    // When: 다시 클릭
    await muteButton.click();

    // Then: 음소거 해제
    await expect(muteButton).toHaveAttribute('data-muted', 'false');
  });

  test('전체화면 토글', async ({ authenticatedPage }) => {
    // Given: 전체화면 버튼
    const fullscreenButton = authenticatedPage.locator(
      '[data-testid="fullscreen-button"]'
    );

    // When: 전체화면 클릭
    await fullscreenButton.click();

    // Then: 전체화면 상태
    const isFullscreen = await authenticatedPage.evaluate(() => {
      return document.fullscreenElement !== null;
    });
    expect(isFullscreen).toBe(true);
  });

  test('시크바로 위치 이동', async ({ authenticatedPage }) => {
    // Given: 재생 시작
    const playButton = authenticatedPage.locator('[data-testid="play-button"]');
    await playButton.click();

    // 약간 대기
    await authenticatedPage.waitForTimeout(1000);

    // When: 시크바 50% 위치로 클릭
    const seekBar = authenticatedPage.locator('[data-testid="seek-bar"]');
    const box = await seekBar.boundingBox();
    if (box) {
      await authenticatedPage.mouse.click(box.x + box.width * 0.5, box.y + box.height / 2);
    }

    // Then: 진행률 표시 업데이트
    const progress = authenticatedPage.locator('[data-testid="progress-bar"]');
    const progressWidth = await progress.evaluate((el) =>
      parseFloat(getComputedStyle(el).width)
    );
    expect(progressWidth).toBeGreaterThan(0);
  });
});

test.describe('비디오 품질', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/player/1');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('품질 선택 메뉴 열기', async ({ authenticatedPage }) => {
    // When: 설정 버튼 클릭
    await authenticatedPage.click('[data-testid="settings-button"]');

    // Then: 품질 옵션 표시
    const qualityMenu = authenticatedPage.locator(
      '[data-testid="quality-menu"]'
    );
    await expect(qualityMenu).toBeVisible();
  });

  test('품질 변경', async ({ authenticatedPage }) => {
    // Given: 설정 메뉴 열기
    await authenticatedPage.click('[data-testid="settings-button"]');

    // When: 720p 선택
    await authenticatedPage.click('[data-testid="quality-720p"]');

    // Then: 품질 표시 업데이트
    const qualityIndicator = authenticatedPage.locator(
      '[data-testid="quality-indicator"]'
    );
    await expect(qualityIndicator).toContainText('720p');
  });

  test('자동 품질 선택', async ({ authenticatedPage }) => {
    // Given: 설정 메뉴 열기
    await authenticatedPage.click('[data-testid="settings-button"]');

    // When: Auto 선택
    await authenticatedPage.click('[data-testid="quality-auto"]');

    // Then: 자동 품질 표시
    const qualityIndicator = authenticatedPage.locator(
      '[data-testid="quality-indicator"]'
    );
    await expect(qualityIndicator).toContainText('Auto');
  });
});

test.describe('타임라인 핸드', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/player/1');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('핸드 마커 표시', async ({ authenticatedPage }) => {
    // Then: 핸드 마커 표시
    const handMarkers = authenticatedPage.locator('[data-testid="hand-marker"]');
    const count = await handMarkers.count();
    expect(count).toBeGreaterThan(0);
  });

  test('핸드 마커 클릭 시 해당 위치로 이동', async ({ authenticatedPage }) => {
    // Given: 첫 번째 핸드 마커
    const firstMarker = authenticatedPage
      .locator('[data-testid="hand-marker"]')
      .first();

    // 마커 위치 기록
    const markerPosition = await firstMarker.getAttribute('data-time');

    // When: 마커 클릭
    await firstMarker.click();

    // Then: 해당 시간으로 이동
    const currentTime = authenticatedPage.locator(
      '[data-testid="current-time"]'
    );
    await expect(currentTime).toContainText(markerPosition || '');
  });

  test('핸드 리스트 패널 열기', async ({ authenticatedPage }) => {
    // When: 핸드 리스트 버튼 클릭
    await authenticatedPage.click('[data-testid="hand-list-toggle"]');

    // Then: 핸드 리스트 패널 표시
    const handListPanel = authenticatedPage.locator(
      '[data-testid="hand-list-panel"]'
    );
    await expect(handListPanel).toBeVisible();
  });

  test('핸드 리스트에서 핸드 선택', async ({ authenticatedPage }) => {
    // Given: 핸드 리스트 열기
    await authenticatedPage.click('[data-testid="hand-list-toggle"]');

    // When: 첫 번째 핸드 클릭
    const firstHand = authenticatedPage
      .locator('[data-testid="hand-item"]')
      .first();
    await firstHand.click();

    // Then: 해당 핸드 위치로 이동
    const handListPanel = authenticatedPage.locator(
      '[data-testid="hand-list-panel"]'
    );
    // 패널이 자동으로 닫히거나 해당 핸드가 하이라이트됨
    await expect(firstHand).toHaveClass(/active/);
  });
});

test.describe('키보드 단축키', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/player/1');
    await testUtils.waitForLoading(authenticatedPage);
  });

  test('Space로 재생/일시정지', async ({ authenticatedPage }) => {
    const playButton = authenticatedPage.locator('[data-testid="play-button"]');

    // When: Space 키
    await authenticatedPage.keyboard.press('Space');

    // Then: 재생 상태
    await expect(playButton).toHaveAttribute('data-playing', 'true');

    // When: Space 다시
    await authenticatedPage.keyboard.press('Space');

    // Then: 일시정지 상태
    await expect(playButton).toHaveAttribute('data-playing', 'false');
  });

  test('좌우 화살표로 10초 이동', async ({ authenticatedPage }) => {
    // Given: 재생 시작
    await authenticatedPage.click('[data-testid="play-button"]');
    await authenticatedPage.waitForTimeout(1000);

    // 현재 시간 기록
    const currentTime = authenticatedPage.locator(
      '[data-testid="current-time"]'
    );
    const timeBefore = await currentTime.textContent();

    // When: 오른쪽 화살표
    await authenticatedPage.keyboard.press('ArrowRight');

    // Then: 10초 전진 (시간 변경 확인)
    await authenticatedPage.waitForTimeout(500);
    const timeAfter = await currentTime.textContent();
    expect(timeAfter).not.toBe(timeBefore);
  });

  test('M키로 음소거 토글', async ({ authenticatedPage }) => {
    const muteButton = authenticatedPage.locator('[data-testid="mute-button"]');

    // When: M 키
    await authenticatedPage.keyboard.press('m');

    // Then: 음소거 상태
    await expect(muteButton).toHaveAttribute('data-muted', 'true');
  });

  test('F키로 전체화면', async ({ authenticatedPage }) => {
    // When: F 키
    await authenticatedPage.keyboard.press('f');

    // Then: 전체화면 상태
    const isFullscreen = await authenticatedPage.evaluate(() => {
      return document.fullscreenElement !== null;
    });
    expect(isFullscreen).toBe(true);
  });
});
