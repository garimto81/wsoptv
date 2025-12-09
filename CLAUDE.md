# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 4.0.0 | **Context**: Windows, PowerShell

---

## Project Overview

WSOPTV는 18TB+ 포커 방송 아카이브를 위한 초대 기반 VOD 스트리밍 플랫폼입니다.

| Stack | Technology |
|-------|------------|
| **Frontend** | SvelteKit 2, Svelte 5, TypeScript, hls.js |
| **Backend** | FastAPI, SQLAlchemy 2, Pydantic 2 |
| **Database** | PostgreSQL 16, MeiliSearch, Redis |
| **E2E Testing** | Playwright (Chromium, Firefox, WebKit) |
| **Infrastructure** | Docker Compose |

---

## Architecture

```
                    ┌───────────────────────┐
                    │    Frontend :3000     │
                    │    (SvelteKit)        │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    Backend :8001      │
                    │    (FastAPI)          │
                    └───────────┬───────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
    ▼                           ▼                           ▼
PostgreSQL :5432       MeiliSearch :7700              Redis :6379
```

### Block Agent System

AI 컨텍스트 최적화를 위한 도메인 기반 블럭화 아키텍처:

```
Orchestrator → Domain Agent → Block → AGENT_RULES.md
```

| Domain | Block Folder | Scope |
|--------|--------------|-------|
| auth | `apps/web/features/auth/` | 인증, 세션, JWT |
| content | `apps/web/features/content/` | 콘텐츠, 핸드, 타임라인 |
| stream | `apps/web/features/player/` | 스트리밍, HLS |
| search | `apps/web/features/search/` | 검색, MeiliSearch |

---

## Project Structure

```
wsoptv/
├── backend/                 # FastAPI 백엔드
│   └── src/
│       ├── main.py         # 앱 엔트리포인트
│       ├── api/v1/         # API 엔드포인트 (auth, catalogs, contents, search, stream)
│       ├── core/           # config, database, security, deps
│       ├── models/         # SQLAlchemy 모델
│       ├── schemas/        # Pydantic 스키마
│       └── services/       # 비즈니스 로직
│
├── frontend/               # SvelteKit 프론트엔드
│   └── src/
│       ├── routes/         # 페이지 라우트
│       ├── lib/components/ # UI 컴포넌트
│       └── lib/stores/     # Svelte 스토어
│
├── apps/web/               # E2E 테스트 + Feature Blocks
│   ├── features/           # 도메인별 블럭 (AGENT_RULES.md 포함)
│   └── e2e/               # Playwright E2E 테스트
│
├── .claude/agents/         # Domain Agent 정의
└── docker-compose.yml      # 서비스 오케스트레이션
```

---

## Build & Run Commands

### Docker (권장)

```powershell
docker compose up -d                      # 전체 서비스 시작
docker compose logs -f backend            # 백엔드 로그
docker compose restart backend            # 백엔드 재시작
docker compose --profile migrate up migrator  # 데이터 마이그레이션
```

### Backend (로컬 개발)

```powershell
cd D:\AI\claude01\wsoptv\backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001

# 테스트
pytest tests/ -v
pytest tests/test_auth.py -v              # 단일 파일
```

### Frontend (로컬 개발)

```powershell
cd D:\AI\claude01\wsoptv\frontend
npm install
npm run dev                               # 개발 서버 :3000
npm run build                             # 프로덕션 빌드
npm run check                             # TypeScript 체크
npm run lint                              # ESLint
```

### E2E Testing

```powershell
cd D:\AI\claude01\wsoptv\apps\web
npx playwright test                       # 전체 테스트
npx playwright test e2e/specs/auth/       # 도메인별 테스트
npx playwright test --project=chromium    # 브라우저 지정
npx playwright show-report                # 결과 리포트
```

---

## Workflow Commands

| 커맨드 | 용도 |
|--------|------|
| `/work-wsoptv "작업 지시"` | Block Agent 기반 전체 워크플로우 |
| `/commit` | 커밋 생성 |
| `/check` | 린트 + 테스트 |
| `/tdd` | TDD 워크플로우 |

### /work-wsoptv 실행 흐름

```
Phase 0: Agent 라우팅
   ├─ Orchestrator → Domain 결정
   ├─ Domain Agent 규칙 로딩
   └─ Block AGENT_RULES.md 로딩

Phase 1: 컨텍스트 분석 (병렬)

Phase 2: 이슈 생성 + 브랜치

Phase 3: 구현 (컨텍스트 격리)
   └─ 해당 Block 폴더 내에서만 작업

Phase 4: E2E 자동 검증
   ├─ 타입 체크 + 린트
   ├─ Vitest 단위 테스트
   ├─ Playwright E2E (3 브라우저)
   └─ 실패 시 자동 수정 (최대 3회)

Phase 5: 커밋 + PR

Phase 6: 사용자 검증 (필요시)
```

---

## Key Constraints

