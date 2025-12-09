/**
 * @wsoptv/types - Block Agent System Type Definitions
 *
 * WSOPTV 플랫폼의 블럭 에이전트 시스템 타입 정의 패키지
 *
 * @version 1.0.0
 * @see docs/architecture/0001-block-agent-system.md
 */

// Block Types
export type {
  DomainType,
  BlockStatus,
  InputPort,
  OutputPort,
  BlockMetadata,
  Block,
  BlockRegistry,
  BlockSizeStatus,
  BlockSizeAnalysis,
} from './block';
export { BLOCK_SIZE_THRESHOLDS } from './block';

// Agent Types
export type {
  AgentLevel,
  AgentStatus,
  Capability,
  TaskType,
  Priority,
  RetryPolicy,
  Task,
  TaskResultStatus,
  TaskResult,
  HealthLevel,
  HealthStatus,
  Agent,
  DomainAgentConfig,
} from './agent';
export { DOMAIN_AGENT_CONFIGS } from './agent';

// Message Types
export type {
  MessageType,
  AgentMessage,
  BlockEventType,
  AgentEventType,
  AgentEvent,
  BlockStartedEvent,
  BlockCompletedEvent,
  BlockErrorEvent,
  EventHandler,
  Subscription,
  EventBus,
} from './message';

// Error Types
export type {
  ErrorSeverity,
  BlockErrorCode,
  AgentErrorCode,
  AuthErrorCode,
  ContentErrorCode,
  StreamErrorCode,
  SearchErrorCode,
  ErrorCode,
  FallbackStrategy,
  BlockError,
  ErrorRecoveryConfig,
  CircuitState,
  CircuitBreakerConfig,
  CircuitBreakerStatus,
} from './error';
export { ERROR_RECOVERY_MATRIX } from './error';
