/**
 * Search Feature - Public API
 *
 * 검색 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { SearchBar, useSearch } from '@/features/search';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
// export { SearchBar } from './components/SearchBar';
// export { SearchResults } from './components/SearchResults';
// export { SearchFilters } from './components/SearchFilters';
// export { Autocomplete } from './components/Autocomplete';
// export { FacetList } from './components/FacetList';

// ============================================================================
// Hooks
// ============================================================================
// export { useSearch } from './hooks/useSearch';
// export { useAutocomplete } from './hooks/useAutocomplete';
// export { useFacets } from './hooks/useFacets';

// ============================================================================
// Stores
// ============================================================================
// export { useSearchStore } from './stores/searchStore';

// ============================================================================
// Types
// ============================================================================
export type {
  SearchQuery,
  SearchFilters,
  SortOption,
  HandGrade,
  SearchResult,
  SearchHit,
  SearchHighlight,
  Facet,
  FacetValue,
  SuggestQuery,
  Suggestion,
  SuggestionType,
  SearchState,
  SearchActions,
  SearchErrorCode,
  SearchError,
  SearchConfig,
} from './types';

export { DEFAULT_SEARCH_CONFIG } from './types';
