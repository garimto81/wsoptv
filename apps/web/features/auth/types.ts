/**
 * Auth Feature Types
 *
 * 인증/인가 블럭의 타입 정의
 * @see AGENT_RULES.md
 */

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: number;
  username: string;
  displayName?: string;
  role: UserRole;
  status: UserStatus;
  createdAt: string;
  lastLoginAt?: string;
}

export type UserRole = 'admin' | 'user' | 'guest';
export type UserStatus = 'pending' | 'approved' | 'rejected' | 'suspended';

// ============================================================================
// Auth Request Types
// ============================================================================

export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  username: string;
  password: string;
  displayName?: string;
}

export interface RefreshRequest {
  refreshToken: string;
}

export interface LogoutRequest {
  accessToken: string;
}

// ============================================================================
// Auth Response Types
// ============================================================================

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface AuthResponse {
  user: User;
  tokens: TokenPair;
}

// ============================================================================
// Auth State
// ============================================================================

export interface AuthState {
  user: User | null;
  tokens: TokenPair | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;
}

export interface AuthActions {
  login: (request: LoginRequest) => Promise<void>;
  register: (request: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  clearError: () => void;
}

// ============================================================================
// Auth Errors
// ============================================================================

export type AuthErrorCode =
  | 'AUTH_INVALID_CREDENTIALS'
  | 'AUTH_TOKEN_EXPIRED'
  | 'AUTH_PENDING_APPROVAL'
  | 'AUTH_REJECTED'
  | 'AUTH_USERNAME_EXISTS'
  | 'AUTH_RATE_LIMITED';

export interface AuthError {
  code: AuthErrorCode;
  message: string;
}
