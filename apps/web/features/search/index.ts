/**
 * Search Feature - Public API
 *
 * 검색 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { SearchBar, useSearch } from '$features/search';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
export { SearchBar, SearchResults, FacetList } from './components';

// ============================================================================
// Hooks
// ============================================================================
export {
  useSearch,
  useAutocomplete,
  useFacets,
  useRecentSearches,
  highlightText,
  getSuggestionIcon,
  getSuggestionLabel
} from './hooks/useSearch';

// ============================================================================
// Stores
// ============================================================================
export { useSearchStore, searchStore } from './stores/searchStore';

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
