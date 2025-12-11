# LLD: WSOPTV Platform (Master)

**Version**: 4.0.0 | **Date**: 2025-12-10 | **PRD**: [0001-prd-wsoptv-platform.md](../prds/0001-prd-wsoptv-platform.md)

> 토큰 최적화된 마스터 문서. 상세 구현은 서브 LLD 참조.
>
> ✅ **Netflix 스타일 동적 카탈로그 시스템**: 고정 계층 구조 대신 Row 기반 단일 홈페이지. [상세 설계](../architecture/0002-netflix-dynamic-catalog-system.md)

---

## 문서 구조

| 문서 | 설명 | 링크 |
|------|------|------|
| **Master** | 전체 아키텍처 개요 (현재 문서) | - |
| **Modules** | 패키지별 상세 인터페이스 | [0002-lld-modules.md](./0002-lld-modules.md) |
| **API** | REST API 전체 스펙 | [0003-lld-api.md](./0003-lld-api.md) |
| **Components** | Svelte 컴포넌트 상세 | [0004-lld-components.md](./0004-lld-components.md) |
| **Flows** | 시퀀스 다이어그램 | [0005-lld-flows.md](./0005-lld-flows.md) |

---

## 1. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    WSOPTV Monorepo                           │
├─────────────────────────────────────────────────────────────┤
│  apps/                      │  packages/                     │
│  ├── web (SvelteKit)        │  ├── @wsoptv/types            │
│  └── api (FastAPI)          │  ├── @wsoptv/ui               │
│                              │  ├── @wsoptv/player           │
│                              │  ├── @wsoptv/hands            │
│                              │  ├── @wsoptv/auth             │
│                              │  ├── @wsoptv/search           │
│                              │  ├── @wsoptv/streaming        │
│                              │  ├── @wsoptv/db               │
│                              │  └── @wsoptv/config           │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure (Docker)                                     │
│  PostgreSQL │ MeiliSearch │ Redis │ Transcoder              │
└─────────────────────────────────────────────────────────────┘
```

## 2. 패키지 의존성 그래프

```mermaid
graph LR
    subgraph Apps
        WEB[web]
        API[api]
    end
    subgraph Core
        TYPES[types]
        CONFIG[config]
    end
    subgraph Frontend
        UI[ui]
        PLAYER[player]
        HANDS_FE[hands]
        SEARCH[search]
        AUTH[auth]
    end
    subgraph Backend
        DB[db]
        STREAM[streaming]
    end

    WEB --> UI & PLAYER & SEARCH & AUTH
    API --> DB & STREAM
    PLAYER --> HANDS_FE --> TYPES
    UI --> TYPES & CONFIG
    DB --> TYPES & CONFIG
