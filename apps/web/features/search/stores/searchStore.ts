/**
 * Search Store
 *
 * Svelte 5 runes 기반 검색 상태 관리
 * @see ../AGENT_RULES.md
 */

import type {
  SearchQuery,
  SearchFilters,
  SearchHit,
  Facet,
  Suggestion,
  SearchState,
  SearchError
} from '../types';
import { DEFAULT_SEARCH_CONFIG } from '../types';
import * as searchApi from '../api/searchApi';

// ============================================================================
// Store State (Svelte 5 Runes)
// ============================================================================

let query = $state('');
let filters = $state<SearchFilters>({});
let results = $state<SearchHit[]>([]);
let facets = $state<Facet[]>([]);
let suggestions = $state<Suggestion[]>([]);
let totalHits = $state(0);
let page = $state(1);
let isLoading = $state(false);
let isSuggestLoading = $state(false);
let error = $state<SearchError | null>(null);
let recentSearches = $state<string[]>([]);

// ============================================================================
// Derived State
// ============================================================================

const state = $derived<SearchState>({
  query,
  filters,
  results,
  facets,
  suggestions,
  totalHits,
  page,
  isLoading,
  isSuggestLoading,
  error,
  recentSearches
});

// ============================================================================
// Debounce Helper
// ============================================================================

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
let suggestDebounceTimer: ReturnType<typeof setTimeout> | null = null;

function debounce(fn: () => void, delay: number, timer: 'search' | 'suggest') {
  if (timer === 'search') {
    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(fn, delay);
  } else {
    if (suggestDebounceTimer) clearTimeout(suggestDebounceTimer);
    suggestDebounceTimer = setTimeout(fn, delay);
  }
}

// ============================================================================
// Actions
// ============================================================================

/**
 * 검색 실행
 */
async function search(searchQuery: SearchQuery): Promise<void> {
  isLoading = true;
  error = null;
  query = searchQuery.q;

  try {
    const result = await searchApi.search(searchQuery);

    results = result.hits;
    facets = result.facets;
    totalHits = result.totalHits;
    page = result.page;

    // 검색어 저장
    if (searchQuery.q.trim()) {
      searchApi.addRecentSearch(searchQuery.q);
      recentSearches = searchApi.getRecentSearches();
    }
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as SearchError;
    } else {
      error = { code: 'SEARCH_INDEX_ERROR', message: '검색에 실패했습니다' };
    }
  } finally {
    isLoading = false;
  }
}

/**
 * 디바운스된 검색 실행
 */
function searchDebounced(searchQuery: SearchQuery): void {
  debounce(() => search(searchQuery), DEFAULT_SEARCH_CONFIG.debounceMs, 'search');
}

/**
 * 자동완성 조회
 */
async function suggest(suggestQuery: { q: string; limit?: number }): Promise<void> {
  if (suggestQuery.q.length < DEFAULT_SEARCH_CONFIG.minChars) {
    suggestions = [];
    return;
  }

  isSuggestLoading = true;

  try {
    const result = await searchApi.suggest(suggestQuery);
    suggestions = result;
  } catch {
    suggestions = [];
  } finally {
    isSuggestLoading = false;
  }
}

/**
 * 디바운스된 자동완성
 */
function suggestDebounced(suggestQuery: { q: string; limit?: number }): void {
  debounce(
    () => suggest(suggestQuery),
    DEFAULT_SEARCH_CONFIG.suggestDebounceMs,
    'suggest'
  );
}

/**
 * 필터 설정
 */
function setFilter<K extends keyof SearchFilters>(
  field: K,
  value: SearchFilters[K]
): void {
  filters = { ...filters, [field]: value };
}

/**
 * 모든 필터 초기화
 */
function clearFilters(): void {
  filters = {};
}

/**
 * 페이지 변경
 */
function setPage(newPage: number): void {
  page = newPage;
}

/**
 * 최근 검색어 추가
 */
function addRecentSearchToStore(searchQuery: string): void {
  searchApi.addRecentSearch(searchQuery);
  recentSearches = searchApi.getRecentSearches();
}

/**
 * 최근 검색어 초기화
 */
function clearRecentSearches(): void {
  searchApi.clearRecentSearches();
  recentSearches = [];
}

/**
 * 검색 초기화
 */
function reset(): void {
  query = '';
  filters = {};
  results = [];
  facets = [];
  suggestions = [];
  totalHits = 0;
  page = 1;
  error = null;
}

/**
 * 스토어 초기화 (앱 시작 시)
 */
function initialize(): void {
  recentSearches = searchApi.getRecentSearches();
}

// ============================================================================
// Store Export
// ============================================================================

export function useSearchStore() {
  return {
    // State (readonly)
    get state() {
      return state;
    },
    get query() {
      return query;
    },
    get filters() {
      return filters;
    },
    get results() {
      return results;
    },
    get facets() {
      return facets;
    },
    get suggestions() {
      return suggestions;
    },
    get totalHits() {
      return totalHits;
    },
    get page() {
      return page;
    },
    get isLoading() {
      return isLoading;
    },
    get isSuggestLoading() {
      return isSuggestLoading;
    },
    get error() {
      return error;
    },
    get recentSearches() {
      return recentSearches;
    },

    // Actions
    search,
    searchDebounced,
    suggest,
    suggestDebounced,
    setFilter,
    clearFilters,
    setPage,
    addRecentSearch: addRecentSearchToStore,
    clearRecentSearches,
    reset,
    initialize
  };
}

export const searchStore = useSearchStore();
