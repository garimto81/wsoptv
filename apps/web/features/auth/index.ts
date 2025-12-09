/**
 * Auth Feature - Public API
 *
 * 인증/인가 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { useAuth, LoginForm } from '@/features/auth';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
// export { LoginForm } from './components/LoginForm';
// export { RegisterForm } from './components/RegisterForm';
// export { LogoutButton } from './components/LogoutButton';

// ============================================================================
// Hooks
// ============================================================================
// export { useAuth } from './hooks/useAuth';
// export { useSession } from './hooks/useSession';

// ============================================================================
// Stores
// ============================================================================
// export { useAuthStore } from './stores/authStore';

// ============================================================================
// Types
// ============================================================================
export type {
  User,
  UserRole,
  UserStatus,
  LoginRequest,
  RegisterRequest,
  RefreshRequest,
  LogoutRequest,
  TokenPair,
  AuthResponse,
  AuthState,
  AuthActions,
  AuthErrorCode,
  AuthError,
} from './types';
