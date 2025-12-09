# WSOPTV 전체 앱 구축 태스크

**Version**: 1.0.0
**Created**: 2025-12-09
**Status**: In Progress
**Related PRD**: `docs/prds/0001-prd-wsoptv-platform.md`

---

## 📊 Progress Overview

```
Phase 0: 프로젝트 설정        ████████████████████ 100% (4/4)
Phase 1: Backend 구축         ░░░░░░░░░░░░░░░░░░░░   0% (0/8)
Phase 2: Frontend 페이지      ████████░░░░░░░░░░░░  40% (4/10)
Phase 3: 통합 & 스트리밍      ░░░░░░░░░░░░░░░░░░░░   0% (0/6)
Phase 4: 테스트 & QA          ░░░░░░░░░░░░░░░░░░░░   0% (0/5)
Phase 5: 배포 & DevOps        ░░░░░░░░░░░░░░░░░░░░   0% (0/4)
─────────────────────────────────────────────────────
Total:                        ████░░░░░░░░░░░░░░░░  22% (8/37)
```

---

## Phase 0: 프로젝트 설정 ✅

### Task 0.1: 문서화 ✅
- [x] PRD 작성 (`docs/prds/0001-prd-wsoptv-platform.md`)
- [x] LLD 문서 작성 (5개 파일)
- [x] CLAUDE.md 프로젝트 가이드

### Task 0.2: 프론트엔드 기본 설정 ✅
- [x] SvelteKit 프로젝트 초기화 (`apps/web/`)
- [x] TypeScript, Vite, ESLint 설정
- [x] Path aliases 설정 ($features, $shared)

### Task 0.3: Block Agent System ✅
- [x] Agent 구조 설계 (`docs/architecture/0001-block-agent-system.md`)
- [x] AGENT_RULES.md 작성 (auth, content, search, player)
- [x] Orchestrator agent 설정

### Task 0.4: 프론트엔드 도메인 기능 ✅
- [x] Auth 도메인 (API, Store, Hooks, Components)
- [x] Content 도메인 (API, Store, Hooks, Components)
- [x] Search 도메인 (API, Store, Hooks, Components)
- [x] Player 도메인 (API, Store, Hooks, Components)
- [x] Shared UI (Button, Input, Card, Spinner)

---

## Phase 1: Backend 구축 🔴

### Task 1.1: 프로젝트 구조 [ ]
**Priority**: P0 | **Estimate**: 2h
- [ ] FastAPI 프로젝트 초기화 (`backend/`)
- [ ] 디렉토리 구조 설정 (api, core, models, services)
- [ ] requirements.txt 작성
- [ ] Dockerfile 작성

### Task 1.2: 데이터베이스 설정 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] SQLAlchemy 모델 정의
  - [ ] User, UserSession
  - [ ] Catalog, Series, Content, File
  - [ ] Player, Hand, HandPlayer
  - [ ] WatchProgress, ViewEvent
- [ ] Alembic 마이그레이션 설정
- [ ] PostgreSQL 초기 스키마 (`docker/postgres/init.sql`)

### Task 1.3: 인증 API [ ]
**Priority**: P0 | **Estimate**: 4h
- [ ] POST `/api/v1/auth/register` - 회원가입
- [ ] POST `/api/v1/auth/login` - 로그인
- [ ] POST `/api/v1/auth/refresh` - 토큰 갱신
- [ ] POST `/api/v1/auth/logout` - 로그아웃
- [ ] GET `/api/v1/auth/me` - 현재 사용자
- [ ] JWT 토큰 관리 (access + refresh)
- [ ] 비밀번호 해싱 (bcrypt)

### Task 1.4: 콘텐츠 API [ ]
**Priority**: P0 | **Estimate**: 4h
- [ ] GET `/api/v1/catalogs` - 카탈로그 목록
- [ ] GET `/api/v1/catalogs/{id}` - 카탈로그 상세
- [ ] GET `/api/v1/series/{id}` - 시리즈 상세
- [ ] GET `/api/v1/contents` - 콘텐츠 목록 (페이지네이션)
- [ ] GET `/api/v1/contents/{id}` - 콘텐츠 상세
- [ ] GET `/api/v1/contents/{id}/hands` - 핸드 목록
- [ ] GET `/api/v1/players` - 플레이어 목록

### Task 1.5: 검색 API [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] MeiliSearch 클라이언트 설정
- [ ] 인덱스 생성 (contents, players, hands)
- [ ] GET `/api/v1/search` - 통합 검색
- [ ] GET `/api/v1/search/suggest` - 자동완성
- [ ] 패싯 필터링 (catalog, player, grade, year)

