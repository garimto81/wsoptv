/**
 * Content Feature - Public API
 *
 * 콘텐츠 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { ContentCard, useContent } from '$features/content';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
export { ContentCard, ContentList, HandList } from './components';

// ============================================================================
// Hooks
// ============================================================================
export {
  useContent,
  useHands,
  useWatchProgress,
  sortContents,
  getGradeLabel,
  getGradeColor
} from './hooks/useContent';

// ============================================================================
// Stores
// ============================================================================
export { useContentStore, contentStore } from './stores/contentStore';

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
