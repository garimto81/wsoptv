/**
 * Search Feature Types
 *
 * 검색 블럭의 타입 정의
 * @see AGENT_RULES.md
 */

// ============================================================================
// Search Query
// ============================================================================

export interface SearchQuery {
  q: string;
  filters?: SearchFilters;
  page?: number;
  limit?: number;
  sort?: SortOption;
}

export interface SearchFilters {
  catalogId?: string;
  handGrade?: HandGrade[];
  season?: string;
  hasHands?: boolean;
  minDuration?: number;
  maxDuration?: number;
}

export type SortOption = 'relevance' | 'date' | 'episode' | 'popular';
export type HandGrade = 'S' | 'A' | 'B' | 'C';

// ============================================================================
// Search Results
// ============================================================================

export interface SearchResult {
  hits: SearchHit[];
  totalHits: number;
  page: number;
  totalPages: number;
  processingTimeMs: number;
  facets: Facet[];
}

export interface SearchHit {
  id: number;
  title: string;
  catalogName: string;
  episode?: number;
  season?: string;
  thumbnailUrl?: string;
  durationSec: number;
  handCount: number;
  highlights: SearchHighlight[];
  score: number;
}

export interface SearchHighlight {
  field: string;
  snippet: string;
}

// ============================================================================
// Facets
// ============================================================================

export interface Facet {
  field: string;
  label: string;
  values: FacetValue[];
}

export interface FacetValue {
  value: string;
  label: string;
  count: number;
  selected: boolean;
}

// ============================================================================
// Autocomplete
// ============================================================================

export interface SuggestQuery {
  q: string;
  limit?: number;
}

export interface Suggestion {
  text: string;
  type: SuggestionType;
  highlight: string;
  metadata?: {
    catalogId?: string;
    contentId?: number;
  };
}

export type SuggestionType = 'query' | 'player' | 'content' | 'catalog';

// ============================================================================
// Search State
// ============================================================================

export interface SearchState {
  query: string;
  filters: SearchFilters;
  results: SearchHit[];
  facets: Facet[];
  suggestions: Suggestion[];
  totalHits: number;
  page: number;
  isLoading: boolean;
  isSuggestLoading: boolean;
  error: SearchError | null;
  recentSearches: string[];
}

export interface SearchActions {
  search: (query: SearchQuery) => Promise<void>;
  suggest: (query: SuggestQuery) => Promise<void>;
  setFilter: (field: string, value: unknown) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  addRecentSearch: (query: string) => void;
  clearRecentSearches: () => void;
}

// ============================================================================
// Search Errors
// ============================================================================

export type SearchErrorCode =
  | 'SEARCH_INDEX_ERROR'
  | 'SEARCH_QUERY_INVALID'
  | 'SEARCH_TIMEOUT';

export interface SearchError {
  code: SearchErrorCode;
  message: string;
}

// ============================================================================
// Search Configuration
// ============================================================================

export interface SearchConfig {
  debounceMs: number;
  suggestDebounceMs: number;
  minChars: number;
  maxSuggestions: number;
  defaultLimit: number;
  maxLimit: number;
}

export const DEFAULT_SEARCH_CONFIG: SearchConfig = {
  debounceMs: 300,
  suggestDebounceMs: 150,
  minChars: 2,
  maxSuggestions: 8,
  defaultLimit: 20,
  maxLimit: 50,
};
