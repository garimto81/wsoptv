/**
 * Playwright E2E Test Configuration
 *
 * WSOPTV Block Agent System E2E 테스트 설정
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 * @see https://playwright.dev/docs/test-configuration
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * 환경변수에서 CI 여부 확인
 * @see https://playwright.dev/docs/ci
 */
const isCI = !!process.env.CI;

export default defineConfig({
  // 테스트 디렉토리
  testDir: './specs',

  // 테스트 파일 패턴
  testMatch: '**/*.spec.ts',

  // 병렬 실행 설정 (속도 최적화)
  fullyParallel: true,
  workers: isCI ? 4 : undefined,

  // 재시도 정책 (자동 수정 후 재시도 대비)
  retries: isCI ? 2 : 0,

  // 타임아웃 설정
  timeout: 30000, // 테스트당 30초
  expect: {
    timeout: 5000, // assertion당 5초
  },

  // 리포터 설정 (최종 보고서용)
  reporter: isCI
    ? [
        ['html', { outputFolder: 'playwright-report', open: 'never' }],
        ['json', { outputFile: 'test-results/results.json' }],
        ['github'], // GitHub Actions 통합
        ['list'], // 콘솔 출력
      ]
    : [
        ['html', { outputFolder: 'playwright-report', open: 'on-failure' }],
        ['list'],
      ],

  // 글로벌 설정
  use: {
    // 기본 URL
    baseURL: process.env.BASE_URL || 'http://localhost:5173',

    // 추적 설정
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // 뷰포트 설정
    viewport: { width: 1280, height: 720 },

    // 로케일/타임존
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',

    // 액션 타임아웃
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 브라우저별 프로젝트 설정
  projects: [
    // === Desktop Browsers ===
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // 크롬 DevTools 프로토콜 접근
        launchOptions: {
          args: ['--disable-web-security'],
        },
      },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // === Mobile Browsers ===
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
    },

    // === Tablet ===
    {
      name: 'tablet',
      use: { ...devices['iPad Pro 11'] },
    },
  ],

  // 웹 서버 자동 시작
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !isCI,
    timeout: 120000,
    stdout: 'pipe',
    stderr: 'pipe',
  },

  // 출력 디렉토리
  outputDir: 'test-results',

  // 스냅샷 설정 (시각적 회귀 테스트용)
  snapshotDir: './visual/snapshots',
  snapshotPathTemplate: '{snapshotDir}/{testFilePath}/{arg}{ext}',

  // 메타데이터
  metadata: {
    project: 'WSOPTV',
    framework: 'Block Agent System',
  },
});
