/**
 * Search API Functions
 *
 * 검색 관련 백엔드 API 호출 함수 (MeiliSearch)
 * @see ../AGENT_RULES.md
 */

import { getAccessToken } from '$features/auth';
import type {
  SearchQuery,
  SearchResult,
  SuggestQuery,
  Suggestion,
  SearchError,
  SearchErrorCode
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE = '/api/v1/search';

// ============================================================================
// API Error Handling
// ============================================================================

class SearchApiError extends Error {
  code: SearchErrorCode;
  status: number;

  constructor(code: SearchErrorCode, message: string, status: number = 400) {
    super(message);
    this.name = 'SearchApiError';
    this.code = code;
    this.status = status;
  }

  toSearchError(): SearchError {
    return { code: this.code, message: this.message };
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const code = mapStatusToErrorCode(response.status);
    throw new SearchApiError(code, error.message || '검색 중 오류가 발생했습니다', response.status);
  }
  return response.json();
}

function mapStatusToErrorCode(status: number): SearchErrorCode {
  switch (status) {
    case 400:
      return 'SEARCH_QUERY_INVALID';
    case 408:
    case 504:
      return 'SEARCH_TIMEOUT';
    default:
      return 'SEARCH_INDEX_ERROR';
  }
}

function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// ============================================================================
// Search API
// ============================================================================

/**
 * 전문 검색
 */
export async function search(query: SearchQuery): Promise<SearchResult> {
  const params = new URLSearchParams();

  params.set('q', query.q);
  if (query.page) params.set('page', query.page.toString());
  if (query.limit) params.set('limit', query.limit.toString());
  if (query.sort) params.set('sort', query.sort);

  // 필터 파라미터
  if (query.filters) {
    if (query.filters.catalogId) params.set('catalogId', query.filters.catalogId);
    if (query.filters.handGrade) params.set('handGrade', query.filters.handGrade.join(','));
    if (query.filters.season) params.set('season', query.filters.season);
    if (query.filters.hasHands !== undefined) params.set('hasHands', query.filters.hasHands.toString());
    if (query.filters.minDuration) params.set('minDuration', query.filters.minDuration.toString());
    if (query.filters.maxDuration) params.set('maxDuration', query.filters.maxDuration.toString());
  }

  const url = `${API_BASE}?${params.toString()}`;

  const response = await fetch(url, {
    headers: getAuthHeaders()
  });

  return handleResponse<SearchResult>(response);
}

/**
 * 자동완성 (Suggestions)
 */
export async function suggest(query: SuggestQuery): Promise<Suggestion[]> {
  if (query.q.length < 2) {
    return [];
  }

  const params = new URLSearchParams();
  params.set('q', query.q);
  if (query.limit) params.set('limit', query.limit.toString());

  const url = `${API_BASE}/suggest?${params.toString()}`;

  const response = await fetch(url, {
    headers: getAuthHeaders()
  });

  return handleResponse<Suggestion[]>(response);
}

// ============================================================================
// Recent Searches (Local Storage)
// ============================================================================

const RECENT_SEARCHES_KEY = 'wsoptv_recent_searches';
const MAX_RECENT_SEARCHES = 10;

export function getRecentSearches(): string[] {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function addRecentSearch(query: string): void {
  if (typeof window === 'undefined') return;

  const trimmed = query.trim();
  if (!trimmed) return;

  const searches = getRecentSearches();

  // 중복 제거 및 최신 순으로 정렬
  const filtered = searches.filter((s) => s !== trimmed);
  const updated = [trimmed, ...filtered].slice(0, MAX_RECENT_SEARCHES);

  localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
}

export function clearRecentSearches(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(RECENT_SEARCHES_KEY);
}

// ============================================================================
// Search Helpers
// ============================================================================

/**
 * 쿼리 하이라이트 적용
 */
export function highlightText(text: string, query: string): string {
  if (!query.trim()) return text;

  const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
