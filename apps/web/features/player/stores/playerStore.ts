/**
 * Player Store
 *
 * Svelte 5 runes 기반 플레이어 상태 관리
 * @see ../AGENT_RULES.md
 */

import type {
  PlayerState,
  QualityLevel,
  TimelineSegment,
  HandInfo,
  TimelineState,
  PlayerError
} from '../types';
import { DEFAULT_HLS_CONFIG } from '../types';

// ============================================================================
// Player State (Svelte 5 Runes)
// ============================================================================

let isPlaying = $state(false);
let isPaused = $state(true);
let currentTime = $state(0);
let duration = $state(0);
let buffered = $state(0);
let volume = $state(1);
let isMuted = $state(false);
let quality = $state<QualityLevel>('auto');
let isFullscreen = $state(false);
let isLoading = $state(false);
let error = $state<PlayerError | null>(null);

// Timeline State
let segments = $state<TimelineSegment[]>([]);
let currentSegment = $state<TimelineSegment | null>(null);
let currentHand = $state<HandInfo | null>(null);

// ============================================================================
// Derived State
// ============================================================================

const playerState = $derived<PlayerState>({
  isPlaying,
  isPaused,
  currentTime,
  duration,
  buffered,
  volume,
  isMuted,
  quality,
  isFullscreen,
  isLoading,
  error
});

const timelineState = $derived<TimelineState>({
  segments,
  currentSegment,
  currentHand,
  totalHands: segments.filter((s) => s.type === 'hand').length,
  highlightHands: segments.filter((s) => s.type === 'hand' && s.hand && ['S', 'A'].includes(s.hand.grade))
});

// ============================================================================
// Player Actions
// ============================================================================

function play(): void {
  isPlaying = true;
  isPaused = false;
}

function pause(): void {
  isPlaying = false;
  isPaused = true;
}

function seek(time: number): void {
  currentTime = Math.max(0, Math.min(time, duration));
}

function setCurrentTime(time: number): void {
  currentTime = time;
  updateCurrentSegment(time);
}

function setDuration(d: number): void {
  duration = d;
}

function setBuffered(b: number): void {
  buffered = b;
}

function setVolume(v: number): void {
  volume = Math.max(0, Math.min(1, v));
  if (volume > 0) {
    isMuted = false;
  }
}

function toggleMute(): void {
  isMuted = !isMuted;
}

function setQuality(q: QualityLevel): void {
  quality = q;
}

function toggleFullscreen(): void {
  isFullscreen = !isFullscreen;
}

function setLoading(loading: boolean): void {
  isLoading = loading;
}

function setError(err: PlayerError | null): void {
  error = err;
}

function clearError(): void {
  error = null;
}

// ============================================================================
// Timeline Actions
// ============================================================================

function setSegments(newSegments: TimelineSegment[]): void {
  segments = newSegments;
}

function updateCurrentSegment(time: number): void {
  const segment = segments.find((s) => time >= s.startSec && time < s.endSec);

  if (segment) {
    currentSegment = segment;
    currentHand = segment.type === 'hand' ? segment.hand || null : null;
  } else {
    currentSegment = null;
    currentHand = null;
  }
}

function getHandSegments(): TimelineSegment[] {
  return segments.filter((s) => s.type === 'hand');
}

function findNextHand(fromTime: number): TimelineSegment | null {
  const handSegments = getHandSegments();
  return handSegments.find((s) => s.startSec > fromTime) || null;
}

function findPrevHand(fromTime: number): TimelineSegment | null {
  const handSegments = getHandSegments();
  const currentIndex = handSegments.findIndex(
    (s) => fromTime >= s.startSec && fromTime < s.endSec
  );

  if (currentIndex > 0) {
    return handSegments[currentIndex - 1];
  }

  // 현재 핸드가 없으면 이전 핸드 찾기
  const prevHands = handSegments.filter((s) => s.endSec <= fromTime);
  return prevHands.length > 0 ? prevHands[prevHands.length - 1] : null;
}

function skipToNextHand(): void {
  const nextHand = findNextHand(currentTime);
  if (nextHand) {
    seek(nextHand.startSec);
  }
}

function skipToPrevHand(): void {
  const prevHand = findPrevHand(currentTime);
  if (prevHand) {
    seek(prevHand.startSec);
  }
}

// ============================================================================
// Reset
// ============================================================================

function reset(): void {
  isPlaying = false;
  isPaused = true;
  currentTime = 0;
  duration = 0;
  buffered = 0;
  quality = 'auto';
  isFullscreen = false;
  isLoading = false;
  error = null;
  segments = [];
  currentSegment = null;
  currentHand = null;
}

// ============================================================================
// Store Export
// ============================================================================

export function usePlayerStore() {
  return {
    // Player State (readonly)
    get playerState() {
      return playerState;
    },
    get timelineState() {
      return timelineState;
    },
    get isPlaying() {
      return isPlaying;
    },
    get isPaused() {
      return isPaused;
    },
    get currentTime() {
      return currentTime;
    },
    get duration() {
      return duration;
    },
    get buffered() {
      return buffered;
    },
    get volume() {
      return volume;
    },
    get isMuted() {
      return isMuted;
    },
    get quality() {
      return quality;
    },
    get isFullscreen() {
      return isFullscreen;
    },
    get isLoading() {
      return isLoading;
    },
    get error() {
      return error;
    },

    // Timeline State (readonly)
    get segments() {
      return segments;
    },
    get currentSegment() {
      return currentSegment;
    },
    get currentHand() {
      return currentHand;
    },

    // Player Actions
    play,
    pause,
    seek,
    setCurrentTime,
    setDuration,
    setBuffered,
    setVolume,
    toggleMute,
    setQuality,
    toggleFullscreen,
    setLoading,
    setError,
    clearError,

    // Timeline Actions
    setSegments,
    updateCurrentSegment,
    getHandSegments,
    findNextHand,
    findPrevHand,
    skipToNextHand,
    skipToPrevHand,

    // Reset
    reset,

    // Config
    hlsConfig: DEFAULT_HLS_CONFIG
  };
}

export const playerStore = usePlayerStore();
