/**
 * Auth Feature - Public API
 *
 * 인증/인가 블럭의 외부 노출 인터페이스
 * 이 파일을 통해서만 외부에서 접근 가능
 *
 * @example
 * import { useAuth, LoginForm } from '$features/auth';
 *
 * @see AGENT_RULES.md
 */

// ============================================================================
// Components
// ============================================================================
export { LoginForm, RegisterForm, LogoutButton } from './components';

// ============================================================================
// Hooks
// ============================================================================
export { useAuth, useSession, useRequireAuth, hasRole, isAdmin, isApproved } from './hooks/useAuth';

// ============================================================================
// Stores
// ============================================================================
export { useAuthStore, authStore } from './stores/authStore';

// ============================================================================
// API
// ============================================================================
export { getAccessToken, loadTokens } from './api/authApi';

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
