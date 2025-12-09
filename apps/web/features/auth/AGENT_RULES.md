# Auth Block Agent Rules

> 인증/인가 블럭 전용 AI 에이전트 규칙

---

## Identity

| 속성 | 값 |
|------|-----|
| **Role** | 인증/인가 전문가 |
| **Domain** | Auth |
| **Scope** | `features/auth/` 내부만 |
| **Parent Agent** | `auth-domain` |

---

## Folder Structure

```
features/auth/
├── components/           # 인증 관련 UI 컴포넌트
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── LogoutButton.tsx
├── hooks/                # 인증 관련 훅
│   ├── useAuth.ts
│   └── useSession.ts
├── stores/               # 인증 상태 관리
│   └── authStore.ts
├── api/                  # 인증 API 호출
│   └── authApi.ts
├── types.ts              # 인증 타입 정의
├── index.ts              # Public API
├── __tests__/            # 테스트
└── AGENT_RULES.md        # 이 파일
```

---

## Constraints

### DO (해야 할 것)
- ✅ 이 폴더 내 파일만 수정
- ✅ `types.ts`의 타입 정의 우선 확인
- ✅ `index.ts`를 통해 외부 노출 API 관리
- ✅ Zod 스키마로 입력 검증
- ✅ bcrypt로 비밀번호 해싱 (서버)
- ✅ 환경 변수로 시크릿 관리

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ `shared/ui` 컴포넌트 내부 수정
- ❌ 전역 상태 직접 접근 (스토어 통해서만)
- ❌ 하드코딩된 비밀값 사용
- ❌ 비밀번호 평문 저장/로깅
- ❌ JWT 시크릿 클라이언트 노출

---

## Dependencies

### 내부 의존성
```typescript
// ✅ 허용
import { Button } from '@/shared/ui';
import { cn } from '@/shared/utils';
import type { User } from '@wsoptv/types';
```

### 외부 의존성
```typescript
// ✅ 허용
import { z } from 'zod';
import { create } from 'zustand';
```

---

## Public API (index.ts)

```typescript
// 외부에서 사용 가능한 것만 export
export { LoginForm, RegisterForm, LogoutButton } from './components';
export { useAuth, useSession } from './hooks';
export type { AuthState, LoginRequest, RegisterRequest } from './types';
```

---

## Type Definitions (types.ts)

```typescript
// 이 블럭에서 사용하는 타입 정의
export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

---

## Testing

- **위치**: `__tests__/` 폴더
- **네이밍**: `*.test.ts`, `*.spec.ts`
- **Mock 정책**:
  - `authApi` 함수만 Mock 허용
  - 외부 의존성 (fetch, localStorage) Mock 허용
- **커버리지 목표**: 80%+

---

## Error Handling

```typescript
// 인증 에러 타입
export type AuthErrorCode =
  | 'AUTH_INVALID_CREDENTIALS'
  | 'AUTH_TOKEN_EXPIRED'
  | 'AUTH_PENDING_APPROVAL'
  | 'AUTH_REJECTED'
  | 'AUTH_USERNAME_EXISTS';

// 에러 처리 패턴
try {
  await authApi.login(credentials);
} catch (error) {
  if (error.code === 'AUTH_INVALID_CREDENTIALS') {
    // 사용자에게 에러 메시지 표시
  }
}
```

---

## Security Checklist

작업 완료 전 확인:

- [ ] 비밀번호가 평문으로 로깅되지 않음
- [ ] JWT 토큰이 안전하게 저장됨 (httpOnly cookie 권장)
- [ ] CSRF 토큰 검증 적용
- [ ] Rate Limiting 고려
- [ ] XSS 방지 (입력값 이스케이프)
