/**
 * Player Hooks
 *
 * 플레이어 관련 유틸리티 훅
 * @see ../AGENT_RULES.md
 */

import { playerStore } from '../stores/playerStore';
import * as playerApi from '../api/playerApi';
import type { QualityLevel, TimelineSegment, HandGrade, PlayerEvent, PlayerEventType } from '../types';

// ============================================================================
// usePlayer Hook
// ============================================================================

/**
 * 플레이어 상태 및 컨트롤 훅
 *
 * @example
 * const { isPlaying, play, pause, seek } = usePlayer();
 */
export function usePlayer() {
  return {
    // State
    get isPlaying() {
      return playerStore.isPlaying;
    },
    get isPaused() {
      return playerStore.isPaused;
    },
    get currentTime() {
      return playerStore.currentTime;
    },
    get duration() {
      return playerStore.duration;
    },
    get buffered() {
      return playerStore.buffered;
    },
    get volume() {
      return playerStore.volume;
    },
    get isMuted() {
      return playerStore.isMuted;
    },
    get quality() {
      return playerStore.quality;
    },
    get isFullscreen() {
      return playerStore.isFullscreen;
    },
    get isLoading() {
      return playerStore.isLoading;
    },
    get error() {
      return playerStore.error;
    },

    // Progress
    get progress() {
      const d = playerStore.duration;
      return d > 0 ? (playerStore.currentTime / d) * 100 : 0;
    },
    get bufferedProgress() {
      const d = playerStore.duration;
      return d > 0 ? (playerStore.buffered / d) * 100 : 0;
    },

    // Actions
    play: playerStore.play,
    pause: playerStore.pause,
    seek: playerStore.seek,
    setVolume: playerStore.setVolume,
    toggleMute: playerStore.toggleMute,
    setQuality: playerStore.setQuality,
    toggleFullscreen: playerStore.toggleFullscreen,
    clearError: playerStore.clearError,
    reset: playerStore.reset
  };
}

// ============================================================================
// useTimeline Hook
// ============================================================================

/**
 * 타임라인 관리 훅
 *
 * @example
 * const { segments, currentHand, skipToNextHand } = useTimeline();
 */
export function useTimeline() {
  return {
    get segments() {
      return playerStore.segments;
    },
    get currentSegment() {
      return playerStore.currentSegment;
    },
    get currentHand() {
      return playerStore.currentHand;
    },
    get handSegments() {
      return playerStore.getHandSegments();
    },
    get totalHands() {
      return playerStore.getHandSegments().length;
    },

    setSegments: playerStore.setSegments,
    findNextHand: playerStore.findNextHand,
    findPrevHand: playerStore.findPrevHand
  };
}

// ============================================================================
// useHandNavigation Hook
// ============================================================================

/**
 * 핸드 네비게이션 훅
 *
 * @example
 * const { skipToNextHand, skipToPrevHand, canSkipNext } = useHandNavigation();
 */
export function useHandNavigation() {
  const hasNextHand = $derived(
    playerStore.findNextHand(playerStore.currentTime) !== null
  );
  const hasPrevHand = $derived(
    playerStore.findPrevHand(playerStore.currentTime) !== null
  );

  return {
    get hasNextHand() {
      return hasNextHand;
    },
    get hasPrevHand() {
      return hasPrevHand;
    },
    get currentHand() {
      return playerStore.currentHand;
    },

    skipToNextHand: playerStore.skipToNextHand,
    skipToPrevHand: playerStore.skipToPrevHand,

    /**
     * 특정 핸드로 이동
     */
    goToHand(segment: TimelineSegment) {
      if (segment.type === 'hand') {
        playerStore.seek(segment.startSec);
      }
    },

    /**
     * 하이라이트 핸드만 보기 (S, A 등급)
     */
    filterHighlightHands(segments: TimelineSegment[]): TimelineSegment[] {
      return segments.filter(
        (s) => s.type === 'hand' && s.hand && ['S', 'A'].includes(s.hand.grade)
      );
    }
  };
}

// ============================================================================
// usePlayerEvents Hook
// ============================================================================

/**
 * 플레이어 이벤트 관리 훅
 */
export function usePlayerEvents(contentId: number) {
  const listeners = new Map<PlayerEventType, ((data: unknown) => void)[]>();

  function emit(type: PlayerEventType, data?: unknown) {
    const event: PlayerEvent = {
      type,
      timestamp: Date.now(),
      data
    };

    // 리스너 호출
    const typeListeners = listeners.get(type);
    if (typeListeners) {
      typeListeners.forEach((fn) => fn(data));
    }

    // 분석 이벤트 전송
    playerApi.trackPlayerEvent({
      contentId,
      event: type,
      position: playerStore.currentTime,
      quality: playerStore.quality,
      error: data instanceof Error ? data.message : undefined
    });
  }

  function on(type: PlayerEventType, callback: (data: unknown) => void) {
    const existing = listeners.get(type) || [];
    listeners.set(type, [...existing, callback]);

    return () => {
      const updated = listeners.get(type)?.filter((fn) => fn !== callback) || [];
      listeners.set(type, updated);
    };
  }

  return {
    emit,
    on,

    // 편의 메서드
    onHandEnter(callback: (hand: unknown) => void) {
      return on('handenter', callback);
    },
    onHandLeave(callback: () => void) {
      return on('handleave', callback);
    },
    onError(callback: (error: unknown) => void) {
      return on('error', callback);
    }
  };
}

// ============================================================================
// Player Helpers
// ============================================================================

/**
 * 품질 레벨 라벨
 */
export function getQualityLabel(quality: QualityLevel): string {
  const labels: Record<QualityLevel, string> = {
    auto: '자동',
    '1080p': '1080p HD',
    '720p': '720p HD',
    '480p': '480p',
    '360p': '360p'
  };
  return labels[quality];
}

/**
 * 세그먼트 타입 색상
 */
export function getSegmentColor(type: TimelineSegment['type'], grade?: HandGrade): string {
  if (type === 'hand' && grade) {
    const gradeColors: Record<HandGrade, string> = {
      S: '#f59e0b',
      A: '#3b82f6',
      B: '#22c55e',
      C: '#64748b'
    };
    return gradeColors[grade];
  }

  const typeColors: Record<TimelineSegment['type'], string> = {
    hand: '#3b82f6',
    shuffle: '#94a3b8',
    break: '#e2e8f0',
    intro: '#a855f7',
    outro: '#a855f7'
  };
  return typeColors[type];
}

/**
 * 시간을 타임라인 위치(%)로 변환
 */
export function timeToPosition(time: number, duration: number): number {
  if (duration <= 0) return 0;
  return (time / duration) * 100;
}

/**
 * 타임라인 위치(%)를 시간으로 변환
 */
export function positionToTime(position: number, duration: number): number {
  return (position / 100) * duration;
}
