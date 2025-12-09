/**
 * Block Agent System - Block Type Definitions
 *
 * 블럭은 WSOPTV 시스템의 최소 실행 단위입니다.
 * 각 블럭은 단일 책임을 가지며, 도메인 에이전트에 의해 관리됩니다.
 *
 * @version 1.0.0
 * @see docs/architecture/0001-block-agent-system.md
 */

// ============================================================================
// Domain Types
// ============================================================================

/**
 * 시스템의 도메인 유형
 * 각 도메인은 비즈니스 영역을 나타냅니다
 */
export type DomainType =
  | 'auth'     // 인증/인가
  | 'content'  // 콘텐츠 관리
  | 'stream'   // 스트리밍
  | 'search'   // 검색
  | 'player'   // 플레이어 (UI)
  | 'admin';   // 관리자

/**
 * 블럭의 상태
 */
export type BlockStatus =
  | 'idle'        // 대기 중
  | 'processing'  // 처리 중
  | 'error'       // 에러 발생
  | 'disabled';   // 비활성화

// ============================================================================
// Port Types
// ============================================================================

/**
 * 블럭의 입력 포트 정의
 * 블럭이 받아들이는 데이터의 인터페이스
 */
export interface InputPort {
  /** 포트 이름 */
  name: string;
  /** 데이터 타입 (TypeScript 타입 문자열) */
  type: string;
  /** 필수 여부 */
  required: boolean;
  /** Zod 스키마 참조 (선택) */
  validator?: string;
  /** 설명 */
  description?: string;
}

/**
 * 블럭의 출력 포트 정의
 * 블럭이 내보내는 데이터의 인터페이스
 */
export interface OutputPort {
  /** 포트 이름 */
  name: string;
  /** 데이터 타입 (TypeScript 타입 문자열) */
  type: string;
  /** 출력 조건 */
  emitsOn: 'success' | 'error' | 'always';
  /** 설명 */
  description?: string;
}

// ============================================================================
// Block Metadata
// ============================================================================

/**
 * 블럭 메타데이터
 */
export interface BlockMetadata {
  /** 블럭 설명 */
  description: string;
  /** 담당 에이전트 ID */
  owner: string;
  /** 태그 (분류용) */
  tags: string[];
  /** 생성일 */
  createdAt: string;
  /** 수정일 */
  updatedAt: string;
  /** 예상 파일 수 */
  estimatedFileCount?: number;
  /** 예상 토큰 수 */
  estimatedTokenCount?: number;
}

// ============================================================================
// Block Interface
// ============================================================================

/**
 * 블럭 인터페이스
 *
 * 블럭은 다음 원칙을 따릅니다:
 * - Single Responsibility: 하나의 관심사만 담당
 * - Self-Contained: 자체 완결성
 * - Explicit Dependencies: 명시적 의존성
 *
 * @example
 * const authValidateBlock: Block = {
 *   id: 'auth.validate',
 *   domain: 'auth',
 *   name: 'validate',
 *   version: '1.0.0',
 *   status: 'idle',
 *   inputs: [{ name: 'credentials', type: 'LoginRequest', required: true }],
 *   outputs: [{ name: 'validated', type: 'ValidatedCredentials', emitsOn: 'success' }],
 *   metadata: { description: '인증 정보 검증', owner: 'auth-domain', tags: ['auth'], ... }
 * };
 */
export interface Block {
  /** 블럭 고유 ID (format: {domain}.{name}) */
  id: string;
  /** 소속 도메인 */
  domain: DomainType;
  /** 블럭 이름 */
  name: string;
  /** 버전 (SemVer) */
  version: string;
  /** 현재 상태 */
  status: BlockStatus;
  /** 입력 포트 목록 */
  inputs: InputPort[];
  /** 출력 포트 목록 */
  outputs: OutputPort[];
  /** 메타데이터 */
  metadata: BlockMetadata;
}

// ============================================================================
// Block Registry
// ============================================================================

/**
 * 블럭 레지스트리
 * 시스템의 모든 블럭을 등록/조회
 */
export interface BlockRegistry {
  /** 블럭 등록 */
  register(block: Block): void;
  /** 블럭 조회 */
  get(blockId: string): Block | undefined;
  /** 도메인별 블럭 목록 */
  getByDomain(domain: DomainType): Block[];
  /** 모든 블럭 목록 */
  getAll(): Block[];
  /** 블럭 존재 여부 */
  has(blockId: string): boolean;
}

// ============================================================================
// Block Size Guide
// ============================================================================

/**
 * 블럭 사이즈 상태
 */
export type BlockSizeStatus =
  | 'optimal'    // 🟢 적정 (15-20 파일, 25k-35k 토큰)
  | 'warning'    // 🟡 경고 (20-30 파일, 35k-50k 토큰)
  | 'critical';  // 🔴 위험 (30+ 파일, 50k+ 토큰)

/**
 * 블럭 사이즈 분석 결과
 */
export interface BlockSizeAnalysis {
  blockId: string;
  fileCount: number;
  tokenCount: number;
  status: BlockSizeStatus;
  recommendation?: string;
}

/**
 * 블럭 사이즈 기준
 */
export const BLOCK_SIZE_THRESHOLDS = {
  file: {
    optimal: 20,
    warning: 30,
  },
  token: {
    optimal: 35000,
    warning: 50000,
  },
} as const;
