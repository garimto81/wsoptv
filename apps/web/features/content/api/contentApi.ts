/**
 * Content API Functions
 *
 * 콘텐츠 관련 백엔드 API 호출 함수
 * @see ../AGENT_RULES.md
 */

import { getAccessToken } from '$features/auth';
import type {
  Content,
  ContentDetail,
  ContentQuery,
  ContentListResult,
  Hand,
  Catalog,
  WatchProgress,
  WatchProgressUpdate,
  ContentError,
  ContentErrorCode
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE = '/api/v1';

// ============================================================================
// API Error Handling
// ============================================================================

class ContentApiError extends Error {
  code: ContentErrorCode;
  status: number;

  constructor(code: ContentErrorCode, message: string, status: number = 400) {
    super(message);
    this.name = 'ContentApiError';
    this.code = code;
    this.status = status;
  }

  toContentError(): ContentError {
    return { code: this.code, message: this.message };
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const code = mapStatusToErrorCode(response.status);
    throw new ContentApiError(code, error.message || '요청 처리 중 오류가 발생했습니다', response.status);
  }
  return response.json();
}

function mapStatusToErrorCode(status: number): ContentErrorCode {
  switch (status) {
    case 404:
      return 'CONTENT_NOT_FOUND';
    case 403:
      return 'CONTENT_ACCESS_DENIED';
    default:
      return 'CONTENT_LOAD_ERROR';
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
// Content API
// ============================================================================

/**
 * 콘텐츠 목록 조회
 */
export async function fetchContents(query: ContentQuery = {}): Promise<ContentListResult> {
  const params = new URLSearchParams();

  if (query.catalogId) params.set('catalogId', query.catalogId);
  if (query.season) params.set('season', query.season);
  if (query.page) params.set('page', query.page.toString());
  if (query.limit) params.set('limit', query.limit.toString());
  if (query.sort) params.set('sort', query.sort);

  const url = `${API_BASE}/contents?${params.toString()}`;

  const response = await fetch(url, {
    headers: getAuthHeaders()
  });

  return handleResponse<ContentListResult>(response);
}

/**
 * 콘텐츠 상세 조회
 */
export async function fetchContentDetail(id: number): Promise<ContentDetail> {
  const response = await fetch(`${API_BASE}/contents/${id}`, {
    headers: getAuthHeaders()
  });

  return handleResponse<ContentDetail>(response);
}

/**
 * 콘텐츠의 핸드 목록 조회
 */
export async function fetchHands(contentId: number, gradeFilter?: string[]): Promise<Hand[]> {
  const params = new URLSearchParams();
  if (gradeFilter && gradeFilter.length > 0) {
    params.set('grades', gradeFilter.join(','));
  }

  const url = `${API_BASE}/contents/${contentId}/hands?${params.toString()}`;

  const response = await fetch(url, {
    headers: getAuthHeaders()
  });

  return handleResponse<Hand[]>(response);
}

// ============================================================================
// Catalog API
// ============================================================================

/**
 * 카탈로그 목록 조회
 */
export async function fetchCatalogs(): Promise<Catalog[]> {
  const response = await fetch(`${API_BASE}/catalogs`, {
    headers: getAuthHeaders()
  });

  return handleResponse<Catalog[]>(response);
}

/**
 * 카탈로그 상세 조회
 */
export async function fetchCatalog(id: string): Promise<Catalog> {
  const response = await fetch(`${API_BASE}/catalogs/${id}`, {
    headers: getAuthHeaders()
  });

  return handleResponse<Catalog>(response);
}

// ============================================================================
// Watch Progress API
// ============================================================================

/**
 * 시청 진행률 조회
 */
export async function fetchWatchProgress(contentId: number): Promise<WatchProgress | null> {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await fetch(`${API_BASE}/progress/${contentId}`, {
      headers: getAuthHeaders()
    });

    if (response.status === 404) return null;

    return handleResponse<WatchProgress>(response);
  } catch {
    return null;
  }
}

/**
 * 시청 진행률 저장
 */
export async function saveWatchProgress(update: WatchProgressUpdate): Promise<WatchProgress> {
  const response = await fetch(`${API_BASE}/progress`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(update)
  });

  return handleResponse<WatchProgress>(response);
}

/**
 * 사용자의 모든 시청 진행률 조회
 */
export async function fetchAllWatchProgress(): Promise<WatchProgress[]> {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const response = await fetch(`${API_BASE}/progress`, {
      headers: getAuthHeaders()
    });

    return handleResponse<WatchProgress[]>(response);
  } catch {
    return [];
  }
}

// ============================================================================
// Cache Helpers
// ============================================================================

const cache = new Map<string, { data: unknown; timestamp: number }>();

export function getCached<T>(key: string, staleTime: number): T | null {
  const cached = cache.get(key);
  if (!cached) return null;

  const isStale = Date.now() - cached.timestamp > staleTime;
  if (isStale) {
    cache.delete(key);
    return null;
  }

  return cached.data as T;
}

export function setCache<T>(key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() });
}

export function invalidateCache(pattern?: string): void {
  if (!pattern) {
    cache.clear();
    return;
  }

  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      cache.delete(key);
    }
  }
}
