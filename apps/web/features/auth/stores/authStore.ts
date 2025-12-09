/**
 * Auth Store
 *
 * Svelte 5 runes 기반 인증 상태 관리
 * @see ../AGENT_RULES.md
 */

import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthState,
  AuthError
} from '../types';
import * as authApi from '../api/authApi';

// ============================================================================
// Store State (Svelte 5 Runes)
// ============================================================================

let user = $state<User | null>(null);
let isAuthenticated = $state(false);
let isLoading = $state(false);
let error = $state<AuthError | null>(null);
let isInitialized = $state(false);

// ============================================================================
// Derived State
// ============================================================================

const state = $derived<AuthState>({
  user,
  tokens: authApi.loadTokens(),
  isAuthenticated,
  isLoading,
  error
});

// ============================================================================
// Actions
// ============================================================================

/**
 * 로그인
 */
async function login(request: LoginRequest): Promise<void> {
  isLoading = true;
  error = null;

  try {
    const response = await authApi.login(request);
    user = response.user;
    isAuthenticated = true;
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as AuthError;
    } else {
      error = { code: 'AUTH_INVALID_CREDENTIALS', message: '로그인에 실패했습니다' };
    }
    throw e;
  } finally {
    isLoading = false;
  }
}

/**
 * 회원가입
 */
async function register(request: RegisterRequest): Promise<void> {
  isLoading = true;
  error = null;

  try {
    const response = await authApi.register(request);
    user = response.user;
    // 회원가입 후 승인 대기 상태일 수 있음
    isAuthenticated = response.user.status === 'approved';
  } catch (e) {
    if (e instanceof Error && 'code' in e) {
      error = { code: (e as { code: string }).code, message: e.message } as AuthError;
    } else {
      error = { code: 'AUTH_INVALID_CREDENTIALS', message: '회원가입에 실패했습니다' };
    }
    throw e;
  } finally {
    isLoading = false;
  }
}

/**
 * 로그아웃
 */
async function logout(): Promise<void> {
  isLoading = true;

  try {
    await authApi.logout();
  } finally {
    user = null;
    isAuthenticated = false;
    isLoading = false;
    error = null;
  }
}

/**
 * 토큰 갱신
 */
async function refresh(): Promise<void> {
  const tokens = authApi.loadTokens();
  if (!tokens?.refreshToken) {
    isAuthenticated = false;
    return;
  }

  try {
    await authApi.refresh({ refreshToken: tokens.refreshToken });
    // 사용자 정보도 다시 가져오기
    const currentUser = await authApi.getCurrentUser();
    if (currentUser) {
      user = currentUser;
      isAuthenticated = true;
    }
  } catch {
    user = null;
    isAuthenticated = false;
  }
}

/**
 * 에러 초기화
 */
function clearError(): void {
  error = null;
}

/**
 * 초기화 (앱 시작 시 호출)
 */
async function initialize(): Promise<void> {
  if (isInitialized) return;

  isLoading = true;

  try {
    const currentUser = await authApi.getCurrentUser();
    if (currentUser) {
      user = currentUser;
      isAuthenticated = true;
    } else {
      // 토큰 갱신 시도
      const refreshed = await authApi.tryRefreshToken();
      if (refreshed) {
        const refreshedUser = await authApi.getCurrentUser();
        if (refreshedUser) {
          user = refreshedUser;
          isAuthenticated = true;
        }
      }
    }
  } catch {
    user = null;
    isAuthenticated = false;
  } finally {
    isLoading = false;
    isInitialized = true;
  }
}

// ============================================================================
// Store Export
// ============================================================================

export function useAuthStore() {
  return {
    // State (readonly)
    get state() {
      return state;
    },
    get user() {
      return user;
    },
    get isAuthenticated() {
      return isAuthenticated;
    },
    get isLoading() {
      return isLoading;
    },
    get error() {
      return error;
    },
    get isInitialized() {
      return isInitialized;
    },

    // Actions
    login,
    register,
    logout,
    refresh,
    clearError,
    initialize
  };
}

// 싱글톤 인스턴스 (서버 사이드에서 주의 필요)
export const authStore = useAuthStore();
