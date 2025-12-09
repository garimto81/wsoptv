/**
 * Content Feature Types
 *
 * 콘텐츠 블럭의 타입 정의
 * @see AGENT_RULES.md
 */

// ============================================================================
// Content Types
// ============================================================================

export interface Content {
  id: number;
  catalogId: string;
  catalogName: string;
  title: string;
  episode?: number;
  season?: string;
  fileId: number;
  durationSec: number;
  thumbnailUrl?: string;
  handCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface ContentDetail extends Content {
  description?: string;
  players: string[];
  hands: Hand[];
  relatedContents?: ContentPreview[];
}

export interface ContentPreview {
  id: number;
  title: string;
  thumbnailUrl?: string;
  durationSec: number;
}

// ============================================================================
// Hand Types
// ============================================================================

export interface Hand {
  id: number;
  contentId: number;
  handNumber: number;
  grade: HandGrade;
  startSec: number;
  endSec: number;
  players: string[];
  potSize?: number;
  description?: string;
}

export type HandGrade = 'S' | 'A' | 'B' | 'C';

// ============================================================================
// Episode Types
// ============================================================================

export interface Episode {
  id: number;
  catalogId: string;
  episode: number;
  title: string;
  contentId: number;
}

export interface Catalog {
  id: string;
  name: string;
  description?: string;
  thumbnailUrl?: string;
  episodeCount: number;
}

// ============================================================================
// Content Query
// ============================================================================

export interface ContentQuery {
  catalogId?: string;
  season?: string;
  page?: number;
  limit?: number;
  sort?: ContentSortOption;
}

export type ContentSortOption = 'recent' | 'episode' | 'popular' | 'hands';

export interface ContentListResult {
  items: Content[];
  total: number;
  page: number;
  totalPages: number;
  hasMore: boolean;
}

// ============================================================================
// Watch Progress
// ============================================================================

export interface WatchProgress {
  contentId: number;
  userId: number;
  progressSec: number;
  durationSec: number;
  completed: boolean;
  lastWatchedAt: string;
}

export interface WatchProgressUpdate {
  contentId: number;
  progressSec: number;
  durationSec: number;
}

// ============================================================================
// Content State
// ============================================================================

export interface ContentState {
  contents: Content[];
  selectedContent: ContentDetail | null;
  hands: Hand[];
  catalogs: Catalog[];
  isLoading: boolean;
  isDetailLoading: boolean;
  error: ContentError | null;
  page: number;
  hasMore: boolean;
}

export interface ContentActions {
  fetchContents: (query: ContentQuery) => Promise<void>;
  fetchContentDetail: (id: number) => Promise<void>;
  fetchHands: (contentId: number) => Promise<void>;
  fetchCatalogs: () => Promise<void>;
  loadMore: () => Promise<void>;
  clearSelection: () => void;
}

// ============================================================================
// Content Errors
// ============================================================================

export type ContentErrorCode =
  | 'CONTENT_NOT_FOUND'
  | 'CONTENT_ACCESS_DENIED'
  | 'CONTENT_LOAD_ERROR';

export interface ContentError {
  code: ContentErrorCode;
  message: string;
}

// ============================================================================
// Cache Configuration
// ============================================================================

export interface ContentCacheConfig {
  listStaleTime: number;
  detailStaleTime: number;
  handStaleTime: number;
  progressStaleTime: number;
}

export const DEFAULT_CACHE_CONFIG: ContentCacheConfig = {
  listStaleTime: 5 * 60 * 1000,      // 5분
  detailStaleTime: 10 * 60 * 1000,   // 10분
  handStaleTime: 30 * 60 * 1000,     // 30분
  progressStaleTime: 0,              // 항상 최신
};
