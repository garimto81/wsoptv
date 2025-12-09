/**
 * Player Feature - Public API
 *
 * 비디오 플레이어 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { VideoPlayer, usePlayer } from '@/features/player';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
export { VideoPlayer, PlayerControls, Timeline } from './components';

// ============================================================================
// Hooks
// ============================================================================
export {
  usePlayer,
  useTimeline,
  useHandNavigation,
  usePlayerEvents,
  getQualityLabel,
  getSegmentColor,
  timeToPosition,
  positionToTime
} from './hooks/usePlayer';

// ============================================================================
// Stores
// ============================================================================
export { playerStore } from './stores/playerStore';

// ============================================================================
// API
// ============================================================================
export {
  getStreamUrl,
  getQualityOptions,
  getTimelineSegments,
  trackPlayerEvent,
  isHlsSupported
} from './api/playerApi';

// ============================================================================
// Types
// ============================================================================
export type {
  PlayerState,
  PlayerActions,
  QualityLevel,
  QualityOption,
  SegmentType,
  TimelineSegment,
  HandInfo,
  HandGrade,
  TimelineState,
  PlayerEventType,
  PlayerEvent,
  PlayerErrorCode,
  PlayerError,
  HLSConfig,
} from './types';

export { DEFAULT_HLS_CONFIG } from './types';
