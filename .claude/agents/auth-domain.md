# Auth Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 인증/인가 전체 관리 (회원가입, 로그인, 세션)

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `auth-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Auth |
| **Managed Blocks** | auth.register, auth.login, auth.session |
| **Scope** | Backend + Frontend 인증 관련 전체 |

---

## 📁 수정 가능 파일 (Scope)

### Backend
| 파일 | 역할 |
|------|------|
| `backend/src/api/v1/auth.py` | 인증 API 엔드포인트 |
| `backend/src/schemas/auth.py` | 요청/응답 스키마 |
| `backend/src/models/user.py` | User 모델 |
| `backend/src/core/security.py` | JWT, 비밀번호 해싱 |

### Frontend
| 파일 | 역할 |
|------|------|
| `frontend/src/routes/login/+page.svelte` | 로그인 페이지 |
| `frontend/src/routes/register/+page.svelte` | 회원가입 페이지 |
| `frontend/src/routes/register/pending/+page.svelte` | 승인 대기 페이지 |
| `frontend/src/lib/stores/auth.svelte.ts` | 인증 상태 스토어 |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AUTH DOMAIN                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   register   │    │    login     │    │   session    │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  • 회원가입 처리       • 로그인 처리       • 세션 관리     │
│  • 비밀번호 검증       • JWT 발급          • Cookie 처리   │
│  • 승인 대기          • 토큰 갱신          • 로그아웃      │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ **위 Scope 파일만 수정** (다른 도메인 오염 방지)
- ✅ Backend + Frontend 동시 변경 시 **둘 다 Docker 재빌드**
- ✅ bcrypt로 비밀번호 해싱
- ✅ JWT 시크릿 환경 변수 참조
- ✅ 에러 메시지 사용자 친화적으로 (영문)

### DON'T (하지 말 것)
- ❌ Jellyfin, content, search, stream 도메인 파일 수정
- ❌ 비밀번호 평문 저장/로깅
- ❌ JWT 시크릿 하드코딩
- ❌ 단일 서비스만 Docker 재빌드 (Backend만 또는 Frontend만)
- ❌ `shared/` 또는 `packages/` 직접 수정

---

## 🐳 Docker 재빌드 규칙

| 변경 대상 | 재빌드 명령 |
|----------|------------|
| Backend만 | `docker compose build backend && docker compose up -d backend` |
| Frontend만 | `docker compose build frontend && docker compose up -d frontend` |
| **둘 다** | `docker compose build backend frontend && docker compose up -d` |

> ⚠️ **중요**: Backend 스키마와 Frontend 폼이 함께 변경되면 반드시 **둘 다 재빌드**

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `login` | `LoginRequest` | `AuthResponse` | 사용자 로그인 처리 |
| `register` | `RegisterRequest` | `RegisterResponse` | 회원가입 처리 |
| `refresh` | Cookie | `TokenRefreshResponse` | 토큰 갱신 |
| `logout` | Cookie | `void` | 로그아웃 처리 |
| `me` | Cookie | `UserResponse` | 현재 사용자 정보 |

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 아이디/비밀번호 불일치 | ❌ |
| `AUTH_TOKEN_EXPIRED` | 401 | 토큰 만료 | ✅ (refresh) |
| `AUTH_PENDING_APPROVAL` | 403 | 승인 대기 중 | ❌ |
| `AUTH_REJECTED` | 403 | 가입 거절됨 | ❌ |
| `AUTH_USERNAME_EXISTS` | 409 | 아이디 중복 | ❌ |

---

## Request/Response Schema

### RegisterRequest
```typescript
{
  username: string      // 4-50자, 영문/숫자/밑줄
  password: string      // 4-128자
  passwordConfirm: string  // password와 일치해야 함
}
```

### LoginRequest
```typescript
{
  username: string
  password: string
}
```

---

## Testing

- **단위 테스트**: `backend/tests/test_auth.py`
- **E2E 테스트**: `apps/web/e2e/specs/auth/`
- **Mock 정책**: 실제 DB 사용 (테스트 격리)

---

## Security Checklist

- [x] 비밀번호 bcrypt 해싱
- [x] JWT 시크릿 환경 변수 관리
- [x] HTTP-Only Cookie 사용
- [ ] Refresh Token Rotation 적용
- [ ] Rate Limiting 적용
