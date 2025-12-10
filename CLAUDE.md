# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 7.0.0 | **Context**: Windows, PowerShell

---

## Project Overview

WSOPTV는 18TB+ 포커 방송 아카이브를 위한 초대 기반 VOD 스트리밍 플랫폼입니다.

| Stack | Technology |
|-------|------------|
| **Frontend** | SvelteKit 2, Svelte 5, TypeScript, hls.js |
| **Backend** | FastAPI 0.115, SQLAlchemy 2, Pydantic 2 |
| **Database** | PostgreSQL 16, MeiliSearch 1.11, Redis 7 |
| **E2E Testing** | Playwright (Chromium, Firefox, WebKit) |
| **Infrastructure** | Docker Compose (172.28.0.0/16 network) |

---

## Architecture

```
Frontend :3000 ──▶ Backend :8001 ──▶ PostgreSQL :5433
(SvelteKit)        (FastAPI)        MeiliSearch :7700
                       │            Redis :6379
                       └──▶ Jellyfin :8096 (Windows Native)
```

**Data Flow**: `NAS(SMB) → archive-analyzer → pokervod.db → Backend → Frontend`

### Data Models

| Model | Description | Relations |
|-------|-------------|-----------|
| `User` | 사용자 계정 | → UserSession, WatchProgress |
| `Catalog` | 최상위 카탈로그 | → Series |
| `Series` | 시리즈/시즌 | → Content |
| `Content` | VOD 콘텐츠 | → File, Hand |
| `Hand` | 포커 핸드 | → HandPlayer, Player |

---

## Block Agent System (핵심)

AI 컨텍스트 최적화를 위한 **도메인 기반 블럭화 아키텍처**:

```
Orchestrator → Domain Agent → Block → AGENT_RULES.md
```

| Domain | Scope | Agent File |
|--------|-------|------------|
| **auth** | 인증, 세션, JWT | `.claude/agents/auth-domain.md` |
| **content** | 콘텐츠, 핸드, 타임라인 | `.claude/agents/content-domain.md` |
| **stream** | 스트리밍, HLS | `.claude/agents/stream-domain.md` |
| **search** | 검색, MeiliSearch | `.claude/agents/search-domain.md` |
| **migration** | 데이터 마이그레이션 | `.claude/agents/migration-domain.md` |
| **jellyfin** | Jellyfin 통합, 라이브러리 | `.claude/agents/jellyfin-domain.md` |

### 작업 전 필수 로딩

```
1. .claude/agents/orchestrator.md      # 라우팅 규칙
2. .claude/agents/{domain}-domain.md   # 도메인 규칙
3. apps/web/features/{domain}/AGENT_RULES.md  # 블럭 제약사항 (해당 시)
```

---

## 핵심 규칙

> **전역 규칙 적용**: [상위 CLAUDE.md](../CLAUDE.md) 참조

---

## Build & Run Commands

### Docker (권장)

```powershell
docker compose up -d                      # 전체 서비스 시작
docker compose logs -f backend            # 백엔드 로그
docker compose restart backend            # 백엔드 재시작
docker compose build backend frontend     # 재빌드
```

### Backend (로컬 개발)

```powershell
cd D:\AI\claude01\wsoptv\backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001

# 테스트
pytest tests/ -v
pytest tests/test_auth.py::test_login -v  # 단일 테스트 함수
```

### Frontend (로컬 개발)

```powershell
cd D:\AI\claude01\wsoptv\frontend
npm install
npm run dev                               # 개발 서버 :3000
npm run check                             # svelte-check (TypeScript)
npm run lint                              # ESLint
```

### E2E Testing

```powershell
cd D:\AI\claude01\wsoptv\apps\web
npx playwright test                            # 전체 테스트
npx playwright test e2e/specs/auth/            # 도메인별 테스트
npx playwright test e2e/performance/           # 성능 테스트 (Web Vitals)
npx playwright test e2e/visual/                # 시각적 회귀 테스트
npx playwright test --project=chromium         # 브라우저 지정
```

---

## Workflow Commands

| 커맨드 | 용도 |
|--------|------|
| `/work-wsoptv "작업 지시"` | Block Agent 기반 전체 워크플로우 (권장) |
| `/commit` | 커밋 생성 |
| `/check` | 린트 + 테스트 |
| `/tdd` | TDD 워크플로우 |

`/work-wsoptv` 흐름: **Agent 라우팅 → 컨텍스트 분석 → 이슈 생성 → 구현 (격리) → E2E 검증 → PR**

---

## Key Constraints

