# Auth Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 인증/인가 전체 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `auth-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Auth |
| **Managed Blocks** | auth.validate, auth.token, auth.session |
| **Scope** | `apps/web/features/auth/`, `packages/agents/auth-domain/` |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AUTH DOMAIN                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   validate   │───▶│    token     │───▶│   session    │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  • 입력 검증          • JWT 발급           • 세션 관리     │
│  • Zod 스키마         • Refresh 처리       • Redis 저장    │
│  • Rate Limit         • Blacklist          • 만료 처리     │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ `features/auth/` 폴더 내 파일만 수정
- ✅ Zod 스키마로 모든 입력 검증
- ✅ bcrypt로 비밀번호 해싱
- ✅ JWT 만료 시간 환경 변수 참조
- ✅ 세션 데이터 Redis 저장

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ 비밀번호 평문 저장/로깅
- ❌ JWT 시크릿 하드코딩
- ❌ 다른 도메인 스토어 직접 접근
- ❌ SQL Injection 취약 쿼리 작성

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `login` | `LoginRequest` | `AuthResponse` | 사용자 로그인 처리 |
| `register` | `RegisterRequest` | `AuthResponse` | 회원가입 처리 |
| `refresh` | `RefreshRequest` | `TokenPair` | 토큰 갱신 |
| `logout` | `LogoutRequest` | `void` | 로그아웃 처리 |
| `validate` | `AccessToken` | `UserContext` | 토큰 검증 |

---

## Dependencies

### 내부 의존성
- `@wsoptv/types`: 공유 타입 (`User`, `TokenPair`, `AuthError`)
- `shared/utils`: 유틸리티 함수

### 외부 의존성
- `bcrypt`: 비밀번호 해싱
- `jose`: JWT 처리
- `zod`: 스키마 검증
- `redis`: 세션 저장소 (선택)

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 아이디/비밀번호 불일치 | ❌ |
| `AUTH_TOKEN_EXPIRED` | 401 | 토큰 만료 | ✅ (refresh) |
| `AUTH_PENDING_APPROVAL` | 403 | 승인 대기 중 | ❌ |
| `AUTH_REJECTED` | 403 | 가입 거절됨 | ❌ |
| `AUTH_USERNAME_EXISTS` | 409 | 아이디 중복 | ❌ |
| `AUTH_RATE_LIMITED` | 429 | 요청 제한 초과 | ✅ (wait) |

---

## Testing

- **단위 테스트**: `features/auth/__tests__/`
- **통합 테스트**: `tests/integration/auth/`
- **Mock 정책**: `authApi` 함수만 Mock 허용
- **테스트 DB**: SQLite in-memory 사용

---

## Security Checklist

- [ ] 비밀번호 bcrypt 해싱 (cost factor ≥ 12)
- [ ] JWT 시크릿 환경 변수 관리
- [ ] Refresh Token Rotation 적용
- [ ] Token Blacklist 구현
- [ ] Rate Limiting 적용
- [ ] CSRF 토큰 검증
