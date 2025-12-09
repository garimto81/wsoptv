/**
 * Content Store
 *
 * Svelte 5 runes 기반 콘텐츠 상태 관리
 * @see ../AGENT_RULES.md
 */

import type {
  Content,
  ContentDetail,
  ContentQuery,
  Hand,
  Catalog,
  ContentState,
  ContentError
} from '../types';
import { DEFAULT_CACHE_CONFIG } from '../types';
import * as contentApi from '../api/contentApi';

// ============================================================================
// Store State (Svelte 5 Runes)
// ============================================================================

let contents = $state<Content[]>([]);
let selectedContent = $state<ContentDetail | null>(null);
let hands = $state<Hand[]>([]);
let catalogs = $state<Catalog[]>([]);
let isLoading = $state(false);
let isDetailLoading = $state(false);
let error = $state<ContentError | null>(null);
let page = $state(1);
let hasMore = $state(true);
let currentQuery = $state<ContentQuery>({});

// ============================================================================
// Derived State
// ============================================================================

const state = $derived<ContentState>({
  contents,
  selectedContent,
  hands,
  catalogs,
  isLoading,
  isDetailLoading,
  error,
  page,
  hasMore
});

// ============================================================================
// Actions
// ============================================================================

/**
 * 콘텐츠 목록 조회
 */
async function fetchContents(query: ContentQuery = {}): Promise<void> {
  isLoading = true;
  error = null;
  currentQuery = query;

  try {
    // 캐시 확인
    const cacheKey = `contents:${JSON.stringify(query)}`;
    const cached = contentApi.getCached<{ items: Content[]; hasMore: boolean }>(
      cacheKey,
      DEFAULT_CACHE_CONFIG.listStaleTime
    );

    if (cached) {
      contents = cached.items;
      hasMore = cached.hasMore;
      page = query.page || 1;
      return;
    }

    const result = await contentApi.fetchContents(query);

    contents = result.items;
    page = result.page;
    hasMore = result.hasMore;

    // 캐시 저장
    contentApi.setCache(cacheKey, { items: result.items, hasMore: result.hasMore });
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as ContentError;
    } else {
      error = { code: 'CONTENT_LOAD_ERROR', message: '콘텐츠를 불러올 수 없습니다' };
    }
  } finally {
    isLoading = false;
  }
}

/**
 * 콘텐츠 더 불러오기 (무한 스크롤)
 */
async function loadMore(): Promise<void> {
  if (isLoading || !hasMore) return;

  const nextPage = page + 1;
  isLoading = true;

  try {
    const result = await contentApi.fetchContents({
      ...currentQuery,
      page: nextPage
    });

    contents = [...contents, ...result.items];
    page = result.page;
    hasMore = result.hasMore;
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as ContentError;
    }
  } finally {
    isLoading = false;
  }
}

/**
 * 콘텐츠 상세 조회
 */
async function fetchContentDetail(id: number): Promise<void> {
  isDetailLoading = true;
  error = null;

  try {
    // 캐시 확인
    const cacheKey = `content:${id}`;
    const cached = contentApi.getCached<ContentDetail>(
      cacheKey,
      DEFAULT_CACHE_CONFIG.detailStaleTime
    );

    if (cached) {
      selectedContent = cached;
      hands = cached.hands || [];
      return;
    }

    const detail = await contentApi.fetchContentDetail(id);
    selectedContent = detail;
    hands = detail.hands || [];

    // 캐시 저장
    contentApi.setCache(cacheKey, detail);
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as ContentError;
    } else {
      error = { code: 'CONTENT_NOT_FOUND', message: '콘텐츠를 찾을 수 없습니다' };
    }
  } finally {
    isDetailLoading = false;
  }
}

/**
 * 핸드 목록 조회
 */
async function fetchHands(contentId: number, gradeFilter?: string[]): Promise<void> {
  try {
    // 캐시 확인
    const cacheKey = `hands:${contentId}:${gradeFilter?.join(',') || 'all'}`;
    const cached = contentApi.getCached<Hand[]>(
      cacheKey,
      DEFAULT_CACHE_CONFIG.handStaleTime
    );

    if (cached) {
      hands = cached;
      return;
    }

    const result = await contentApi.fetchHands(contentId, gradeFilter);
    hands = result;

    // 캐시 저장
    contentApi.setCache(cacheKey, result);
  } catch (e) {
    console.error('Failed to fetch hands:', e);
  }
}

/**
 * 카탈로그 목록 조회
 */
async function fetchCatalogs(): Promise<void> {
  try {
    // 캐시 확인 (카탈로그는 자주 변경되지 않음)
    const cacheKey = 'catalogs';
    const cached = contentApi.getCached<Catalog[]>(cacheKey, 30 * 60 * 1000); // 30분

    if (cached) {
      catalogs = cached;
      return;
    }

    const result = await contentApi.fetchCatalogs();
    catalogs = result;

    // 캐시 저장
    contentApi.setCache(cacheKey, result);
  } catch (e) {
    console.error('Failed to fetch catalogs:', e);
  }
}

/**
 * 선택 초기화
 */
function clearSelection(): void {
  selectedContent = null;
  hands = [];
}

/**
 * 캐시 무효화
 */
function invalidate(pattern?: string): void {
  contentApi.invalidateCache(pattern);
}

// ============================================================================
// Store Export
// ============================================================================

export function useContentStore() {
  return {
    // State (readonly)
    get state() {
      return state;
    },
    get contents() {
      return contents;
    },
    get selectedContent() {
      return selectedContent;
    },
    get hands() {
      return hands;
    },
    get catalogs() {
      return catalogs;
    },
    get isLoading() {
      return isLoading;
    },
    get isDetailLoading() {
      return isDetailLoading;
    },
    get error() {
      return error;
    },
    get page() {
      return page;
    },
    get hasMore() {
      return hasMore;
    },

    // Actions
    fetchContents,
    fetchContentDetail,
    fetchHands,
    fetchCatalogs,
    loadMore,
    clearSelection,
    invalidate
  };
}

export const contentStore = useContentStore();
