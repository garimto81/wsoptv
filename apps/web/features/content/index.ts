/**
 * Content Feature - Public API
 *
 * 콘텐츠 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { ContentCard, useContent } from '@/features/content';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
// export { ContentCard } from './components/ContentCard';
// export { ContentList } from './components/ContentList';
// export { ContentDetail } from './components/ContentDetail';
// export { HandList } from './components/HandList';
// export { EpisodeSelector } from './components/EpisodeSelector';

// ============================================================================
// Hooks
// ============================================================================
// export { useContent } from './hooks/useContent';
// export { useHands } from './hooks/useHands';
// export { useWatchProgress } from './hooks/useWatchProgress';

// ============================================================================
// Stores
// ============================================================================
// export { useContentStore } from './stores/contentStore';

// ============================================================================
// Types
// ============================================================================
export type {
  Content,
  ContentDetail,
  ContentPreview,
  Hand,
  HandGrade,
  Episode,
  Catalog,
  ContentQuery,
  ContentSortOption,
  ContentListResult,
  WatchProgress,
  WatchProgressUpdate,
  ContentState,
  ContentActions,
  ContentErrorCode,
  ContentError,
  ContentCacheConfig,
} from './types';

export { DEFAULT_CACHE_CONFIG } from './types';
