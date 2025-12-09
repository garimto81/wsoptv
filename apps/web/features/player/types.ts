/**
 * Player Feature Types
 *
 * 비디오 플레이어 블럭의 타입 정의
 * @see AGENT_RULES.md
 */

// ============================================================================
// Player State
// ============================================================================

export interface PlayerState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  buffered: number;
  volume: number;
  isMuted: boolean;
  quality: QualityLevel;
  isFullscreen: boolean;
  isLoading: boolean;
  error: PlayerError | null;
}

export interface PlayerActions {
  play: () => void;
  pause: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  setQuality: (quality: QualityLevel) => void;
  toggleFullscreen: () => void;
  skipToNextHand: () => void;
  skipToPrevHand: () => void;
}

// ============================================================================
// Quality
// ============================================================================

export type QualityLevel = 'auto' | '1080p' | '720p' | '480p' | '360p';

export interface QualityOption {
  level: QualityLevel;
  label: string;
  bitrate: number;
  available: boolean;
}

// ============================================================================
// Timeline
// ============================================================================

export type SegmentType = 'hand' | 'shuffle' | 'break' | 'intro' | 'outro';

export interface TimelineSegment {
  type: SegmentType;
  startSec: number;
  endSec: number;
  hand?: HandInfo;
}

export interface HandInfo {
  id: number;
  handNumber: number;
  grade: HandGrade;
  players: string[];
  potSize?: number;
}

export type HandGrade = 'S' | 'A' | 'B' | 'C';

export interface TimelineState {
  segments: TimelineSegment[];
  currentSegment: TimelineSegment | null;
  currentHand: HandInfo | null;
  totalHands: number;
  highlightHands: TimelineSegment[];
}

// ============================================================================
// Player Events
// ============================================================================

export type PlayerEventType =
  | 'handenter'       // 핸드 구간 진입
  | 'handleave'       // 핸드 구간 이탈
  | 'nonhandsegment'  // 비핸드 구간 진입
  | 'skiptohand'      // 다음 핸드로 스킵
  | 'highlightsonly'  // 하이라이트만 보기
  | 'qualitychange'   // 품질 변경
  | 'error';          // 에러 발생

export interface PlayerEvent {
  type: PlayerEventType;
  timestamp: number;
  data?: unknown;
}

// ============================================================================
// Player Errors
// ============================================================================

export type PlayerErrorCode =
  | 'PLAYER_SOURCE_ERROR'
  | 'PLAYER_NETWORK_ERROR'
  | 'PLAYER_DECODE_ERROR'
  | 'PLAYER_TIMEOUT';

export interface PlayerError {
  code: PlayerErrorCode;
  message: string;
  recoverable: boolean;
}

// ============================================================================
// HLS Configuration
// ============================================================================

export interface HLSConfig {
  maxBufferLength: number;
  maxMaxBufferLength: number;
  startLevel: number;
  capLevelToPlayerSize: boolean;
  progressive: boolean;
}

export const DEFAULT_HLS_CONFIG: HLSConfig = {
  maxBufferLength: 30,
  maxMaxBufferLength: 60,
  startLevel: -1,  // auto
  capLevelToPlayerSize: true,
  progressive: true,
};
