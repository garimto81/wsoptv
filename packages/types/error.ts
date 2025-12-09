/**
 * Block Agent System - Error Type Definitions
 *
 * 블럭 에이전트 시스템의 에러 타입 및 복구 전략 정의
 *
 * @version 1.0.0
 * @see docs/architecture/0001-block-agent-system.md
 */

// ============================================================================
// Error Severity & Codes
// ============================================================================

/**
 * 에러 심각도
 */
export type ErrorSeverity = 'critical' | 'error' | 'warning';

/**
 * 블럭 에러 코드
 */
export type BlockErrorCode =
  | 'BLOCK_TIMEOUT'           // 블럭 실행 타임아웃
  | 'BLOCK_UNAVAILABLE'       // 블럭 사용 불가
  | 'BLOCK_VALIDATION_FAILED'; // 입력 검증 실패

/**
 * 에이전트 에러 코드
 */
export type AgentErrorCode =
  | 'AGENT_OVERLOADED'           // 에이전트 과부하
  | 'AGENT_COMMUNICATION_FAILED'; // 에이전트 통신 실패

/**
 * 도메인 에러 코드 - Auth
 */
export type AuthErrorCode =
  | 'AUTH_INVALID_CREDENTIALS'  // 인증 정보 불일치
  | 'AUTH_TOKEN_EXPIRED'        // 토큰 만료
  | 'AUTH_PENDING_APPROVAL'     // 승인 대기 중
  | 'AUTH_REJECTED'             // 가입 거절
  | 'AUTH_USERNAME_EXISTS'      // 아이디 중복
  | 'AUTH_RATE_LIMITED';        // 요청 제한 초과

/**
 * 도메인 에러 코드 - Content
 */
export type ContentErrorCode =
  | 'CONTENT_NOT_FOUND'       // 콘텐츠 없음
  | 'CONTENT_ACCESS_DENIED'   // 접근 권한 없음
  | 'CONTENT_LOAD_ERROR';     // 로드 실패

/**
 * 도메인 에러 코드 - Stream
 */
export type StreamErrorCode =
  | 'STREAM_SOURCE_ERROR'       // NAS 접근 실패
  | 'STREAM_NOT_READY'          // 트랜스코딩 중
  | 'STREAM_TRANSCODE_FAILED'   // 트랜스코딩 실패
  | 'STREAM_ACCESS_DENIED'      // 스트림 권한 없음
  | 'STREAM_NOT_FOUND';         // 파일 없음

/**
 * 도메인 에러 코드 - Search
 */
export type SearchErrorCode =
  | 'SEARCH_INDEX_ERROR'      // MeiliSearch 오류
  | 'SEARCH_QUERY_INVALID'    // 잘못된 검색어
  | 'SEARCH_TIMEOUT';         // 검색 타임아웃

/**
 * 모든 에러 코드
 */
export type ErrorCode =
  | BlockErrorCode
  | AgentErrorCode
  | AuthErrorCode
  | ContentErrorCode
  | StreamErrorCode
  | SearchErrorCode;

// ============================================================================
// Fallback Strategy
// ============================================================================

/**
 * 복구 전략
 */
export type FallbackStrategy =
  | 'retry'            // 재시도
  | 'fallback_cache'   // 캐시된 값 사용
  | 'fallback_default' // 기본값 반환
  | 'circuit_break'    // 회로 차단
  | 'escalate';        // 상위 에이전트로 위임

// ============================================================================
// Block Error
// ============================================================================

/**
 * 블럭 에러
 *
 * @example
 * const error: BlockError = {
 *   code: 'STREAM_NOT_READY',
 *   severity: 'warning',
 *   blockId: 'stream.transcode',
 *   message: '트랜스코딩 진행 중입니다',
 *   recoverable: true,
 *   retryAfter: 5000,
 *   fallbackStrategy: 'retry'
 * };
 */
export interface BlockError {
  /** 에러 코드 */
  code: ErrorCode;
  /** 심각도 */
  severity: ErrorSeverity;
  /** 발생 블럭 ID */
  blockId: string;
  /** 에러 메시지 */
  message: string;
  /** 원인 (옵션) */
  cause?: unknown;
  /** 복구 가능 여부 */
  recoverable: boolean;
  /** 재시도 대기 시간 (ms) */
  retryAfter?: number;
  /** 폴백 전략 */
  fallbackStrategy?: FallbackStrategy;
}