### Task 1.6: 스트리밍 API [ ]
**Priority**: P0 | **Estimate**: 5h
- [ ] GET `/api/v1/stream/{content_id}/manifest.m3u8` - HLS 매니페스트
- [ ] GET `/api/v1/stream/{content_id}/{segment}.ts` - HLS 세그먼트
- [ ] FFmpeg HLS 트랜스먹싱 서비스
- [ ] 세그먼트 캐싱 (Redis)
- [ ] 품질 옵션 (360p, 480p, 720p, 1080p)

### Task 1.7: 사용자 데이터 API [ ]
**Priority**: P1 | **Estimate**: 3h
- [ ] POST `/api/v1/watch-progress` - 시청 진행 저장
- [ ] GET `/api/v1/watch-progress/{content_id}` - 시청 진행 조회
- [ ] POST `/api/v1/events` - 이벤트 트래킹
- [ ] GET `/api/v1/history` - 시청 기록

### Task 1.8: 데이터 마이그레이션 [ ]
**Priority**: P0 | **Estimate**: 2h
- [ ] pokervod.db → PostgreSQL 마이그레이션 스크립트
- [ ] Dockerfile.migrator 작성
- [ ] MeiliSearch 인덱싱 스크립트

---

## Phase 2: Frontend 페이지 🟡

### Task 2.1: 레이아웃 & 네비게이션 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] 메인 레이아웃 (`+layout.svelte`)
- [ ] Header 컴포넌트 (로고, 검색, 사용자 메뉴)
- [ ] Sidebar/Navigation 컴포넌트
- [ ] Footer 컴포넌트
- [ ] 반응형 디자인 (mobile, tablet, desktop)

### Task 2.2: 인증 페이지 [ ]
**Priority**: P0 | **Estimate**: 2h
- [ ] `/login` - 로그인 페이지
- [ ] `/register` - 회원가입 페이지
- [ ] 인증 가드 (ProtectedRoute)
- [ ] 인증 상태 유지 (localStorage + refresh)

### Task 2.3: 홈 & 브라우징 페이지 [ ]
**Priority**: P0 | **Estimate**: 4h
- [ ] `/` - 홈 페이지 (추천, 최신, 인기)
- [ ] `/browse` - 브라우징 페이지
- [ ] `/catalog/[id]` - 카탈로그 상세
- [ ] `/series/[id]` - 시리즈 상세
- [ ] Infinite scroll 구현

### Task 2.4: 검색 페이지 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] `/search` - 검색 결과 페이지
- [ ] 검색 필터 UI (사이드바)
- [ ] 패싯 필터링 연동
- [ ] 검색 결과 하이라이팅

### Task 2.5: 콘텐츠 상세 페이지 [ ]
**Priority**: P0 | **Estimate**: 4h
- [ ] `/watch/[id]` - 시청 페이지
- [ ] 비디오 플레이어 통합
- [ ] 핸드 타임라인 연동
- [ ] 핸드 목록 사이드바
- [ ] 핸드 스킵 (이전/다음)

### Task 2.6: 플레이어 기능 강화 [ ]
**Priority**: P1 | **Estimate**: 4h
- [ ] 키보드 단축키 (스페이스, 방향키, N/P)
- [ ] 품질 선택 UI
- [ ] 재생 속도 조절
- [ ] PIP (Picture-in-Picture) 모드
- [ ] 전체화면 지원

### Task 2.7: 사용자 페이지 [ ]
**Priority**: P1 | **Estimate**: 3h
- [ ] `/profile` - 프로필 페이지
- [ ] `/history` - 시청 기록
- [ ] `/favorites` - 즐겨찾기
- [ ] 설정 (언어, 품질 기본값)

### Task 2.8: 플레이어 상세 페이지 [ ]
**Priority**: P2 | **Estimate**: 2h
- [ ] `/player/[id]` - 플레이어 프로필
- [ ] 플레이어 통계 (핸드 수, 승률)
- [ ] 관련 콘텐츠 목록

### Task 2.9: 관리자 페이지 [ ]
**Priority**: P2 | **Estimate**: 4h
- [ ] `/admin` - 관리자 대시보드
- [ ] `/admin/users` - 사용자 관리 (승인/거부)
- [ ] `/admin/content` - 콘텐츠 관리
- [ ] `/admin/invitations` - 초대 코드 관리

### Task 2.10: 에러 & 상태 페이지 [ ]
**Priority**: P1 | **Estimate**: 1h
- [ ] `/error` - 에러 페이지 (404, 500)
- [ ] 로딩 스켈레톤
- [ ] Empty states

---

## Phase 3: 통합 & 스트리밍 🔴

### Task 3.1: Docker 환경 구성 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] `docker-compose.yml` 작성
- [ ] 서비스 네트워크 설정 (wsoptv-network)
- [ ] 볼륨 설정 (postgres, meili, redis, hls)
- [ ] NAS 마운트 설정

