/**
 * Auth Hooks
 *
 * 인증 관련 유틸리티 훅
 * @see ../AGENT_RULES.md
 */

import { authStore } from '../stores/authStore';
import { getAccessToken } from '../api/authApi';

// ============================================================================
// useAuth Hook
// ============================================================================

/**
 * 인증 상태 및 액션 접근 훅
 *
 * @example
 * const { user, isAuthenticated, login, logout } = useAuth();
 */
export function useAuth() {
  return {
    // State
    get user() {
      return authStore.user;
    },
    get isAuthenticated() {
      return authStore.isAuthenticated;
    },
    get isLoading() {
      return authStore.isLoading;
    },
    get error() {
      return authStore.error;
    },

    // Actions
    login: authStore.login,
    register: authStore.register,
    logout: authStore.logout,
    clearError: authStore.clearError
  };
}

// ============================================================================
// useSession Hook
// ============================================================================

/**
 * 세션 관련 유틸리티 훅
 *
 * @example
 * const { token, isExpired, refresh } = useSession();
 */
export function useSession() {
  return {
    /**
     * 현재 액세스 토큰 (만료되었으면 null)
     */
    get token() {
      return getAccessToken();
    },

    /**
     * 토큰 존재 여부
     */
    get hasToken() {
      return !!getAccessToken();
    },

    /**
     * 토큰 갱신
     */
    refresh: authStore.refresh,

    /**
     * 앱 초기화 (세션 복원)
     */
    initialize: authStore.initialize
  };
}

// ============================================================================
// useRequireAuth Hook
// ============================================================================

/**
 * 인증 필수 페이지에서 사용하는 훅
 * 인증되지 않으면 로그인 페이지로 리다이렉트 해야 함
 *
 * @example
 * const { user, isReady } = useRequireAuth();
 *
 * if (!isReady) return <Spinner />;
 * if (!user) return <Navigate to="/login" />;
 */
export function useRequireAuth() {
  return {
    get user() {
      return authStore.user;
    },
    get isReady() {
      return authStore.isInitialized && !authStore.isLoading;
    },
    get isAuthenticated() {
      return authStore.isAuthenticated;
    }
  };
}

// ============================================================================
// Authorization Helpers
// ============================================================================

/**
 * 사용자 역할 확인
 */
export function hasRole(role: 'admin' | 'user' | 'guest'): boolean {
  const user = authStore.user;
  if (!user) return false;
  return user.role === role;
}

/**
 * 관리자 여부 확인
 */
export function isAdmin(): boolean {
  return hasRole('admin');
}

/**
 * 사용자 승인 상태 확인
 */
export function isApproved(): boolean {
  const user = authStore.user;
  return user?.status === 'approved';
}
