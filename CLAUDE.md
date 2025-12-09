# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

**Version**: 1.0.0 | **Context**: Windows, PowerShell, Docker

---

## Project Overview

WSOPTV는 18TB+ 포커 방송 아카이브를 기반으로 한 초대 기반 VOD 스트리밍 플랫폼입니다.

| 항목 | 내용 |
|------|------|
| **플랫폼명** | WSOPTV |
| **타겟 사용자** | 일반 포커 팬 (관리자 승인) |
| **핵심 기능** | 검색, 스트리밍 중계, 핸드 타임코드, 핸드 스킵 |
| **인증 방식** | 회원가입 + 관리자 승인 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 WSOPTV (Docker Network: 172.28.0.0/16)          │
├─────────────────────────────────────────────────────────────────┤
│  Database Tier          │  Application Tier                     │
│  ┌──────────────────┐   │  ┌──────────────────┐                │
│  │ PostgreSQL :5432 │   │  │ Backend    :8001 │                │
│  │ MeiliSearch:7700 │   │  │ Frontend   :3000 │                │
│  │ Redis      :6379 │   │  │ Transcoder       │                │
│  └──────────────────┘   │  └──────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
wsoptv/
├── docker-compose.yml          # Docker 서비스 정의
├── .env                        # 환경 변수 (gitignore)
├── CLAUDE.md                   # 이 문서
│
├── backend/                    # FastAPI 백엔드
│   ├── Dockerfile
│   ├── Dockerfile.migrator     # SQLite → PostgreSQL 마이그레이션
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── api/v1/             # API 엔드포인트
│       ├── core/               # 설정, 보안, DB
│       ├── models/             # SQLAlchemy 모델
│       └── services/           # 비즈니스 로직
│
├── frontend/                   # SvelteKit 프론트엔드
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── routes/             # 페이지 라우트
│       ├── lib/components/     # Svelte 컴포넌트
│       └── lib/stores/         # 상태 관리
│
├── docker/                     # Docker 설정 파일
│   └── postgres/
│       └── init.sql            # PostgreSQL 초기화 스키마
│
└── docs/
    └── prds/
        └── 0001-prd-wsoptv-platform.md
```

---

## Quick Start

```powershell
# 1. NAS 마운트 (Windows)
net use Z: \\10.10.100.122\GGPNAs\ARCHIVE /persistent:yes

# 2. 환경 변수 설정
cp .env.example .env
# POSTGRES_PASSWORD, MEILI_MASTER_KEY 설정

# 3. Docker 서비스 시작
docker compose up -d

# 4. 최초 데이터 마이그레이션 (pokervod.db → PostgreSQL)
docker compose --profile migrate up migrator

# 5. 서비스 확인
# Frontend: http://localhost:3000
# Backend:  http://localhost:8001/docs
# MeiliSearch: http://localhost:7700
```

---

## Development Commands

### Docker

```powershell
docker compose up -d              # 전체 서비스 시작
docker compose logs -f backend    # 백엔드 로그
docker compose restart backend    # 백엔드 재시작
docker compose down               # 전체 중지
docker compose down -v            # 볼륨 포함 삭제 (주의!)
```

### Database

```powershell
# PostgreSQL 접속
docker exec -it wsoptv-postgres psql -U wsoptv -d wsoptv

# 마이그레이션 실행
docker compose --profile migrate up migrator

# 백업
docker run --rm -v wsoptv_postgres-data:/data -v ${PWD}:/backup alpine tar cvf /backup/postgres-backup.tar /data
```

### Backend (FastAPI)

```powershell
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001

# 테스트
pytest tests/ -v
```

### Frontend (SvelteKit)

```powershell
cd frontend
npm install
npm run dev                       # 개발 서버 (port 3000)
npm run build                     # 프로덕션 빌드
npm test                          # 테스트
```

---

## Docker Services

| Service | Container | Port | IP | 역할 |
|---------|-----------|------|-----|------|
| postgres | wsoptv-postgres | 5432 | 172.28.1.1 | Primary DB |
| meilisearch | wsoptv-meili | 7700 | 172.28.1.2 | 전문 검색 |
| redis | wsoptv-redis | 6379 | 172.28.1.3 | 캐싱, 작업 큐 |
| backend | wsoptv-backend | 8001 | 172.28.2.1 | FastAPI |
| frontend | wsoptv-frontend | 3000 | 172.28.2.2 | SvelteKit |
| transcoder | wsoptv-transcoder | - | 172.28.2.3 | HLS 트랜스코딩 |

---

## Environment Variables

```env
# .env
POSTGRES_PASSWORD=your_secure_password
MEILI_MASTER_KEY=your_meili_key

# Google OAuth (Phase 2)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

---

## Database Schema

PostgreSQL 16 사용. 주요 테이블:

| Category | Tables |
|----------|--------|
| **Core** | catalogs, series, contents, files, players, hands |
| **Auth** | users, invitations, user_sessions |
| **User** | watch_progress, view_events, user_favorite_players |
| **Search** | (MeiliSearch 인덱스) |

상세 스키마: `docker/postgres/init.sql`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/catalogs` | 카탈로그 목록 |
| GET | `/api/v1/series/{id}` | 시리즈 상세 |
| GET | `/api/v1/contents/{id}` | 콘텐츠 상세 |
| GET | `/api/v1/contents/{id}/hands` | 핸드 목록 |
| GET | `/api/v1/search` | 검색 |
| GET | `/api/v1/stream/{id}` | HLS 스트리밍 |

API 문서: `http://localhost:8001/docs`

---

## Related Projects

| 프로젝트 | 경로 | 역할 |
|----------|------|------|
| archive-analyzer | `D:/AI/claude01/archive-analyzer` | NAS 스캔, 메타데이터 추출 |
| shared-data | `D:/AI/claude01/shared-data` | pokervod.db (원본) |

---

## Key Constraints

| 제약 | 설명 |
|------|------|
| **Docker 필수** | 모든 서비스는 Docker 컨테이너로 실행 |
| **NAS 마운트** | `/mnt/nas` (Linux) 또는 `Z:` (Windows) |
| **관리자 승인** | 회원가입 후 관리자 승인 필요 |
| **스트리밍 중계** | NAS → Frontend(중계) → 시청자 구조 |

---

## Documentation

| 문서 | 위치 |
|------|------|
| PRD | `docs/prds/0001-prd-wsoptv-platform.md` |
| API Docs | `http://localhost:8001/docs` |
| DB Schema | `docker/postgres/init.sql` |