### Task 3.2: API 통합 [ ]
**Priority**: P0 | **Estimate**: 2h
- [ ] Frontend API 클라이언트 연동
- [ ] API 에러 핸들링
- [ ] 인터셉터 설정 (토큰 갱신)
- [ ] 환경변수 관리 (.env)

### Task 3.3: HLS 스트리밍 통합 [ ]
**Priority**: P0 | **Estimate**: 4h
- [ ] Transcoder 서비스 구현
- [ ] On-demand HLS 변환
- [ ] 세그먼트 캐싱 전략
- [ ] 품질 적응 (ABR)

### Task 3.4: 실시간 기능 [ ]
**Priority**: P2 | **Estimate**: 3h
- [ ] WebSocket 연결 (시청자 수)
- [ ] 실시간 알림
- [ ] 트랜스코딩 진행률

### Task 3.5: 캐싱 전략 [ ]
**Priority**: P1 | **Estimate**: 2h
- [ ] Redis 캐시 레이어
- [ ] API 응답 캐싱
- [ ] MeiliSearch 결과 캐싱
- [ ] CDN 연동 준비

### Task 3.6: 보안 강화 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] CORS 설정
- [ ] Rate limiting
- [ ] 입력 검증 (Zod/Pydantic)
- [ ] SQL Injection 방지
- [ ] XSS 방지

---

## Phase 4: 테스트 & QA 🔴

### Task 4.1: Backend 단위 테스트 [ ]
**Priority**: P1 | **Estimate**: 4h
- [ ] API 엔드포인트 테스트
- [ ] 서비스 레이어 테스트
- [ ] 인증 로직 테스트
- [ ] pytest 설정

### Task 4.2: Frontend 단위 테스트 [ ]
**Priority**: P1 | **Estimate**: 3h
- [ ] 컴포넌트 테스트 (Vitest)
- [ ] Store 테스트
- [ ] Hook 테스트

### Task 4.3: E2E 테스트 [ ]
**Priority**: P1 | **Estimate**: 4h
- [ ] 인증 플로우 테스트
- [ ] 검색 플로우 테스트
- [ ] 시청 플로우 테스트
- [ ] Playwright 설정

### Task 4.4: 성능 테스트 [ ]
**Priority**: P2 | **Estimate**: 2h
- [ ] Lighthouse 점수
- [ ] Core Web Vitals
- [ ] 스트리밍 버퍼링 테스트
- [ ] 동시 접속 테스트

### Task 4.5: 접근성 테스트 [ ]
**Priority**: P2 | **Estimate**: 2h
- [ ] ARIA 속성 검증
- [ ] 키보드 네비게이션
- [ ] 스크린 리더 호환성

---

## Phase 5: 배포 & DevOps 🔴

### Task 5.1: CI/CD 파이프라인 [ ]
**Priority**: P1 | **Estimate**: 3h
- [ ] GitHub Actions 워크플로우
- [ ] 자동 테스트
- [ ] Docker 이미지 빌드
- [ ] 자동 배포

### Task 5.2: 모니터링 [ ]
**Priority**: P2 | **Estimate**: 2h
- [ ] 로깅 설정 (structured logs)
- [ ] 에러 트래킹 (Sentry)
- [ ] 메트릭 수집
- [ ] 알림 설정

### Task 5.3: 백업 & 복구 [ ]
**Priority**: P1 | **Estimate**: 2h
- [ ] PostgreSQL 백업 스크립트
- [ ] 볼륨 백업 전략
- [ ] 복구 프로세스 문서화

### Task 5.4: 프로덕션 배포 [ ]
**Priority**: P0 | **Estimate**: 3h
- [ ] 프로덕션 환경 설정
- [ ] SSL/TLS 인증서
- [ ] 도메인 설정
- [ ] 최종 배포

---

## 우선순위 범례

| 우선순위 | 설명 |
|----------|------|
| **P0** | MVP 필수 - 반드시 완료해야 함 |
| **P1** | 중요 - MVP 직후 구현 |
| **P2** | 선택 - 시간 여유 시 구현 |

---

## 다음 단계 (Recommended Order)

1. **Phase 1.1-1.2**: Backend 프로젝트 구조 + DB 설정
2. **Phase 3.1**: Docker 환경 구성
3. **Phase 1.3-1.5**: 핵심 API (인증, 콘텐츠, 검색)
4. **Phase 2.1-2.5**: Frontend 핵심 페이지
5. **Phase 1.6 + 3.3**: HLS 스트리밍
6. **Phase 4**: 테스트
7. **Phase 5**: 배포

---

## 관련 문서

- [PRD](../prds/0001-prd-wsoptv-platform.md)
- [LLD Master](../lld/0001-lld-wsoptv-platform.md)
- [LLD Modules](../lld/0002-lld-modules.md)
- [LLD API](../lld/0003-lld-api.md)
- [LLD Components](../lld/0004-lld-components.md)
- [LLD Flows](../lld/0005-lld-flows.md)