```

## 3. 핵심 도메인 요약

### 3.1 인증 (Auth)

| 항목 | 내용 |
|------|------|
| 방식 | JWT (HS256) + httpOnly 쿠키 (#1) |
| Access Token | 15분 (prod) / 24시간 (dev) |
| Refresh Token | 7일 (prod) / 30일 (dev) (#12) |
| 비밀번호 | bcrypt, cost=12 (#2) |
| 가입 | username + password → pending 상태 |
| 승인 | Admin 수동 승인 → approved |
| 상태 | `pending` / `approved` / `rejected` / `suspended` |

### 3.2 스트리밍 (Streaming)

| 항목 | 내용 |
|------|------|
| 프로토콜 | HLS (ABR) |
| 품질 | 360p / 480p / 720p / 1080p |
| 전략 | 인기 콘텐츠 프리트랜스코딩 + 온디맨드 |
| 캐시 | Redis (manifest) + 파일시스템 (segments) |

### 3.3 핸드 시스템 (Hands)

| 항목 | 내용 |
|------|------|
| 등급 | S (필수시청) / A (추천) / B (일반) / C (기본) |
| 스킵 | Netflix 스타일 오버레이 버튼 |
| 모드 | 전체 / 핸드만 / 하이라이트 (S,A) |

### 3.4 홈페이지 (Netflix 스타일 동적 Row)

| 항목 | 내용 |
|------|------|
| 구조 | 단일 홈페이지 + 동적 Row 목록 |
| Row Types | continue_watching, recently_added, library, trending |
| 데이터 소스 | Jellyfin Libraries (자동 Row 생성) |
| 네비게이션 | Home → Watch (2단계) |

### 3.5 검색 (Search)

| 항목 | 내용 |
|------|------|
| 엔진 | MeiliSearch |
| 검색 대상 | title, player, tags, library |
| 필터 | library_id, player, handGrade, year |
| 브라우징 | `/browse?library={id}` 필터 기반 |

## 4. API 엔드포인트 요약

| 그룹 | 엔드포인트 수 | 인증 | 상세 |
|------|-------------|------|------|
| Auth | 5 | 일부 | [0003-lld-api.md#1-auth](./0003-lld-api.md#1-auth) |
| **Home** | 1 | ✓ | [0003-lld-api.md#home](./0003-lld-api.md#2-home) |
| **Browse** | 1 | ✓ | [0003-lld-api.md#browse](./0003-lld-api.md#3-browse) |
| Jellyfin | 5 | ✓ | [0003-lld-api.md#jellyfin](./0003-lld-api.md#4-jellyfin) |
| Search | 1 | ✓ | [0003-lld-api.md#search](./0003-lld-api.md#5-search) |
| Stream | 1 | ✓ | [0003-lld-api.md#stream](./0003-lld-api.md#6-stream) |
| Progress | 2 | ✓ | [0003-lld-api.md#progress](./0003-lld-api.md#7-progress) |
| Admin | 2 | Admin | [0003-lld-api.md#admin](./0003-lld-api.md#8-admin) |

## 5. 컴포넌트 요약

| 컴포넌트 | 패키지 | 역할 | 상세 |
|----------|--------|------|------|
| `HomePage` | home | 동적 Row 목록 홈페이지 | [0004](./0004-lld-components.md#homepage) |
| `ContentRow` | home | Netflix 스타일 Row | [0004](./0004-lld-components.md#contentrow) |
| `ContentCard` | ui | 콘텐츠 카드 | [0004](./0004-lld-components.md#contentcard) |
| `VideoPlayer` | player | HLS 재생 + 핸드 감지 | [0004](./0004-lld-components.md#videoplayer) |
| `SkipButtons` | player | Netflix 스타일 스킵 | [0004](./0004-lld-components.md#skipbuttons) |
| `HandTimeline` | player | 타임라인 마커 | [0004](./0004-lld-components.md#handtimeline) |
| `SearchBar` | search | 자동완성 검색 | [0004](./0004-lld-components.md#searchbar) |

## 6. 주요 플로우

| 플로우 | 설명 | 상세 |
|--------|------|------|
| 비디오 재생 | 콘텐츠 선택 → HLS 스트리밍 → 핸드 감지 | [0005](./0005-lld-flows.md#1-video-playback) |
| 회원가입/승인 | 가입 → pending → Admin 승인 | [0005](./0005-lld-flows.md#2-auth) |
| 검색 | 쿼리 → MeiliSearch → 결과 | [0005](./0005-lld-flows.md#3-search) |
| 핸드 스킵 | 비핸드 구간 → 버튼 표시 → 다음 핸드 | [0005](./0005-lld-flows.md#4-hand-skip) |

## 7. 에러 코드 요약

> 전체 에러 코드 목록은 [0003-lld-api.md#에러-코드-전체-목록](./0003-lld-api.md#에러-코드-전체-목록) 참조 (#18)

| Category | Codes | HTTP |
|----------|-------|------|
| **Auth** | `AUTH_INVALID_CREDENTIALS`, `AUTH_PENDING_APPROVAL`, `AUTH_TOKEN_EXPIRED` | 401, 403 |
| **Content** | `CONTENT_NOT_FOUND`, `LIBRARY_NOT_FOUND` | 404 |
| **Jellyfin** | `JELLYFIN_ERROR`, `JELLYFIN_CONNECTION_ERROR` | 502, 503 |
| **Stream** | `STREAM_NOT_READY`, `STREAM_SOURCE_ERROR`, `STREAM_ACCESS_DENIED` | 503, 500, 403 |
| **Rate Limit** | `RATE_LIMIT_EXCEEDED` | 429 |
| **Validation** | `VALIDATION_ERROR`, `PROGRESS_VERSION_CONFLICT` | 400, 409 |

## 8. 기술 스택

| 레이어 | 기술 |
|--------|------|
| Monorepo | Turborepo + pnpm |
| Frontend | SvelteKit + Tailwind |
| Backend | FastAPI + SQLAlchemy |
| Database | PostgreSQL 16 |
| Search | MeiliSearch 1.6 |
| Cache | Redis 7 |
| Streaming | FFmpeg + HLS |
| Player | Video.js + hls.js |

---

## 9. Phase 2: Jellyfin 하이브리드 아키텍처 (전환 예정)

Docker Desktop + Windows SMB 제약으로 Jellyfin 기반 하이브리드 아키텍처로 전환이 승인되었습니다.

> ⚠️ **핵심**: Docker 서비스(PostgreSQL, MeiliSearch, Redis)는 **계속 유지**됩니다. Jellyfin만 Windows Native로 설치.

### 9.1 배포 구조

| 컴포넌트 | 배포 방식 | 역할 | 변경사항 |
|----------|----------|------|----------|
| **Jellyfin** | 🖥️ Windows Native | 미디어 스트리밍, NAS 직접 액세스, HW 트랜스코딩 | **신규** |
| **PostgreSQL** | 🐳 Docker | 포커 메타데이터 (핸드, 플레이어, 타임코드, 사용자) | 유지 |
| **MeiliSearch** | 🐳 Docker | 검색 인덱스 (포커 특화) | 유지 |
| **Redis** | 🐳 Docker | API 캐싱, Jellyfin 응답 캐싱, 세션 | 유지 |
| **Backend** | 🐳 Docker | Jellyfin Proxy + 포커 메타 API | 수정 |
| **Frontend** | 🐳 Docker | SvelteKit UI (Jellyfin 플레이어 통합) | 수정 |

### 9.2 전환 아키텍처

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    WSOPTV Phase 2: Hybrid Deployment                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [Windows Native]                    [Docker Compose - 유지]              │
│  ┌─────────────────────┐             ┌──────────────────────────────┐   │
│  │ Jellyfin :8096      │             │ PostgreSQL :5432 (포커 메타) │   │
│  │ • NAS 직접 마운트   │             │ MeiliSearch :7700 (검색)     │   │
│  │   (Z:\GGPNAs)       │             │ Redis :6379 (캐싱)           │   │
│  │ • HW 트랜스코딩     │             ├──────────────────────────────┤   │
│  │ • HLS 스트리밍      │────────────▶│ Backend :8001                │   │
│  └─────────────────────┘  API 호출   │ • Jellyfin Proxy             │   │
│                                       │ • 포커 메타 API              │   │
│                                       ├──────────────────────────────┤   │
│                                       │ Frontend :3000               │   │
│                                       │ • Jellyfin 플레이어 통합     │   │
│                                       │ • 핸드 타임라인/스킵 UI      │   │
│                                       └──────────────────────────────┘   │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

[네트워크 통신]
• Backend → Jellyfin: http://host.docker.internal:8096 (Docker에서 호스트 접근)
• Backend ↔ PostgreSQL/MeiliSearch/Redis: Docker 내부 네트워크 (172.28.x.x)
• Frontend → Backend: Docker 내부 (SvelteKit 서버 프록시)
```