// ============================================================================
// Error Recovery Matrix
// ============================================================================

/**
 * 에러 복구 설정
 */
export interface ErrorRecoveryConfig {
  code: ErrorCode;
  severity: ErrorSeverity;
  recoverable: boolean;
  strategy: FallbackStrategy;
  httpStatus?: number;
  retryConfig?: {
    maxAttempts: number;
    backoffMs: number;
    multiplier: number;
  };
}

/**
 * 에러 복구 매트릭스
 * 각 에러 코드별 복구 전략 정의
 */
export const ERROR_RECOVERY_MATRIX: ErrorRecoveryConfig[] = [
  // Block Errors
  { code: 'BLOCK_TIMEOUT', severity: 'error', recoverable: true, strategy: 'retry', retryConfig: { maxAttempts: 3, backoffMs: 1000, multiplier: 2 } },
  { code: 'BLOCK_UNAVAILABLE', severity: 'critical', recoverable: false, strategy: 'circuit_break' },
  { code: 'BLOCK_VALIDATION_FAILED', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 400 },

  // Auth Errors
  { code: 'AUTH_INVALID_CREDENTIALS', severity: 'error', recoverable: false, strategy: 'fallback_default', httpStatus: 401 },
  { code: 'AUTH_TOKEN_EXPIRED', severity: 'warning', recoverable: true, strategy: 'retry', httpStatus: 401 },
  { code: 'AUTH_PENDING_APPROVAL', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 403 },
  { code: 'AUTH_REJECTED', severity: 'error', recoverable: false, strategy: 'fallback_default', httpStatus: 403 },
  { code: 'AUTH_USERNAME_EXISTS', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 409 },
  { code: 'AUTH_RATE_LIMITED', severity: 'warning', recoverable: true, strategy: 'retry', httpStatus: 429 },

  // Content Errors
  { code: 'CONTENT_NOT_FOUND', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 404 },
  { code: 'CONTENT_ACCESS_DENIED', severity: 'error', recoverable: false, strategy: 'fallback_default', httpStatus: 403 },
  { code: 'CONTENT_LOAD_ERROR', severity: 'error', recoverable: true, strategy: 'retry' },

  // Stream Errors
  { code: 'STREAM_SOURCE_ERROR', severity: 'error', recoverable: true, strategy: 'retry', httpStatus: 500 },
  { code: 'STREAM_NOT_READY', severity: 'warning', recoverable: true, strategy: 'retry', httpStatus: 503, retryConfig: { maxAttempts: 3, backoffMs: 5000, multiplier: 1 } },
  { code: 'STREAM_TRANSCODE_FAILED', severity: 'error', recoverable: true, strategy: 'retry', httpStatus: 500 },
  { code: 'STREAM_ACCESS_DENIED', severity: 'error', recoverable: false, strategy: 'fallback_default', httpStatus: 403 },
  { code: 'STREAM_NOT_FOUND', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 404 },

  // Search Errors
  { code: 'SEARCH_INDEX_ERROR', severity: 'error', recoverable: true, strategy: 'fallback_cache', httpStatus: 500 },
  { code: 'SEARCH_QUERY_INVALID', severity: 'warning', recoverable: false, strategy: 'fallback_default', httpStatus: 400 },
  { code: 'SEARCH_TIMEOUT', severity: 'error', recoverable: true, strategy: 'retry', httpStatus: 504 },
];

// ============================================================================
// Circuit Breaker Types
// ============================================================================

/**
 * 회로 차단기 상태
 */
export type CircuitState = 'closed' | 'open' | 'half-open';

/**
 * 회로 차단기 설정
 */
export interface CircuitBreakerConfig {
  /** 실패 임계값 (기본: 5) */
  failureThreshold: number;
  /** 복구 임계값 (기본: 3) */
  successThreshold: number;
  /** 반열림 대기 시간 (기본: 30000ms) */
  timeout: number;
}

/**
 * 회로 차단기 상태 정보
 */
export interface CircuitBreakerStatus {
  /** 블럭 ID */
  blockId: string;
  /** 현재 상태 */
  state: CircuitState;
  /** 연속 실패 횟수 */
  failures: number;
  /** 연속 성공 횟수 (half-open 상태) */
  successes: number;
  /** 마지막 실패 시간 */
  lastFailure?: number;
  /** 다음 재시도 가능 시간 */
  nextRetryAt?: number;
}
