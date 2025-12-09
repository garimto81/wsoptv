/**
 * Search Hooks
 *
 * 검색 관련 유틸리티 훅
 * @see ../AGENT_RULES.md
 */

import { searchStore } from '../stores/searchStore';
import { highlightText } from '../api/searchApi';
import type { SearchFilters, Suggestion, SuggestionType } from '../types';
import { DEFAULT_SEARCH_CONFIG } from '../types';

// ============================================================================
// useSearch Hook
// ============================================================================

/**
 * 검색 상태 및 액션 접근 훅
 *
 * @example
 * const { results, search, isLoading } = useSearch();
 */
export function useSearch() {
  return {
    // State
    get query() {
      return searchStore.query;
    },
    get results() {
      return searchStore.results;
    },
    get totalHits() {
      return searchStore.totalHits;
    },
    get page() {
      return searchStore.page;
    },
    get isLoading() {
      return searchStore.isLoading;
    },
    get error() {
      return searchStore.error;
    },
    get facets() {
      return searchStore.facets;
    },

    // Actions
    search: searchStore.search,
    searchDebounced: searchStore.searchDebounced,
    setPage: searchStore.setPage,
    reset: searchStore.reset
  };
}

// ============================================================================
// useAutocomplete Hook
// ============================================================================

/**
 * 자동완성 훅
 *
 * @example
 * const { suggestions, suggest, isLoading } = useAutocomplete();
 */
export function useAutocomplete() {
  let inputValue = $state('');
  let isOpen = $state(false);

  function handleInput(value: string) {
    inputValue = value;

    if (value.length >= DEFAULT_SEARCH_CONFIG.minChars) {
      searchStore.suggestDebounced({ q: value, limit: DEFAULT_SEARCH_CONFIG.maxSuggestions });
      isOpen = true;
    } else {
      isOpen = false;
    }
  }

  function selectSuggestion(suggestion: Suggestion) {
    inputValue = suggestion.text;
    isOpen = false;

    // 검색 실행
    searchStore.search({
      q: suggestion.text,
      filters: searchStore.filters
    });
  }

  function close() {
    isOpen = false;
  }

  return {
    get inputValue() {
      return inputValue;
    },
    get suggestions() {
      return searchStore.suggestions;
    },
    get isLoading() {
      return searchStore.isSuggestLoading;
    },
    get isOpen() {
      return isOpen && searchStore.suggestions.length > 0;
    },

    handleInput,
    selectSuggestion,
    close,
    suggest: searchStore.suggest
  };
}

// ============================================================================
// useFacets Hook
// ============================================================================

/**
 * 패싯 필터 훅
 *
 * @example
 * const { facets, filters, setFilter } = useFacets();
 */
export function useFacets() {
  return {
    get facets() {
      return searchStore.facets;
    },
    get filters() {
      return searchStore.filters;
    },

    setFilter: searchStore.setFilter,
    clearFilters: searchStore.clearFilters,

    /**
     * 필터 적용하여 재검색
     */
    applyFilters(newFilters: Partial<SearchFilters>) {
      Object.entries(newFilters).forEach(([key, value]) => {
        searchStore.setFilter(key as keyof SearchFilters, value);
      });

      searchStore.search({
        q: searchStore.query,
        filters: { ...searchStore.filters, ...newFilters }
      });
    }
  };
}

// ============================================================================
// useRecentSearches Hook
// ============================================================================

/**
 * 최근 검색어 훅
 */
export function useRecentSearches() {
  return {
    get searches() {
      return searchStore.recentSearches;
    },

    add: searchStore.addRecentSearch,
    clear: searchStore.clearRecentSearches,

    /**
     * 최근 검색어로 검색 실행
     */
    searchRecent(query: string) {
      searchStore.search({
        q: query,
        filters: searchStore.filters
      });
    }
  };
}

// ============================================================================
// Search Helpers
// ============================================================================

/**
 * 검색어 하이라이트
 */
export { highlightText };

/**
 * 제안 유형 아이콘
 */
export function getSuggestionIcon(type: SuggestionType): string {
  const icons: Record<SuggestionType, string> = {
    query: '🔍',
    player: '👤',
    content: '🎬',
    catalog: '📁'
  };
  return icons[type];
}

/**
 * 제안 유형 라벨
 */
export function getSuggestionLabel(type: SuggestionType): string {
  const labels: Record<SuggestionType, string> = {
    query: '검색어',
    player: '플레이어',
    content: '콘텐츠',
    catalog: '카탈로그'
  };
  return labels[type];
}
