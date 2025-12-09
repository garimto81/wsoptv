/**
 * Player API Functions
 *
 * 플레이어 관련 백엔드 API 호출 함수
 * @see ../AGENT_RULES.md
 */

import { getAccessToken } from '$features/auth';
import type {
  TimelineSegment,
  QualityOption,
  PlayerError,
  PlayerErrorCode
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE = '/api/v1';

// ============================================================================
// API Error Handling
// ============================================================================

class PlayerApiError extends Error {
  code: PlayerErrorCode;
  status: number;

  constructor(code: PlayerErrorCode, message: string, status: number = 400) {
    super(message);
    this.name = 'PlayerApiError';
    this.code = code;
    this.status = status;
  }

  toPlayerError(): PlayerError {
    return { code: this.code, message: this.message, recoverable: this.status < 500 };
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const code = mapStatusToErrorCode(response.status);
    throw new PlayerApiError(code, error.message || '재생 중 오류가 발생했습니다', response.status);
  }
  return response.json();
}

function mapStatusToErrorCode(status: number): PlayerErrorCode {
  switch (status) {
    case 404:
      return 'PLAYER_SOURCE_ERROR';
    case 408:
    case 504:
      return 'PLAYER_TIMEOUT';
    default:
      return 'PLAYER_NETWORK_ERROR';
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
// Stream API
// ============================================================================

/**
 * HLS 스트림 URL 획득
 */
export async function getStreamUrl(contentId: number): Promise<string> {
  const response = await fetch(`${API_BASE}/stream/${contentId}`, {
    headers: getAuthHeaders()
  });

  const result = await handleResponse<{ url: string }>(response);
  return result.url;
}

/**
 * 사용 가능한 품질 옵션 조회
 */
export async function getQualityOptions(contentId: number): Promise<QualityOption[]> {
  const response = await fetch(`${API_BASE}/stream/${contentId}/qualities`, {
    headers: getAuthHeaders()
  });

  return handleResponse<QualityOption[]>(response);
}

/**
 * 콘텐츠의 타임라인 세그먼트 조회
 */
export async function getTimelineSegments(contentId: number): Promise<TimelineSegment[]> {
  const response = await fetch(`${API_BASE}/contents/${contentId}/timeline`, {
    headers: getAuthHeaders()
  });

  return handleResponse<TimelineSegment[]>(response);
}

// ============================================================================
// Player Event Tracking
// ============================================================================

interface PlayerEventData {
  contentId: number;
  event: string;
  position?: number;
  quality?: string;
  error?: string;
}

/**
 * 플레이어 이벤트 전송 (분석용)
 */
export async function trackPlayerEvent(data: PlayerEventData): Promise<void> {
  const token = getAccessToken();
  if (!token) return; // 비로그인 사용자는 추적 안함

  try {
    await fetch(`${API_BASE}/analytics/player`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        ...data,
        timestamp: Date.now()
      })
    });
  } catch {
    // 실패해도 무시
  }
}

// ============================================================================
// HLS Helper
// ============================================================================

/**
 * HLS 지원 여부 확인
 */
export function isHlsSupported(): boolean {
  if (typeof window === 'undefined') return false;

  const video = document.createElement('video');

  // Native HLS support (Safari)
  if (video.canPlayType('application/vnd.apple.mpegurl')) {
    return true;
  }

  // hls.js support check
  return !!window.MediaSource;
}

/**
 * 적정 시작 품질 결정
 */
export function getInitialQuality(
  connectionType?: string,
  saveData?: boolean
): 'auto' | '480p' | '720p' | '1080p' {
  // 데이터 절약 모드
  if (saveData) {
    return '480p';
  }

  // 연결 타입에 따른 기본 품질
  switch (connectionType) {
    case '4g':
    case 'wifi':
      return 'auto';
    case '3g':
      return '480p';
    case '2g':
    case 'slow-2g':
      return '480p';
    default:
      return 'auto';
  }
}

/**
 * 네트워크 상태 확인
 */
export function getNetworkInfo(): { type?: string; saveData?: boolean } {
  if (typeof window === 'undefined' || !('connection' in navigator)) {
    return {};
  }

  const connection = (navigator as { connection?: { effectiveType?: string; saveData?: boolean } }).connection;
  return {
    type: connection?.effectiveType,
    saveData: connection?.saveData
  };
}
