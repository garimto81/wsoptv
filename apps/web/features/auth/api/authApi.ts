/**
 * Auth API Functions
 *
 * 인증 관련 백엔드 API 호출 함수
 * @see ../AGENT_RULES.md
 */

import { z } from 'zod';
import type {
  LoginRequest,
  RegisterRequest,
  RefreshRequest,
  AuthResponse,
  TokenPair,
  AuthError,
  AuthErrorCode
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE = '/api/v1/auth';

// ============================================================================
// Validation Schemas
// ============================================================================

export const loginRequestSchema = z.object({
  username: z.string().min(1, '아이디를 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
  rememberMe: z.boolean().optional()
});

export const registerRequestSchema = z.object({
  username: z
    .string()
    .min(4, '아이디는 4자 이상이어야 합니다')
    .max(50, '아이디는 50자 이하여야 합니다')
    .regex(/^[a-zA-Z0-9_]+$/, '영문, 숫자, 밑줄만 사용 가능합니다'),
  password: z
    .string()
    .min(8, '비밀번호는 8자 이상이어야 합니다')
    .max(128, '비밀번호는 128자 이하여야 합니다')
    .regex(/[A-Z]/, '대문자를 포함해야 합니다')
    .regex(/[a-z]/, '소문자를 포함해야 합니다')
    .regex(/[0-9]/, '숫자를 포함해야 합니다'),
  displayName: z.string().min(2).max(100).optional()
});

// ============================================================================
// API Error Handling
// ============================================================================

class AuthApiError extends Error {
  code: AuthErrorCode;
  status: number;

  constructor(code: AuthErrorCode, message: string, status: number = 400) {
    super(message);
    this.name = 'AuthApiError';
    this.code = code;
    this.status = status;
  }

  toAuthError(): AuthError {
    return { code: this.code, message: this.message };
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const code = mapStatusToErrorCode(response.status, error.code);
    throw new AuthApiError(code, error.message || '요청 처리 중 오류가 발생했습니다', response.status);
  }
  return response.json();
}

function mapStatusToErrorCode(status: number, serverCode?: string): AuthErrorCode {
  if (serverCode && isValidAuthErrorCode(serverCode)) {
    return serverCode;
  }

  switch (status) {
    case 401:
      return 'AUTH_INVALID_CREDENTIALS';
    case 403:
      return 'AUTH_PENDING_APPROVAL';
    case 409:
      return 'AUTH_USERNAME_EXISTS';
    case 429:
      return 'AUTH_RATE_LIMITED';
    default:
      return 'AUTH_INVALID_CREDENTIALS';
  }
}

function isValidAuthErrorCode(code: string): code is AuthErrorCode {
  const validCodes: AuthErrorCode[] = [
    'AUTH_INVALID_CREDENTIALS',
    'AUTH_TOKEN_EXPIRED',
    'AUTH_PENDING_APPROVAL',
    'AUTH_REJECTED',
    'AUTH_USERNAME_EXISTS',
    'AUTH_RATE_LIMITED'
  ];
  return validCodes.includes(code as AuthErrorCode);
}

// ============================================================================
// Token Storage
// ============================================================================

const TOKEN_KEY = 'wsoptv_tokens';

export function saveTokens(tokens: TokenPair): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

export function loadTokens(): TokenPair | null {
  if (typeof window === 'undefined') return null;
  const stored = localStorage.getItem(TOKEN_KEY);
  if (!stored) return null;

  try {
    return JSON.parse(stored) as TokenPair;
  } catch {
    return null;
  }
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

export function getAccessToken(): string | null {
  const tokens = loadTokens();
  if (!tokens) return null;

  // 토큰 만료 확인
  if (Date.now() > tokens.expiresAt) {
    return null;
  }

  return tokens.accessToken;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * 로그인 API
 */
export async function login(request: LoginRequest): Promise<AuthResponse> {
  // 입력 검증
  const validated = loginRequestSchema.parse(request);

  const response = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(validated)
  });

  const result = await handleResponse<AuthResponse>(response);

  // 토큰 저장
  saveTokens(result.tokens);

  return result;
}

/**
 * 회원가입 API
 */
export async function register(request: RegisterRequest): Promise<AuthResponse> {
  // 입력 검증
  const validated = registerRequestSchema.parse(request);

  const response = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(validated)
  });

  const result = await handleResponse<AuthResponse>(response);

  // 토큰 저장
  saveTokens(result.tokens);

  return result;
}

/**
 * 토큰 갱신 API
 */
export async function refresh(request: RefreshRequest): Promise<TokenPair> {
  const response = await fetch(`${API_BASE}/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  const result = await handleResponse<TokenPair>(response);

  // 새 토큰 저장
  saveTokens(result);

  return result;
}

/**
 * 로그아웃 API
 */
export async function logout(): Promise<void> {
  const token = getAccessToken();

  if (token) {
    try {
      await fetch(`${API_BASE}/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        }
      });
    } catch {
      // 로그아웃 API 실패해도 로컬 토큰은 삭제
    }
  }

  clearTokens();
}

/**
 * 현재 사용자 정보 조회
 */
export async function getCurrentUser(): Promise<AuthResponse['user'] | null> {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!response.ok) {
      if (response.status === 401) {
        clearTokens();
      }
      return null;
    }

    return response.json();
  } catch {
    return null;
  }
}

/**
 * 토큰 자동 갱신 시도
 */
export async function tryRefreshToken(): Promise<boolean> {
  const tokens = loadTokens();
  if (!tokens?.refreshToken) return false;

  try {
    await refresh({ refreshToken: tokens.refreshToken });
    return true;
  } catch {
    clearTokens();
    return false;
  }
}
