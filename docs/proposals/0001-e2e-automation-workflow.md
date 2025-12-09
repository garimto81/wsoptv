# Proposal: E2E 자동화 워크플로우

**Version**: 1.0.0 | **Date**: 2025-12-09 | **Status**: Draft

---

## 목차

1. [개요](#1-개요)
2. [핵심 원칙](#2-핵심-원칙)
3. [자동화 계층 구조](#3-자동화-계층-구조)
4. [Playwright 통합 전략](#4-playwright-통합-전략)
5. [작업 분류 체계](#5-작업-분류-체계)
6. [워크플로우 설계](#6-워크플로우-설계)
7. [구현 가이드](#7-구현-가이드)
8. [CI/CD 통합](#8-cicd-통합)
9. [보고서 형식](#9-보고서-형식)

---

## 1. 개요

### 1.1 목적

사용자(지휘자)가 **최종 결과물만** 보고받을 수 있도록 E2E 테스트 자동화 워크플로우를 설계합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTOMATION GOAL                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Before (현재)                 After (목표)                 │
│   ───────────────              ─────────────                │
│                                                              │
│   /work-wsoptv "기능 추가"     /work-wsoptv "기능 추가"      │
│        ↓                            ↓                       │
│   [중간 보고 1]                 (자동 E2E 검증)              │
│   "테스트 통과했나요?"              ↓                       │
│        ↓                       (자동 수정 재시도)            │
│   [중간 보고 2]                     ↓                       │
│   "확인 부탁드립니다"          [최종 보고서]                 │
│        ↓                       "PR #45 준비 완료"           │
│   (사용자 개입)                     ↓                       │
│                                [사용자 검증 태스크]         │
│                                (마지막에 한 번만)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 핵심 요구사항

| 요구사항 | 설명 |
|----------|------|
| **자동화 우선** | 모든 검증은 Playwright E2E로 자동 수행 |
| **최종 보고** | 중간 보고 최소화, 완료 시 결과만 보고 |
| **사용자 검증 후순위** | 반드시 사람이 필요한 작업만 마지막에 요청 |
| **자동 수정** | 테스트 실패 시 AI가 자동으로 수정 시도 |

### 1.3 Block Agent System 통합

```
/work-wsoptv 실행
    │
    ├─ Phase 0: Agent 라우팅 (기존)
    │
    ├─ Phase 1: 컨텍스트 분석 (기존)
    │
    ├─ Phase 2: 이슈 + 브랜치 (기존)
    │
    ├─ Phase 3: 구현 (기존)
    │
    ├─ Phase 4: 🆕 E2E 자동 검증 ──────────────────────────┐
    │      │                                                │
    │      ├─ 4.1: Playwright 테스트 실행                   │
    │      │      └─ 단위/통합/E2E 모두 실행                │
    │      │                                                │
    │      ├─ 4.2: 실패 시 자동 수정                        │
    │      │      └─ 최대 3회 재시도                        │
    │      │                                                │
    │      ├─ 4.3: 시각적 회귀 테스트                       │
    │      │      └─ 스크린샷 비교                          │
    │      │                                                │
    │      └─ 4.4: 성능 벤치마크                            │
    │             └─ Web Vitals 체크                    ────┘
    │
    ├─ Phase 5: 🆕 최종 보고서 생성
    │      └─ 변경 요약 + 테스트 결과 + PR 링크
    │
    └─ Phase 6: 🆕 사용자 검증 태스크 (마지막)
           └─ 반드시 사람이 필요한 항목만
```

---

## 2. 핵심 원칙

### 2.1 자동화 피라미드

```
                         ┌───────────────────┐
                         │  사용자 검증      │  ◀─ 마지막, 최소화
                         │  (Manual Only)    │
                         ├───────────────────┤
                      ┌──┤   E2E Tests       │──┐
                      │  │   (Playwright)    │  │
                      │  ├───────────────────┤  │
                      │  │ Integration Tests │  │  ◀─ 자동화 영역
                      │  ├───────────────────┤  │
                      │  │   Unit Tests      │  │
                      └──┴───────────────────┴──┘
                               ▲
                               │
                         AI 자동 실행
```

### 2.2 Zero-Interrupt 철학

| 원칙 | 설명 |
|------|------|
| **Silent Execution** | 성공하면 조용히 진행, 실패 시에만 보고 |
| **Auto-Retry** | 실패 시 AI가 자동으로 3회까지 수정 시도 |
| **Batch Reporting** | 모든 작업 완료 후 한 번에 보고 |
| **Human-Last** | 사람의 판단이 필요한 작업은 마지막에만 |

### 2.3 작업 분류 원칙

```
┌─────────────────────────────────────────────────────────────┐
│                   TASK CLASSIFICATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   🤖 자동화 가능 (99%)              👤 사용자 검증 필수 (1%) │
│   ─────────────────                 ─────────────────────   │
│                                                              │
│   ✅ 코드 컴파일/타입 체크           ✅ UI/UX 디자인 승인    │
│   ✅ 단위 테스트                    ✅ 비즈니스 로직 검토    │
│   ✅ 통합 테스트                    ✅ 보안 정책 결정        │
│   ✅ E2E 테스트                     ✅ 법적/규정 준수 확인   │
│   ✅ 린트/포맷팅                    ✅ 접근성 최종 확인      │
│   ✅ 성능 벤치마크                  ✅ 외부 시스템 연동 승인 │
│   ✅ 스크린샷 비교                                          │
│   ✅ API 계약 검증                                          │
│   ✅ 의존성 취약점 스캔                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 자동화 계층 구조

### 3.1 테스트 레벨별 구성

```
apps/web/
├── __tests__/                     # 단위 테스트 (Vitest)
│   ├── unit/
│   │   ├── auth.test.ts
│   │   ├── content.test.ts
│   │   └── ...
│   └── integration/
│       ├── auth-flow.test.ts
│       └── ...
│
├── e2e/                           # E2E 테스트 (Playwright)
│   ├── playwright.config.ts
│   ├── fixtures/
│   │   ├── auth.fixture.ts        # 인증 픽스처
│   │   └── content.fixture.ts
│   ├── specs/
│   │   ├── auth/
│   │   │   ├── login.spec.ts
│   │   │   ├── logout.spec.ts
│   │   │   └── 2fa.spec.ts
│   │   ├── content/
│   │   │   ├── list.spec.ts
│   │   │   └── detail.spec.ts
│   │   ├── player/
│   │   │   ├── playback.spec.ts
│   │   │   └── timeline.spec.ts
│   │   └── search/
│   │       ├── basic.spec.ts
│   │       └── autocomplete.spec.ts
│   ├── visual/                    # 시각적 회귀 테스트
│   │   ├── snapshots/
│   │   └── visual.spec.ts
│   └── performance/               # 성능 테스트
│       └── web-vitals.spec.ts
│
└── features/                      # 블럭별 AGENT_RULES.md
    └── {domain}/
        └── AGENT_RULES.md
```

### 3.2 Domain-Block 테스트 매핑

| Domain | Block | 테스트 스펙 | 자동화 레벨 |
|--------|-------|------------|------------|
| auth | validate, token, session | `e2e/specs/auth/*.spec.ts` | 100% 자동 |
| content | query, cache, hands, timeline | `e2e/specs/content/*.spec.ts` | 100% 자동 |
| stream | resolve, transcode, deliver | `e2e/specs/player/*.spec.ts` | 100% 자동 |
| search | parse, search, rank | `e2e/specs/search/*.spec.ts` | 100% 자동 |

---

## 4. Playwright 통합 전략

### 4.1 Playwright 설정

```typescript
// e2e/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs',

  // 병렬 실행으로 속도 최적화
  fullyParallel: true,
  workers: process.env.CI ? 4 : undefined,

  // 재시도 정책 (자동 수정 후 재시도 대비)
  retries: process.env.CI ? 2 : 0,

  // 리포터 설정 (최종 보고서용)
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['github'],  // GitHub Actions 통합
  ],

  // 글로벌 설정
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  // 브라우저별 설정
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // 모바일 뷰포트
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // 웹 서버 자동 시작
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

### 4.2 픽스처 설계

```typescript
// e2e/fixtures/auth.fixture.ts
import { test as base, expect } from '@playwright/test';

// 인증된 사용자 픽스처
export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    // 로그인 수행
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="submit"]');

    // 로그인 완료 대기
    await expect(page).toHaveURL('/dashboard');

    // 픽스처 제공
    await use(page);

    // 정리: 로그아웃
    await page.click('[data-testid="logout"]');
  },
});

export { expect } from '@playwright/test';
```

### 4.3 E2E 테스트 예시

```typescript
// e2e/specs/auth/login.spec.ts
import { test, expect } from '../../fixtures/auth.fixture';

test.describe('로그인 기능', () => {
  test('유효한 자격증명으로 로그인 성공', async ({ page }) => {
    await page.goto('/login');

    // 입력
    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'validPassword');
    await page.click('[data-testid="submit"]');

    // 검증
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('잘못된 비밀번호로 로그인 실패', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'wrongPassword');
    await page.click('[data-testid="submit"]');

    // 에러 메시지 검증
    await expect(page.locator('[data-testid="error-message"]'))
      .toHaveText('이메일 또는 비밀번호가 잘못되었습니다.');
  });

  test('빈 필드 제출 시 검증 오류', async ({ page }) => {
    await page.goto('/login');
    await page.click('[data-testid="submit"]');

    // 필드별 에러 확인
    await expect(page.locator('[data-testid="email-error"]'))
      .toHaveText('이메일을 입력해주세요.');
    await expect(page.locator('[data-testid="password-error"]'))
      .toHaveText('비밀번호를 입력해주세요.');
  });
});
```

### 4.4 시각적 회귀 테스트

```typescript
// e2e/visual/visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('시각적 회귀 테스트', () => {
  test('로그인 페이지 스냅샷', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveScreenshot('login-page.png', {
      maxDiffPixels: 100,
    });
  });

  test('대시보드 스냅샷', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard.png', {
      maxDiffPixels: 100,
    });
  });

  test('플레이어 UI 스냅샷', async ({ authenticatedPage: page }) => {
    await page.goto('/player/1');
    await page.waitForSelector('[data-testid="video-player"]');
    await expect(page).toHaveScreenshot('player.png', {
      maxDiffPixels: 200,  // 비디오 프레임 변동 허용
    });
  });
});
```

### 4.5 성능 테스트

```typescript
// e2e/performance/web-vitals.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Web Vitals 성능 테스트', () => {
  test('LCP (Largest Contentful Paint) < 2.5s', async ({ page }) => {
    await page.goto('/');

    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      });
    });

    expect(lcp).toBeLessThan(2500);
  });

  test('FID (First Input Delay) < 100ms', async ({ page }) => {
    await page.goto('/');

    // 첫 입력 시뮬레이션
    await page.click('button');

    const fid = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          if (entries.length > 0) {
            resolve(entries[0].processingStart - entries[0].startTime);
          }
        }).observe({ type: 'first-input', buffered: true });
      });
    });

    expect(fid).toBeLessThan(100);
  });

  test('CLS (Cumulative Layout Shift) < 0.1', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          resolve(clsValue);
        }).observe({ type: 'layout-shift', buffered: true });

        setTimeout(() => resolve(clsValue), 5000);
      });
    });

    expect(cls).toBeLessThan(0.1);
  });
});
```

---

## 5. 작업 분류 체계

### 5.1 자동화 가능 작업 (Auto-Verify)

```python
AUTO_VERIFY_TASKS = {
    # 코드 품질
    "compile": "타입스크립트 컴파일",
    "lint": "ESLint/Prettier 검사",
    "type_check": "타입 체크",

    # 테스트
    "unit_test": "단위 테스트 (Vitest)",
    "integration_test": "통합 테스트",
    "e2e_test": "E2E 테스트 (Playwright)",
    "visual_regression": "시각적 회귀 테스트",
    "performance": "성능 벤치마크",

    # 보안
    "dependency_audit": "의존성 취약점 스캔",
    "secrets_scan": "시크릿 노출 검사",

    # API
    "api_contract": "API 스키마 검증",
    "api_compatibility": "API 하위호환성 검사",
}
```

### 5.2 사용자 검증 필수 작업 (Human-Verify)

```python
HUMAN_VERIFY_TASKS = {
    # 디자인
    "ui_approval": "UI/UX 디자인 최종 승인",
    "accessibility_final": "접근성 최종 검토",

    # 비즈니스
    "business_logic": "비즈니스 로직 검토",
    "pricing_change": "가격/요금 변경 승인",

    # 보안/규정
    "security_policy": "보안 정책 결정",
    "compliance": "법적/규정 준수 확인",

    # 외부 연동
    "third_party": "외부 시스템 연동 승인",
    "production_deploy": "프로덕션 배포 승인",
}
```

### 5.3 작업 분류 의사결정 트리

```
┌─────────────────────────────────────────────────────────────┐
│                   TASK CLASSIFICATION TREE                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌─────────────────┐                       │
│                    │  새 작업 발생    │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│               ┌─────────────▼─────────────┐                  │
│               │  코드로 검증 가능한가?     │                  │
│               └─────────────┬─────────────┘                  │
│                    YES      │      NO                        │
│               ┌─────────────┴─────────────┐                  │
│               ▼                           ▼                  │
│      ┌───────────────┐           ┌───────────────┐          │
│      │  자동 검증    │           │  주관적 판단   │          │
│      │  (Auto)       │           │  필요한가?     │          │
│      └───────┬───────┘           └───────┬───────┘          │
│              │                      YES  │  NO               │
│              │               ┌───────────┴───────────┐       │
│              │               ▼                       ▼       │
│              │      ┌───────────────┐       ┌───────────────┐│
│              │      │  사용자 검증  │       │  자동 검증    ││
│              │      │  (Human)      │       │  (Auto)       ││
│              │      └───────────────┘       └───────────────┘│
│              │              │                       │        │
│              ▼              ▼                       ▼        │
│      ┌──────────────────────────────────────────────────┐   │
│      │            작업 큐에 추가                          │   │
│      │  ┌────────────────────────────────────────────┐  │   │
│      │  │  Auto Queue: [compile, lint, test, ...]    │  │   │
│      │  │  Human Queue: [ui_approval, ...]           │  │   │
│      │  └────────────────────────────────────────────┘  │   │
│      └──────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 워크플로우 설계

### 6.1 자동 검증 루프

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTO-VERIFY LOOP                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌─────────────────┐                       │
│                    │  구현 완료      │                       │
│                    └────────┬────────┘                       │
│                             │                                │
│                    ┌────────▼────────┐                       │
│            ┌──────▶│  E2E 테스트 실행 │◀──────┐              │
│            │       └────────┬────────┘       │              │
│            │                │                │              │
│            │       ┌────────▼────────┐       │              │
│            │       │   통과 여부?    │       │              │
│            │       └────────┬────────┘       │              │
│            │          PASS  │  FAIL          │              │
│            │       ┌────────┴────────┐       │              │
│            │       ▼                 ▼       │              │
│            │  ┌─────────┐      ┌─────────┐   │              │
│            │  │ 다음    │      │ 실패    │   │              │
│            │  │ 단계    │      │ 분석    │   │              │
│            │  └────┬────┘      └────┬────┘   │              │
│            │       │                │        │              │
│            │       │       ┌────────▼────────┐              │
│            │       │       │  AI 자동 수정   │              │
│            │       │       └────────┬────────┘              │
│            │       │                │                       │
│            │       │       ┌────────▼────────┐              │
│            │       │       │  재시도 < 3?    │              │
│            │       │       └────────┬────────┘              │
│            │       │          YES   │   NO                  │
│            │       │       ┌────────┴────────┐              │
│            │       │       │                 ▼              │
│            └───────┼───────┘        ┌─────────────┐         │
│                    │                │  에스컬레이션│         │
│                    │                │  (보고)      │         │
│                    │                └─────────────┘         │
│                    │                                        │
│           ┌────────▼────────┐                               │
│           │  모든 테스트    │                               │
│           │  통과?          │                               │
│           └────────┬────────┘                               │
│                YES │                                        │
│           ┌────────▼────────┐                               │
│           │  최종 보고서    │                               │
│           │  생성           │                               │
│           └────────┬────────┘                               │
│                    │                                        │
│           ┌────────▼────────┐                               │
│           │  사용자 검증    │                               │
│           │  태스크 실행    │                               │
│           └─────────────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 워크플로우 상세 (Phase 4-6)

```python
# Phase 4: E2E 자동 검증
async def phase_4_auto_verify(changes: ChangeSet) -> VerifyResult:
    """
    모든 자동화 가능한 검증 수행
    실패 시 자동 수정 시도 (최대 3회)
    """

    max_retries = 3

    for attempt in range(max_retries):
        # 4.1: 컴파일 + 타입 체크
        compile_result = await run_compile()
        if not compile_result.success:
            await auto_fix_compile_errors(compile_result.errors)
            continue

        # 4.2: 린트
        lint_result = await run_lint()
        if not lint_result.success:
            await auto_fix_lint_errors(lint_result.errors)
            continue

        # 4.3: 단위 테스트
        unit_result = await run_unit_tests(
            scope=get_affected_files(changes)
        )
        if not unit_result.success:
            await auto_fix_test_failures(unit_result.failures)
            continue

        # 4.4: E2E 테스트 (Playwright)
        e2e_result = await run_playwright_tests(
            specs=get_relevant_specs(changes),
            browsers=['chromium', 'firefox', 'webkit'],
            parallel=True
        )
        if not e2e_result.success:
            await auto_fix_e2e_failures(e2e_result.failures)
            continue

        # 4.5: 시각적 회귀 테스트
        visual_result = await run_visual_tests()
        if not visual_result.success:
            # 시각적 변경은 자동 수정 불가 → 스냅샷 업데이트 제안
            await suggest_snapshot_update(visual_result.diffs)

        # 4.6: 성능 테스트
        perf_result = await run_performance_tests()
        if not perf_result.success:
            await analyze_performance_regression(perf_result)

        # 모든 테스트 통과
        return VerifyResult(
            success=True,
            attempts=attempt + 1,
            results={
                'compile': compile_result,
                'lint': lint_result,
                'unit': unit_result,
                'e2e': e2e_result,
                'visual': visual_result,
                'performance': perf_result,
            }
        )

    # 3회 재시도 후에도 실패
    return VerifyResult(
        success=False,
        attempts=max_retries,
        escalation_required=True,
        failures=collect_all_failures()
    )


# Phase 5: 최종 보고서 생성
async def phase_5_generate_report(verify_result: VerifyResult) -> Report:
    """
    간결한 최종 보고서 생성
    성공 시: 변경 요약 + PR 링크
    실패 시: 실패 원인 + 해결 제안
    """

    return Report(
        status='success' if verify_result.success else 'failed',
        summary=generate_summary(verify_result),
        changes=summarize_changes(),
        test_coverage=calculate_coverage(),
        pr_link=create_pr_if_success(verify_result),
        human_tasks=extract_human_tasks() if verify_result.success else []
    )


# Phase 6: 사용자 검증 태스크
async def phase_6_human_verification(report: Report) -> HumanTaskList:
    """
    반드시 사람이 필요한 검증 항목만 요청
    모든 자동 검증 완료 후 마지막에 실행
    """

    human_tasks = []

    # UI 변경이 있는 경우
    if has_ui_changes(report):
        human_tasks.append({
            'type': 'ui_review',
            'description': 'UI 변경사항 최종 검토',
            'attachments': get_screenshots(),
        })

    # 비즈니스 로직 변경이 있는 경우
    if has_business_logic_changes(report):
        human_tasks.append({
            'type': 'logic_review',
            'description': '비즈니스 로직 검토',
            'changes': get_logic_diff(),
        })

    # 보안 관련 변경이 있는 경우
    if has_security_changes(report):
        human_tasks.append({
            'type': 'security_review',
            'description': '보안 변경사항 검토',
            'changes': get_security_diff(),
        })

    return HumanTaskList(
        tasks=human_tasks,
        estimated_time=estimate_review_time(human_tasks),
        priority=calculate_priority(human_tasks),
    )
```

### 6.3 /work-wsoptv 확장

기존 `/work-wsoptv` 커맨드에 E2E 자동화 페이즈를 추가합니다:

```markdown
## 실행 흐름 (확장)

```
/work-wsoptv 실행
    │
    ├─ Phase 0: Agent 라우팅
    │      └─ (기존)
    │
    ├─ Phase 1: 컨텍스트 분석
    │      └─ (기존)
    │
    ├─ Phase 2: 이슈 + 브랜치
    │      └─ (기존)
    │
    ├─ Phase 3: 구현
    │      └─ (기존)
    │
    ├─ Phase 4: 🆕 E2E 자동 검증 ──────────────────────────────┐
    │      │                                                    │
    │      ├─ Step 4.1: 타입 체크                               │
    │      │      npx tsc --noEmit                              │
    │      │                                                    │
    │      ├─ Step 4.2: 린트                                    │
    │      │      npm run lint                                  │
    │      │                                                    │
    │      ├─ Step 4.3: 단위 테스트                             │
    │      │      npm run test:unit -- --coverage               │
    │      │                                                    │
    │      ├─ Step 4.4: E2E 테스트                              │
    │      │      npx playwright test --reporter=html           │
    │      │      └─ 병렬 실행 (4 workers)                      │
    │      │      └─ 3개 브라우저 (Chromium/Firefox/WebKit)     │
    │      │                                                    │
    │      ├─ Step 4.5: 시각적 회귀 테스트                      │
    │      │      npx playwright test visual/                   │
    │      │                                                    │
    │      ├─ Step 4.6: 성능 테스트                             │
    │      │      npx playwright test performance/              │
    │      │                                                    │
    │      └─ Step 4.7: 실패 시 자동 수정 (최대 3회)            │
    │             AI가 에러 분석 → 수정 → 재실행            ────┘
    │
    ├─ Phase 5: 🆕 최종 보고서 생성
    │      │
    │      ├─ 변경 요약
    │      ├─ 테스트 결과 (커버리지, 통과율)
    │      ├─ 성능 메트릭
    │      └─ PR 링크
    │
    └─ Phase 6: 🆕 사용자 검증 태스크
           │
           ├─ (자동 검증 후 남은 항목만)
           ├─ UI/UX 최종 확인 (해당 시)
           └─ 비즈니스 로직 검토 (해당 시)
```

---

## 7. 구현 가이드

### 7.1 패키지 설치

```bash
# Playwright 설치
npm init playwright@latest

# 추가 패키지
npm install -D @playwright/test axe-playwright lighthouse
```

### 7.2 스크립트 설정

```json
// package.json
{
  "scripts": {
    "test:unit": "vitest",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:visual": "playwright test visual/",
    "test:performance": "playwright test performance/",
    "test:all": "npm run test:unit && npm run test:e2e",
    "test:ci": "npm run test:unit -- --coverage && npm run test:e2e"
  }
}
```

### 7.3 도메인별 테스트 스펙 템플릿

```typescript
// e2e/specs/{domain}/{feature}.spec.ts 템플릿
import { test, expect } from '../../fixtures/base.fixture';

/**
 * {Domain} - {Feature} E2E 테스트
 *
 * AGENT_RULES 참조: apps/web/features/{domain}/AGENT_RULES.md
 *
 * 자동화 레벨: 100%
 * 브라우저: Chromium, Firefox, WebKit
 * 재시도: CI에서 2회
 */
test.describe('{Feature} 기능', () => {
  test.beforeEach(async ({ page }) => {
    // 테스트 전 설정
  });

  test.afterEach(async ({ page }) => {
    // 테스트 후 정리
  });

  test('정상 케이스', async ({ page }) => {
    // Given
    // When
    // Then
  });

  test('예외 케이스', async ({ page }) => {
    // Given
    // When
    // Then
  });

  test('경계값 케이스', async ({ page }) => {
    // Given
    // When
    // Then
  });
});
```

---

## 8. CI/CD 통합

### 8.1 GitHub Actions 워크플로우

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Unit Tests
        run: npm run test:unit -- --coverage

      - name: Run E2E Tests
        run: npm run test:e2e

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### 8.2 자동 재시도 + 보고

```yaml
# .github/workflows/auto-fix.yml
name: Auto Fix & Retry

on:
  workflow_run:
    workflows: ["E2E Tests"]
    types: [completed]

jobs:
  auto-fix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Analyze Failures
        id: analyze
        run: |
          # 실패 분석 및 자동 수정 시도
          echo "Analyzing test failures..."

      - name: Auto Fix
        if: steps.analyze.outputs.fixable == 'true'
        run: |
          # AI 기반 자동 수정
          echo "Attempting auto-fix..."

      - name: Retry Tests
        run: npm run test:e2e

      - name: Report Results
        uses: actions/github-script@v7
        with:
          script: |
            // PR에 결과 코멘트
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '## E2E 테스트 결과\n...'
            });
```

---

## 9. 보고서 형식

### 9.1 최종 보고서 템플릿

```markdown
# /work-wsoptv 완료 보고서

## 작업 정보
- **지시**: {instruction}
- **도메인**: {domain}
- **블럭**: features/{domain}/

## E2E 검증 결과

### 테스트 요약
| 항목 | 결과 |
|------|------|
| 타입 체크 | ✅ 통과 |
| 린트 | ✅ 통과 |
| 단위 테스트 | ✅ 42/42 통과 (100%) |
| E2E 테스트 | ✅ 15/15 통과 |
| 시각적 회귀 | ✅ 변경 없음 |
| 성능 | ✅ LCP 1.2s, FID 45ms, CLS 0.02 |

### 커버리지
- 라인: 87.5%
- 브랜치: 82.3%
- 함수: 91.2%

### 자동 수정 이력
- 시도: 0회 (첫 시도에 성공)

## 결과
- **커밋**: a1b2c3d
- **PR**: #45

---

## 사용자 검증 태스크

> 아래 항목은 자동 검증이 불가능하여 확인이 필요합니다.

- [ ] **UI 확인**: 새로운 버튼 디자인 최종 승인
  - 📎 스크린샷: [link]

- [ ] **동작 확인**: 2FA 플로우 사용자 경험 검토
  - 📎 시연 영상: [link]

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 9.2 실패 시 보고서 템플릿

```markdown
# /work-wsoptv 실패 보고서

## 작업 정보
- **지시**: {instruction}
- **도메인**: {domain}
- **블럭**: features/{domain}/

## 실패 요약

### 테스트 결과
| 항목 | 결과 |
|------|------|
| 타입 체크 | ✅ 통과 |
| 린트 | ✅ 통과 |
| 단위 테스트 | ✅ 40/42 통과 |
| E2E 테스트 | ❌ 12/15 통과 |
| 시각적 회귀 | ⚠️ 2개 변경 감지 |

### 실패 상세

#### E2E 실패 (3개)
1. `auth/login.spec.ts:45` - 로그인 후 리다이렉트 실패
   - 예상: `/dashboard`
   - 실제: `/login`

2. `player/playback.spec.ts:78` - 비디오 로드 타임아웃
   - 원인: API 응답 지연 (>10s)

3. `search/autocomplete.spec.ts:23` - 자동완성 결과 불일치
   - 예상: 5개 결과
   - 실제: 0개 결과

### 자동 수정 시도
- **1차 시도**: 리다이렉트 로직 수정 → 실패
- **2차 시도**: 타임아웃 증가 → 실패
- **3차 시도**: API 호출 순서 변경 → 실패

### 에스컬레이션 사유
자동 수정 3회 시도 후에도 해결되지 않았습니다.
사람의 개입이 필요합니다.

---

## 권장 조치

1. **API 팀 확인 필요**: 검색 API 응답 지연 조사
2. **인증 로직 검토**: 리다이렉트 조건 재확인
3. **비디오 스트리밍 상태 확인**: HLS 서버 상태 점검

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 제안서 작성 |

---

## 참조

### 외부 리소스
- [Playwright 공식 문서](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Web Vitals](https://web.dev/vitals/)

### 관련 문서
- [Block Agent System Architecture](../architecture/0001-block-agent-system.md)
- [/work-wsoptv Command](../../.claude/commands/work-wsoptv.md)
