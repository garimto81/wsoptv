/**
 * Block Agent System - Message Type Definitions
 *
 * 에이전트 간 통신을 위한 메시지 타입 정의
 *
 * @version 1.0.0
 * @see docs/architecture/0001-block-agent-system.md
 */

import type { Priority } from './agent';

// ============================================================================
// Message Types
// ============================================================================

/**
 * 메시지 유형
 */
export type MessageType =
  | 'task.request'    // 태스크 요청
  | 'task.response'   // 태스크 응답
  | 'task.error'      // 태스크 에러
  | 'status.update'   // 상태 업데이트
  | 'health.ping'     // 헬스 체크 요청
  | 'health.pong';    // 헬스 체크 응답

// ============================================================================
// Agent Message
// ============================================================================

/**
 * 에이전트 메시지
 *
 * 에이전트 간 통신의 기본 단위
 * UUID v7을 사용하여 시간 정렬 가능
 *
 * @example
 * const message: AgentMessage = {
 *   id: '01912345-6789-7abc-def0-123456789abc',
 *   timestamp: Date.now(),
 *   source: 'orchestrator',
 *   target: 'auth-domain',
 *   type: 'task.request',
 *   payload: { type: 'login', credentials: { ... } },
 *   correlationId: 'corr-123',
 *   traceId: 'trace-456',
 *   spanId: 'span-789',
 *   priority: 'normal',
 *   ttl: 30000
 * };
 */
export interface AgentMessage {
  /** 메시지 ID (UUID v7) */
  id: string;
  /** 생성 시간 (Unix ms) */
  timestamp: number;
  /** 발신 에이전트 ID */
  source: string;
  /** 수신 에이전트 ID 또는 'broadcast' */
  target: string;
  /** 메시지 유형 */
  type: MessageType;
  /** 메시지 페이로드 */
  payload: unknown;

  // 추적 정보
  /** 요청-응답 연결 ID */
  correlationId: string;
  /** 분산 추적 ID */
  traceId: string;
  /** Span ID */
  spanId: string;

  // 메타데이터
  /** 우선순위 */
  priority: Priority;
  /** Time to live (ms) */
  ttl: number;
}

// ============================================================================
// Agent Events
// ============================================================================

/**
 * 블럭 이벤트 유형
 */
export type BlockEventType =
  | 'block.started'     // 블럭 실행 시작
  | 'block.completed'   // 블럭 실행 완료
  | 'block.error'       // 블럭 에러 발생
  | 'block.timeout';    // 블럭 타임아웃

/**
 * 에이전트 이벤트 유형
 */
export type AgentEventType =
  | 'agent.started'     // 에이전트 시작
  | 'agent.stopped'     // 에이전트 중지
  | 'agent.error'       // 에이전트 에러
  | 'agent.recovered';  // 에이전트 복구

/**
 * 이벤트 기본 인터페이스
 */
export interface AgentEvent {
  /** 이벤트 유형 */
  type: BlockEventType | AgentEventType;
  /** 발생 소스 (에이전트 또는 블럭 ID) */
  source: string;
  /** 이벤트 데이터 */
  payload: unknown;
  /** 발생 시간 */
  timestamp: number;
}

/**
 * 블럭 시작 이벤트
 */
export interface BlockStartedEvent extends AgentEvent {
  type: 'block.started';
  payload: {
    blockId: string;
    taskId: string;
  };
}

/**
 * 블럭 완료 이벤트
 */
export interface BlockCompletedEvent extends AgentEvent {
  type: 'block.completed';
  payload: {
    blockId: string;
    taskId: string;
    result: unknown;
    durationMs: number;
  };
}

/**
 * 블럭 에러 이벤트
 */
export interface BlockErrorEvent extends AgentEvent {
  type: 'block.error';
  payload: {
    blockId: string;
    taskId: string;
    error: {
      code: string;
      message: string;
      cause?: unknown;
    };
  };
}

// ============================================================================
// Event Bus Types
// ============================================================================

/**
 * 이벤트 핸들러
 */
export type EventHandler = (event: AgentEvent) => void | Promise<void>;

/**
 * 구독 객체
 */
export interface Subscription {
  /** 구독 해제 */
  unsubscribe(): void;
}

/**
 * 이벤트 버스 인터페이스
 */
export interface EventBus {
  /**
   * 이벤트 발행
   * @param event 발행할 이벤트
   */
  publish(event: AgentEvent): Promise<void>;

  /**
   * 이벤트 구독
   * @param pattern 구독 패턴 (예: 'auth.*', 'block.completed')
   * @param handler 이벤트 핸들러
   * @returns 구독 객체
   */
  subscribe(pattern: string, handler: EventHandler): Subscription;

  /**
   * 요청-응답 패턴
   * @param target 대상 에이전트 ID
   * @param message 요청 메시지
   * @param timeout 타임아웃 (ms)
   * @returns 응답 메시지
   */
  request(target: string, message: AgentMessage, timeout: number): Promise<AgentMessage>;
}
