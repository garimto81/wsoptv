# Jellyfin Domain Agent Rules

**Level**: 1 (Domain)
**Role**: Jellyfin 미디어 서버 통합 관리 (라이브러리, 스트리밍, 메타데이터)

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `jellyfin-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Jellyfin |
| **Managed Blocks** | jellyfin.library, jellyfin.stream, jellyfin.metadata |
| **Scope** | Backend API 프록시 + Frontend 라이브러리 UI |

---

## 📁 수정 가능 파일 (Scope)

### Backend
| 파일 | 역할 |
|------|------|
| `backend/src/api/v1/jellyfin.py` | Jellyfin API 프록시 엔드포인트 |
| `backend/src/schemas/jellyfin.py` | Jellyfin 요청/응답 스키마 |
| `backend/src/services/jellyfin.py` | Jellyfin 서비스 로직 |
| `backend/src/core/config.py` | `JELLYFIN_*` 설정 (읽기 전용 참조) |

### Frontend
| 파일 | 역할 |
|------|------|
| `frontend/src/routes/jellyfin/+page.svelte` | 라이브러리 목록 페이지 |
| `frontend/src/routes/jellyfin/+page.ts` | 인증 가드 |
| `frontend/src/routes/jellyfin/watch/[id]/*` | 시청 페이지 |
| `frontend/src/lib/api/jellyfin.ts` | Jellyfin API 클라이언트 |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    JELLYFIN DOMAIN                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   library    │    │    stream    │    │   metadata   │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  • 라이브러리 조회     • HLS 스트림 URL     • 아이템 정보    │
│  • 콘텐츠 목록        • Direct Play URL    • 썸네일 URL     │
│  • 검색              • 트랜스코딩 설정     • 재생 상태      │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
Frontend ──▶ Backend (/api/v1/jellyfin/*) ──▶ Jellyfin Server (:8096)
   │              │                                │
   │              ├── WSOPTV 인증 필수              │
   │              └── API 프록시 패턴              │
   │                                               │
   └──────────── HLS 스트림 직접 연결 ─────────────┘
                  (인증된 사용자만)
```

---

## Constraints

### DO (해야 할 것)
- ✅ **위 Scope 파일만 수정** (다른 도메인 오염 방지)
- ✅ Backend를 통한 Jellyfin API 프록시
- ✅ WSOPTV 인증 필수 (`ActiveUser` 의존성)
- ✅ HLS 스트리밍 우선 (호환성)
- ✅ 썸네일 캐싱 활용
- ✅ 에러 메시지 사용자 친화적으로 (영문)

### DON'T (하지 말 것)
- ❌ auth, content, search, stream 도메인 파일 수정
- ❌ **다른 도메인의 DB 테이블 직접 조작** (users, sessions 등)
- ❌ **E2E 테스트에서 프로덕션 DB 사용**
- ❌ Frontend에서 Jellyfin 직접 호출 (CORS, 보안)
- ❌ Jellyfin 인증 직접 처리 (WSOPTV 인증 사용)
- ❌ `JELLYFIN_API_KEY` 프론트엔드 노출
- ❌ Direct Play 강제 (HLS fallback 필요)
- ❌ Jellyfin URL 하드코딩 (config.py 참조)

### ⚠️ 크로스 도메인 주의사항
```
Jellyfin 작업 시 auth-domain 경계 침범 금지!

✅ 허용: Jellyfin API 호출, jellyfin.py 수정, Frontend Jellyfin 페이지
❌ 금지: users 테이블 조작, auth 관련 테스트 데이터 생성

테스트 시 인증이 필요하면:
→ 기존 테스트 유저 사용
→ 또는 auth-domain에 요청 (직접 DB 조작 금지)
```

---

## 🐳 Docker 재빌드 규칙

| 변경 대상 | 재빌드 명령 |
|----------|------------|
| Backend만 | `docker compose build backend && docker compose up -d backend` |
| Frontend만 | `docker compose build frontend && docker compose up -d frontend` |
| **둘 다** | `docker compose build backend frontend && docker compose up -d` |

> ⚠️ **중요**: Jellyfin 설정 변경 시 `.env` 확인 후 Backend 재빌드

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `getServerInfo` | - | `JellyfinServerInfo` | 서버 정보 조회 |
| `getLibraries` | - | `JellyfinLibrary[]` | 라이브러리 목록 |
| `getContents` | `{library?, q?, page?, limit?}` | `JellyfinContentList` | 콘텐츠 목록/검색 |
| `getContent` | `itemId` | `JellyfinContent` | 단일 콘텐츠 정보 |
| `getStreamInfo` | `itemId` | `JellyfinStreamInfo` | 스트림 URL 정보 |
| `getThumbnail` | `itemId` | `image` | 썸네일 이미지 |

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `JELLYFIN_UNAVAILABLE` | 503 | Jellyfin 서버 연결 실패 | ✅ (재시도) |
| `JELLYFIN_UNAUTHORIZED` | 401 | Jellyfin API 키 무효 | ❌ (설정 확인) |
| `JELLYFIN_ITEM_NOT_FOUND` | 404 | 아이템을 찾을 수 없음 | ❌ |
| `JELLYFIN_STREAM_ERROR` | 500 | 스트림 생성 실패 | ✅ (fallback) |

---

## Request/Response Schema

### JellyfinContent
```typescript
{
  jellyfinId: string       // Jellyfin 내부 ID
  title: string
  description?: string
  durationSec: number
  thumbnailUrl?: string
  streamUrl?: string
  libraryName?: string
  path?: string           // 파일 경로 (관리자용)
  year?: number
  dateCreated?: string
  mediaType: string       // "Video", "Movie", etc.
  supportsDirectPlay: boolean
  supportsHls: boolean
}
```

### JellyfinStreamInfo
```typescript
{
  itemId: string
  hlsUrl: string          // HLS 스트리밍 URL
  directUrl: string       // Direct Play URL (fallback)
  thumbnailUrl: string
}
```

---

## Jellyfin Integration Notes

### 서버 설정

```env
# Backend → Jellyfin 통신 (Docker 컨테이너에서 호스트 접근)
JELLYFIN_HOST=http://host.docker.internal:8096

# Browser → Jellyfin 스트리밍 (브라우저에서 직접 접근)
JELLYFIN_BROWSER_HOST=http://localhost:8096

# Jellyfin API 키
JELLYFIN_API_KEY=your-api-key-here
```

> ⚠️ **중요**: `JELLYFIN_HOST`와 `JELLYFIN_BROWSER_HOST`를 분리해야 합니다!
> - `JELLYFIN_HOST`: Docker 컨테이너 내부에서 Jellyfin 서버에 접근할 때 사용 (`host.docker.internal`)
> - `JELLYFIN_BROWSER_HOST`: 브라우저에서 스트림 URL에 접근할 때 사용 (`localhost`)

### API 키 생성
1. Jellyfin 관리자 대시보드 접속
2. 대시보드 → API 키 → 새 키 생성
3. `.env` 파일에 `JELLYFIN_API_KEY` 설정

### 스트리밍 우선순위
1. **HLS** (기본) - 브라우저 호환성 최고
2. **Direct Play** (fallback) - 트랜스코딩 불필요 시

---

## Testing

- **단위 테스트**: `backend/tests/test_jellyfin.py`
- **E2E 테스트**: `apps/web/e2e/specs/jellyfin/`
- **Mock 정책**: Jellyfin 응답 Mock 사용 (실 서버 의존 최소화)

---

## Security Checklist

- [x] Jellyfin API 키 환경 변수 관리
- [x] Backend 프록시를 통한 API 호출
- [x] WSOPTV 인증 필수
- [ ] Rate Limiting 적용
- [ ] 스트림 URL 만료 처리