| 규칙 | 설명 |
|------|------|
| **main 브랜치 수정 금지** | 반드시 feature 브랜치 생성 |
| **컨텍스트 격리** | Block 작업 시 해당 폴더 내에서만 수정 |
| **UI 언어** | 모든 웹 UI 텍스트는 **영문**으로 작성 |
| **AGENT_RULES 준수** | 각 Block의 DO/DON'T 규칙 확인 필수 |

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

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | 로그인 |
| POST | `/api/v1/auth/register` | 회원가입 |
| GET | `/api/v1/catalogs` | 카탈로그 목록 |
| GET | `/api/v1/contents/{id}` | 콘텐츠 상세 |
| GET | `/api/v1/search` | 통합 검색 |
| GET | `/api/v1/stream/{id}/playlist.m3u8` | HLS 스트리밍 |

API 문서: `http://localhost:8001/docs`

---

## Documentation

| 문서 | 위치 | 용도 |
|------|------|------|
| Block Agent Architecture | `docs/architecture/0001-block-agent-system.md` | 블럭화 설계 |
| Domain Agents | `.claude/agents/*.md` | 에이전트 규칙 |
| Block Rules | `apps/web/features/*/AGENT_RULES.md` | 블럭별 제약사항 |
| LLD Master | `docs/lld/0001-lld-wsoptv-platform.md` | 전체 구조 |
| E2E Workflow | `docs/proposals/0001-e2e-automation-workflow.md` | 자동화 워크플로우 |

### 문서 참조 우선순위

| 질문 유형 | 참조 문서 |
|-----------|-----------|
| 전체 구조 | `0001-lld-wsoptv-platform.md` |
| 모듈/타입 | `0002-lld-modules.md` |
| API | `0003-lld-api.md` |
| UI 컴포넌트 | `0004-lld-components.md` |
| 시퀀스/플로우 | `0005-lld-flows.md` |

---

## Current Status: Phase 6 Jellyfin 전환 (진행 중)

> **문제**: Docker Desktop WSL2는 Windows SMB 네트워크 드라이브 pass-through 불가 → HLS 스트리밍 실패
> **해결**: Jellyfin 하이브리드 아키텍처로 전환 결정 (✅ 승인됨)

### 전환 로드맵

| 주차 | 작업 | 상태 |
|------|------|------|
| Week 1-2 | Jellyfin 서버 설치, 라이브러리 구성 | ⬜ **다음 작업** |
| Week 3-4 | 포커 메타데이터 플러그인 개발 (C#) | ⬜ 대기 |
| Week 5-6 | 커스텀 웹 UI 통합 | ⬜ 대기 |
| Week 7-8 | 마이그레이션 & E2E 테스트 | ⬜ 대기 |

### Jellyfin 하이브리드 아키텍처

> ⚠️ **핵심**: Docker 서비스(PostgreSQL, MeiliSearch, Redis)는 **계속 유지**됩니다. Jellyfin만 Windows Native로 설치.

```
┌─────────────────────────────────────────────────────────────────┐
│  Windows Native                    │  Docker Compose (유지)     │
│  ─────────────────                 │  ─────────────────────     │
│  ┌─────────────────┐               │  ┌─────────────────────┐  │
│  │ Jellyfin :8096  │               │  │ PostgreSQL :5432    │  │
│  │ • NAS 직접 액세스│               │  │ • 포커 메타데이터   │  │
│  │ • HW 트랜스코딩 │               │  ├─────────────────────┤  │
│  │ • HLS 스트리밍  │               │  │ MeiliSearch :7700   │  │
│  └────────┬────────┘               │  │ • 검색 인덱스       │  │
│           │                        │  ├─────────────────────┤  │
│           │ Jellyfin API           │  │ Redis :6379         │  │
│           ▼                        │  │ • 캐싱/세션         │  │
│  ┌────────────────────────────────────┴─────────────────────┤  │
│  │              Backend :8001 (Docker)                      │  │
│  │              • Jellyfin Proxy + 포커 API                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

| 컴포넌트 | 배포 | 역할 |
|----------|------|------|
| Jellyfin | 🖥️ Windows Native | NAS 스트리밍 (SMB 마운트 가능) |
| PostgreSQL | 🐳 Docker | 포커 메타 (핸드, 플레이어, 타임코드) |
| MeiliSearch | 🐳 Docker | 검색 인덱스 |
| Redis | 🐳 Docker | API 캐싱, 세션 |
| Backend/Frontend | 🐳 Docker | API + UI |

상세 계획: `docs/proposals/0002-jellyfin-migration.md`

---

## Related Projects

| 프로젝트 | 경로 | 역할 |
|----------|------|------|
| archive-analyzer | `D:/AI/claude01/archive-analyzer` | NAS 스캔, 메타데이터 추출 |
| shared-data | `D:/AI/claude01/shared-data` | pokervod.db (원본 데이터) |