### 전환 일정

| 주차 | 작업 | 담당 |
|------|------|------|
| Week 1-2 | Jellyfin 설치, 라이브러리 구성 | jellyfin-agent |
| Week 3-4 | 포커 메타데이터 플러그인 개발 | poker-agent |
| Week 5-6 | 커스텀 웹 UI 개발 | frontend-agent |
| Week 7-8 | 통합 테스트 및 마이그레이션 | test-agent |

### 코드 변경 범위

| 레이어 | 변경률 | 주요 변경 |
|--------|--------|----------|
| Backend | ~60-70% | streaming 모듈 제거, Jellyfin 연동 추가 |
| Frontend | ~40-50% | 플레이어 Jellyfin 통합 |
| Plugin | 100% 신규 | C# Jellyfin 플러그인 개발 |

상세 계획: [docs/proposals/0002-jellyfin-migration.md](../proposals/0002-jellyfin-migration.md)

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 LLD (단일 문서) |
| 2.0.0 | 2025-12-09 | 마스터 + 서브 문서 분할 |
| 2.1.0 | 2025-12-09 | 보안/성능/로직/스타일 이슈 32건 수정 (#1-#32) |
| 3.0.0 | 2025-12-09 | Jellyfin 하이브리드 아키텍처 전환 계획 추가 |