| 규칙 | 설명 |
|------|------|
| **main 브랜치 수정 금지** | 반드시 `feat/{domain}/issue-N-desc` 브랜치 생성 |
| **컨텍스트 격리** | Block 작업 시 해당 폴더 내에서만 수정 |
| **UI 언어** | 모든 웹 UI 텍스트는 **영문**으로 작성 |
| **AGENT_RULES 준수** | 각 Block의 `DO/DON'T` 규칙 확인 필수 |

---

## Environment Variables

```env
# .env (필수)
POSTGRES_PASSWORD=your_password
MEILI_MASTER_KEY=your_meili_key
JWT_SECRET_KEY=your_jwt_secret

# NAS 마운트 (스트리밍용)
NAS_LOCAL_PATH=//10.10.100.122/docker/GGPNAs
```

---

## API Endpoints

### Active Endpoints (v0.2.0-jellyfin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | JWT 토큰 발급 |
| POST | `/api/v1/auth/register` | 회원가입 (승인 대기) |
| GET | `/api/v1/jellyfin/contents` | Jellyfin 콘텐츠 목록 |
| GET | `/api/v1/jellyfin/contents/{id}` | Jellyfin 콘텐츠 상세 |
| GET | `/api/v1/jellyfin/stream/{id}` | Jellyfin 스트림 URL (HLS/Direct) |
| GET | `/api/v1/jellyfin/libraries` | Jellyfin 라이브러리 목록 |
| GET | `/api/v1/jellyfin/search` | Jellyfin 콘텐츠 검색 |
| GET | `/api/v1/search` | MeiliSearch 통합 검색 |

### Deprecated Endpoints (비활성화됨)

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/api/v1/catalogs` | ❌ 비활성 (Jellyfin libraries 사용) |
| GET | `/api/v1/contents/{id}` | ❌ 비활성 (Jellyfin contents 사용) |
| GET | `/api/v1/stream/{id}` | ❌ 비활성 (Jellyfin stream 사용) |

API 문서: `http://localhost:8001/docs`

---

## Current Tasks

### Active: 데이터 마이그레이션 (Task 0002)

**Source**: `D:/AI/claude01/qwen_hand_analysis/data/pokervod.db` (SQLite)
**Target**: WSOPTV PostgreSQL

| 소스 테이블 | 타겟 테이블 | 레코드 수 |
|-------------|-------------|-----------|
| catalogs | catalogs | 12 |
| subcatalogs | series | 24 |
| players | players | 386 |
| files | contents + files | ~3,400 |
| hands | hands | 434 |
| hand_players | hand_players | 861 |

**상세**: `tasks/0002-migration-pokervod-to-wsoptv.md`
**Agent**: `.claude/agents/migration-domain.md`

### ✅ Completed: Jellyfin 단일 아키텍처 전환 (v0.2.0)

Docker Desktop WSL2의 Windows SMB 마운트 제한 해결 완료

**아키텍처**:
- **Jellyfin**: Windows Native 10.11.4 (NAS SMB 직접 액세스)
- **Docker 서비스**: PostgreSQL, MeiliSearch, Redis, Backend, Frontend

**구현 완료**:
- ✅ Backend: Jellyfin API 프록시 (`/api/v1/jellyfin/*`)
- ✅ Frontend: 단일 Jellyfin 기반 UI (`/`, `/watch/{id}`)
- ✅ 레거시 API 비활성화 (catalogs, contents, stream)
- ✅ 중복 라우트 제거 (/browse, /catalog, /series, /jellyfin)

**Frontend Routes (v0.2.0)**:
```
/                  → Jellyfin 콘텐츠 목록 (Home)
/watch/{id}        → Jellyfin 스트리밍 플레이어
/search            → MeiliSearch 통합 검색
/login             → 로그인
/register          → 회원가입
```

**상세**: `docs/proposals/0002-jellyfin-migration.md`
**E2E 체크리스트**: `docs/E2E_VERIFICATION_CHECKLIST.md`

---

## Documentation Reference

| 질문 유형 | 참조 문서 |
|-----------|-----------|
| 전체 구조 | `docs/lld/0001-lld-wsoptv-platform.md` |
| 모듈/타입 | `docs/lld/0002-lld-modules.md` |
| API 상세 | `docs/lld/0003-lld-api.md` |
| UI 컴포넌트 | `docs/lld/0004-lld-components.md` |
| 시퀀스/플로우 | `docs/lld/0005-lld-flows.md` |
| Block Agent 설계 | `docs/architecture/0001-block-agent-system.md` |

---

## Related Projects

| 프로젝트 | 경로 | 역할 |
|----------|------|------|
| archive-analyzer | `D:/AI/claude01/archive-analyzer` | NAS 스캔, 메타데이터 추출 |
| qwen_hand_analysis | `D:/AI/claude01/qwen_hand_analysis` | pokervod.db 소스 데이터 |
