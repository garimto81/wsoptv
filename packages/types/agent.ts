/**
 * Block Agent System - Agent Type Definitions
 *
 * 에이전트는 블럭을 관리하고 실행하는 주체입니다.
 * 3계층 구조: Orchestrator → Domain → Block
 *
 * @version 1.0.0
 * @see docs/architecture/0001-block-agent-system.md
 */

import type { DomainType } from './block';

// ============================================================================
// Agent Level & Status
// ============================================================================

/**
 * 에이전트 레벨
 * - orchestrator: 전역 조정자 (Level 0)
 * - domain: 도메인 관리자 (Level 1)
 * - block: 블럭 실행자 (Level 2)
 */
export type AgentLevel = 'orchestrator' | 'domain' | 'block';

/**
 * 에이전트 상태
 */
export type AgentStatus =
  | 'idle'     // 대기 중
  | 'busy'     // 작업 중
  | 'error'    // 에러 발생
  | 'stopped'; // 중지됨

// ============================================================================
// Capability
// ============================================================================

/**
 * 에이전트 능력 정의
 * 에이전트가 수행할 수 있는 작업의 명세
 */
export interface Capability {
  /** 능력 이름 (예: 'login', 'search', 'transcode') */
  name: string;
  /** 설명 */
  description: string;
  /** 입력 스키마 (Zod 스키마 이름) */
  inputSchema: string;
  /** 출력 스키마 (Zod 스키마 이름) */
  outputSchema: string;
}

// ============================================================================
// Task & Result
// ============================================================================

/**
 * 태스크 유형
 */
export type TaskType =
  | 'query'     // 데이터 조회
  | 'mutation'  // 데이터 변경
  | 'stream'    // 스트리밍 작업
  | 'batch'     // 배치 처리
  | 'monitor';  // 상태 감시

/**
 * 우선순위
 */
export type Priority = 'critical' | 'high' | 'normal' | 'low';

/**
 * 재시도 정책
 */
export interface RetryPolicy {
  /** 최대 재시도 횟수 */
  maxAttempts: number;
  /** 초기 대기 시간 (ms) */
  backoffMs: number;
  /** 백오프 배율 */
  backoffMultiplier: number;
}

/**
 * 태스크 정의
 */
export interface Task {
  /** 태스크 ID (UUID) */
  id: string;
  /** 태스크 유형 */
  type: TaskType;
  /** 우선순위 */
  priority: Priority;
  /** 태스크 데이터 */
  payload: unknown;
  /** 타임아웃 (ms) */
  timeout: number;
  /** 재시도 정책 */
  retryPolicy: RetryPolicy;
  /** 메타데이터 */
  metadata?: {
    correlationId?: string;
    traceId?: string;
    spanId?: string;
  };
}

/**
 * 태스크 결과 상태
 */
export type TaskResultStatus = 'success' | 'failure' | 'timeout' | 'cancelled';

/**
 * 태스크 결과
 */
export interface TaskResult {
  /** 태스크 ID */
  taskId: string;
  /** 결과 상태 */
  status: TaskResultStatus;
  /** 결과 데이터 (성공 시) */
  data?: unknown;
  /** 에러 정보 (실패 시) */
  error?: {
    code: string;
    message: string;
    cause?: unknown;
  };
  /** 실행 시간 (ms) */
  durationMs: number;
  /** 재시도 횟수 */
  retryCount: number;
}

// ============================================================================
// Health Check
// ============================================================================

/**
 * 헬스 상태
 */
export type HealthLevel = 'healthy' | 'degraded' | 'unhealthy';

/**
 * 헬스 체크 결과
 */
export interface HealthStatus {
  /** 에이전트 ID */
  agentId: string;
  /** 헬스 상태 */
  level: HealthLevel;
  /** 체크 시간 */
  timestamp: number;
  /** 상세 정보 */
  details?: {
    uptime: number;
    tasksProcessed: number;
    errorRate: number;
    lastError?: string;
  };
}

// ============================================================================
// Agent Interface
// ============================================================================

/**
 * 에이전트 인터페이스
 *
 * @example
 * const authDomainAgent: Agent = {
 *   id: 'auth-domain',
 *   level: 'domain',
 *   status: 'idle',
 *   managedBlocks: ['auth.validate', 'auth.token', 'auth.session'],
 *   childAgents: [],
 *   capabilities: [
 *     { name: 'login', description: '사용자 로그인', ... },
 *     { name: 'logout', description: '로그아웃', ... }
 *   ],
 *   execute: async (task) => { ... },
 *   start: async () => { ... },
 *   stop: async () => { ... },
 *   healthCheck: async () => ({ agentId: 'auth-domain', level: 'healthy', ... })
 * };
 */
