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
// export { VideoPlayer } from './components/VideoPlayer';
// export { PlayerControls } from './components/PlayerControls';
// export { Timeline } from './components/Timeline';
// export { HandOverlay } from './components/HandOverlay';
// export { SkipButtons } from './components/SkipButtons';

// ============================================================================
// Hooks
// ============================================================================
// export { usePlayer } from './hooks/usePlayer';
// export { useTimeline } from './hooks/useTimeline';
// export { useHandNavigation } from './hooks/useHandNavigation';

// ============================================================================
// Stores
// ============================================================================
// export { usePlayerStore } from './stores/playerStore';

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
