/**
 * Content Hooks
 *
 * 콘텐츠 관련 유틸리티 훅
 * @see ../AGENT_RULES.md
 */

import { contentStore } from '../stores/contentStore';
import * as contentApi from '../api/contentApi';
import type { ContentQuery, Hand, HandGrade, WatchProgress, WatchProgressUpdate } from '../types';

// ============================================================================
// useContent Hook
// ============================================================================

/**
 * 콘텐츠 목록 및 상세 접근 훅
 *
 * @example
 * const { contents, fetchContents, selectedContent } = useContent();
 */
export function useContent() {
  return {
    // State
    get contents() {
      return contentStore.contents;
    },
    get selectedContent() {
      return contentStore.selectedContent;
    },
    get catalogs() {
      return contentStore.catalogs;
    },
    get isLoading() {
      return contentStore.isLoading;
    },
    get isDetailLoading() {
      return contentStore.isDetailLoading;
    },
    get error() {
      return contentStore.error;
    },
    get hasMore() {
      return contentStore.hasMore;
    },

    // Actions
    fetchContents: contentStore.fetchContents,
    fetchContentDetail: contentStore.fetchContentDetail,
    fetchCatalogs: contentStore.fetchCatalogs,
    loadMore: contentStore.loadMore,
    clearSelection: contentStore.clearSelection
  };
}

// ============================================================================
// useHands Hook
// ============================================================================

/**
 * 핸드 데이터 접근 훅
 *
 * @example
 * const { hands, fetchHands, filterByGrade } = useHands();
 */
export function useHands() {
  let gradeFilter = $state<HandGrade[]>([]);

  function setGradeFilter(grades: HandGrade[]) {
    gradeFilter = grades;
  }

  function filterByGrade(hands: Hand[], grades: HandGrade[]): Hand[] {
    if (grades.length === 0) return hands;
    return hands.filter((hand) => grades.includes(hand.grade));
  }

  return {
    get hands() {
      return contentStore.hands;
    },
    get gradeFilter() {
      return gradeFilter;
    },
    get filteredHands() {
      return filterByGrade(contentStore.hands, gradeFilter);
    },

    fetchHands: contentStore.fetchHands,
    setGradeFilter,
    filterByGrade
  };
}

// ============================================================================
// useWatchProgress Hook
// ============================================================================

/**
 * 시청 진행률 관리 훅
 *
 * @example
 * const { progress, saveProgress, resumePosition } = useWatchProgress(contentId);
 */
export function useWatchProgress(contentId: number) {
  let progress = $state<WatchProgress | null>(null);
  let isSaving = $state(false);

  // 진행률 조회
  async function loadProgress() {
    progress = await contentApi.fetchWatchProgress(contentId);
  }

  // 진행률 저장 (디바운싱 적용)
  let saveTimeout: ReturnType<typeof setTimeout> | null = null;

  async function saveProgress(update: Omit<WatchProgressUpdate, 'contentId'>) {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    saveTimeout = setTimeout(async () => {
      isSaving = true;
      try {
        progress = await contentApi.saveWatchProgress({
          contentId,
          ...update
        });
      } finally {
        isSaving = false;
      }
    }, 5000); // 5초 디바운스
  }

  // 즉시 저장 (페이지 이탈 시)
  async function saveProgressImmediately(update: Omit<WatchProgressUpdate, 'contentId'>) {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    try {
      await contentApi.saveWatchProgress({
        contentId,
        ...update
      });
    } catch {
      // 실패해도 무시
    }
  }

  return {
    get progress() {
      return progress;
    },
    get isSaving() {
      return isSaving;
    },
    get resumePosition() {
      return progress?.progressSec || 0;
    },
    get isCompleted() {
      return progress?.completed || false;
    },

    loadProgress,
    saveProgress,
    saveProgressImmediately
  };
}

// ============================================================================
// Content Helpers
// ============================================================================

/**
 * 콘텐츠 정렬 헬퍼
 */
export function sortContents(contents: import('../types').Content[], sort: ContentQuery['sort']) {
  const sorted = [...contents];

  switch (sort) {
    case 'recent':
      return sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    case 'episode':
      return sorted.sort((a, b) => (a.episode || 0) - (b.episode || 0));
    case 'popular':
      return sorted; // 서버에서 정렬됨
    case 'hands':
      return sorted.sort((a, b) => b.handCount - a.handCount);
    default:
      return sorted;
  }
}

/**
 * 핸드 등급 라벨
 */
export function getGradeLabel(grade: HandGrade): string {
  const labels: Record<HandGrade, string> = {
    S: '레전드',
    A: '하이라이트',
    B: '일반',
    C: '기본'
  };
  return labels[grade];
}

/**
 * 핸드 등급 색상
 */
export function getGradeColor(grade: HandGrade): string {
  const colors: Record<HandGrade, string> = {
    S: '#f59e0b', // 골드
    A: '#3b82f6', // 블루
    B: '#22c55e', // 그린
    C: '#64748b'  // 그레이
  };
  return colors[grade];
}