export interface Agent {
  /** 에이전트 고유 ID */
  id: string;
  /** 에이전트 레벨 */
  level: AgentLevel;
  /** 현재 상태 */
  status: AgentStatus;
  /** 관리하는 블럭 ID 목록 */
  managedBlocks: string[];
  /** 하위 에이전트 ID 목록 */
  childAgents: string[];
  /** 에이전트 능력 목록 */
  capabilities: Capability[];

  /**
   * 태스크 실행
   * @param task 실행할 태스크
   * @returns 태스크 결과
   */
  execute(task: Task): Promise<TaskResult>;

  /**
   * 에이전트 시작
   */
  start(): Promise<void>;

  /**
   * 에이전트 중지
   */
  stop(): Promise<void>;

  /**
   * 헬스 체크
   * @returns 헬스 상태
   */
  healthCheck(): Promise<HealthStatus>;
}

// ============================================================================
// Domain Agent Definitions
// ============================================================================

/**
 * 도메인 에이전트 정의
 * 각 도메인별 에이전트 구성 정보
 */
export interface DomainAgentConfig {
  id: string;
  domain: DomainType;
  managedBlocks: string[];
  capabilities: Capability[];
  rulesPath: string;  // .claude/agents/{domain}-domain.md
}

/**
 * WSOPTV 도메인 에이전트 설정
 */
export const DOMAIN_AGENT_CONFIGS: DomainAgentConfig[] = [
  {
    id: 'auth-domain',
    domain: 'auth',
    managedBlocks: ['auth.validate', 'auth.token', 'auth.session'],
    capabilities: [
      { name: 'login', description: '사용자 로그인 처리', inputSchema: 'LoginRequestSchema', outputSchema: 'AuthResponseSchema' },
      { name: 'register', description: '회원가입 처리', inputSchema: 'RegisterRequestSchema', outputSchema: 'AuthResponseSchema' },
      { name: 'refresh', description: '토큰 갱신', inputSchema: 'RefreshRequestSchema', outputSchema: 'TokenPairSchema' },
      { name: 'logout', description: '로그아웃 처리', inputSchema: 'LogoutRequestSchema', outputSchema: 'VoidSchema' },
      { name: 'validate', description: 'Access Token 검증', inputSchema: 'TokenSchema', outputSchema: 'UserContextSchema' },
    ],
    rulesPath: '.claude/agents/auth-domain.md',
  },
  {
    id: 'content-domain',
    domain: 'content',
    managedBlocks: ['content.query', 'content.cache', 'content.response', 'content.hands', 'content.timeline'],
    capabilities: [
      { name: 'getContent', description: '콘텐츠 상세 조회', inputSchema: 'ContentIdSchema', outputSchema: 'ContentDetailSchema' },
      { name: 'listContents', description: '콘텐츠 목록 조회', inputSchema: 'ContentListQuerySchema', outputSchema: 'ContentListSchema' },
      { name: 'getHands', description: '핸드 목록 조회', inputSchema: 'HandQuerySchema', outputSchema: 'HandListSchema' },
      { name: 'buildTimeline', description: '타임라인 인덱스 생성', inputSchema: 'ContentIdSchema', outputSchema: 'TimelineIndexSchema' },
    ],
    rulesPath: '.claude/agents/content-domain.md',
  },
  {
    id: 'stream-domain',
    domain: 'stream',
    managedBlocks: ['stream.resolve', 'stream.transcode', 'stream.deliver', 'stream.monitor'],
    capabilities: [
      { name: 'getStreamUrl', description: 'HLS 스트림 URL 획득', inputSchema: 'StreamRequestSchema', outputSchema: 'StreamUrlSchema' },
      { name: 'getStreamStatus', description: '스트림 상태 조회', inputSchema: 'StreamIdSchema', outputSchema: 'StreamStatusSchema' },
      { name: 'startTranscode', description: '트랜스코딩 시작', inputSchema: 'TranscodeRequestSchema', outputSchema: 'TranscodeJobSchema' },
    ],
    rulesPath: '.claude/agents/stream-domain.md',
  },
  {
    id: 'search-domain',
    domain: 'search',
    managedBlocks: ['search.parse', 'search.search', 'search.rank'],
    capabilities: [
      { name: 'search', description: '전문 검색', inputSchema: 'SearchQuerySchema', outputSchema: 'SearchResultSchema' },
      { name: 'suggest', description: '자동완성', inputSchema: 'SuggestQuerySchema', outputSchema: 'SuggestionListSchema' },
    ],
    rulesPath: '.claude/agents/search-domain.md',
  },
];
