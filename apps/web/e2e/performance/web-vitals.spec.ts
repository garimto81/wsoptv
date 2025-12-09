/**
 * Performance Tests - Web Vitals
 *
 * Web Vitals 성능 벤치마크 테스트
 *
 * @see docs/proposals/0001-e2e-automation-workflow.md
 * @see https://web.dev/vitals/
 */

import { test, expect } from '@playwright/test';

/**
 * Web Vitals 임계값 (Good 기준)
 */
const THRESHOLDS = {
  LCP: 2500, // Largest Contentful Paint < 2.5s
  FID: 100, // First Input Delay < 100ms
  CLS: 0.1, // Cumulative Layout Shift < 0.1
  TTFB: 800, // Time to First Byte < 800ms
  FCP: 1800, // First Contentful Paint < 1.8s
  TTI: 3800, // Time to Interactive < 3.8s
};

test.describe('Web Vitals 성능 테스트', () => {
  test.describe('Core Web Vitals', () => {
    test('LCP (Largest Contentful Paint) < 2.5s', async ({ page }) => {
      await page.goto('/');

      // LCP 측정
      const lcp = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          let lcpValue = 0;

          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1] as PerformanceEntry & {
              startTime: number;
            };
            lcpValue = lastEntry.startTime;
          });

          observer.observe({ type: 'largest-contentful-paint', buffered: true });

          // 5초 후 결과 반환
          setTimeout(() => {
            observer.disconnect();
            resolve(lcpValue);
          }, 5000);
        });
      });

      console.log(`LCP: ${lcp}ms`);
      expect(lcp).toBeLessThan(THRESHOLDS.LCP);
    });

    test('CLS (Cumulative Layout Shift) < 0.1', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // CLS 측정
      const cls = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          let clsValue = 0;

          const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              const layoutShiftEntry = entry as PerformanceEntry & {
                hadRecentInput: boolean;
                value: number;
              };
              if (!layoutShiftEntry.hadRecentInput) {
                clsValue += layoutShiftEntry.value;
              }
            }
          });

          observer.observe({ type: 'layout-shift', buffered: true });

          // 5초 후 결과 반환
          setTimeout(() => {
            observer.disconnect();
            resolve(clsValue);
          }, 5000);
        });
      });

      console.log(`CLS: ${cls}`);
      expect(cls).toBeLessThan(THRESHOLDS.CLS);
    });

    test('FCP (First Contentful Paint) < 1.8s', async ({ page }) => {
      await page.goto('/');

      // FCP 측정
      const fcp = await page.evaluate(() => {
        const paintEntries = performance.getEntriesByType(
          'paint'
        ) as PerformanceEntry[];
        const fcpEntry = paintEntries.find(
          (entry) => entry.name === 'first-contentful-paint'
        );
        return fcpEntry ? fcpEntry.startTime : 0;
      });

      console.log(`FCP: ${fcp}ms`);
      expect(fcp).toBeLessThan(THRESHOLDS.FCP);
    });
  });

  test.describe('추가 성능 메트릭', () => {
    test('TTFB (Time to First Byte) < 800ms', async ({ page }) => {
      await page.goto('/');

      // TTFB 측정
      const ttfb = await page.evaluate(() => {
        const navigation = performance.getEntriesByType(
          'navigation'
        )[0] as PerformanceNavigationTiming;
        return navigation.responseStart - navigation.requestStart;
      });

      console.log(`TTFB: ${ttfb}ms`);
      expect(ttfb).toBeLessThan(THRESHOLDS.TTFB);
    });

    test('페이지 로드 시간 < 3s', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/');
      await page.waitForLoadState('load');

      const loadTime = Date.now() - startTime;

      console.log(`Page Load Time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(3000);
    });

    test('DOM 요소 수 < 1500', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      const domElements = await page.evaluate(() => {
        return document.querySelectorAll('*').length;
      });

      console.log(`DOM Elements: ${domElements}`);
      expect(domElements).toBeLessThan(1500);
    });
  });

  test.describe('리소스 성능', () => {
    test('총 리소스 크기 < 5MB', async ({ page }) => {
      let totalSize = 0;

      page.on('response', async (response) => {
        try {
          const buffer = await response.body();
          totalSize += buffer.length;
        } catch {
          // 일부 응답은 body를 가져올 수 없음
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const sizeMB = totalSize / (1024 * 1024);
      console.log(`Total Resource Size: ${sizeMB.toFixed(2)}MB`);
      expect(sizeMB).toBeLessThan(5);
    });

    test('JavaScript 번들 크기 < 500KB', async ({ page }) => {
      let jsSize = 0;

      page.on('response', async (response) => {
        const contentType = response.headers()['content-type'] || '';
        if (contentType.includes('javascript')) {
          try {
            const buffer = await response.body();
            jsSize += buffer.length;
          } catch {
            // ignore
          }
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const sizeKB = jsSize / 1024;
      console.log(`JavaScript Size: ${sizeKB.toFixed(2)}KB`);
      expect(sizeKB).toBeLessThan(500);
    });

    test('CSS 크기 < 100KB', async ({ page }) => {
      let cssSize = 0;

      page.on('response', async (response) => {
        const contentType = response.headers()['content-type'] || '';
        if (contentType.includes('css')) {
          try {
            const buffer = await response.body();
            cssSize += buffer.length;
          } catch {
            // ignore
          }
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const sizeKB = cssSize / 1024;
      console.log(`CSS Size: ${sizeKB.toFixed(2)}KB`);
      expect(sizeKB).toBeLessThan(100);
    });

    test('이미지 최적화 - WebP/AVIF 사용', async ({ page }) => {
      const imageFormats: string[] = [];

      page.on('response', async (response) => {
        const contentType = response.headers()['content-type'] || '';
        if (contentType.includes('image')) {
          imageFormats.push(contentType);
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // 최소 50%의 이미지가 최적화된 포맷 사용
      const optimizedFormats = imageFormats.filter(
        (format) => format.includes('webp') || format.includes('avif')
      );

      if (imageFormats.length > 0) {
        const optimizedRatio = optimizedFormats.length / imageFormats.length;
        console.log(`Optimized Images: ${(optimizedRatio * 100).toFixed(1)}%`);
        expect(optimizedRatio).toBeGreaterThan(0.5);
      }
    });
  });

  test.describe('페이지별 성능', () => {
    const pages = [
      { name: '홈', path: '/' },
      { name: '콘텐츠 목록', path: '/contents' },
      { name: '검색 결과', path: '/search?q=poker' },
      { name: '로그인', path: '/login' },
    ];

    for (const pageInfo of pages) {
      test(`${pageInfo.name} 페이지 LCP < 2.5s`, async ({ page }) => {
        await page.goto(pageInfo.path);

        const lcp = await page.evaluate(() => {
          return new Promise<number>((resolve) => {
            let lcpValue = 0;

            const observer = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const lastEntry = entries[entries.length - 1] as PerformanceEntry & {
                startTime: number;
              };
              lcpValue = lastEntry.startTime;
            });

            observer.observe({
              type: 'largest-contentful-paint',
              buffered: true,
            });

            setTimeout(() => {
              observer.disconnect();
              resolve(lcpValue);
            }, 5000);
          });
        });

        console.log(`${pageInfo.name} LCP: ${lcp}ms`);
        expect(lcp).toBeLessThan(THRESHOLDS.LCP);
      });
    }
  });
});
