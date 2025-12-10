# Task 0003: 동적 카탈로그 시스템 구현

**PRD**: `docs/prds/0003-prd-dynamic-catalog-system.md`
**Architecture**: `docs/architecture/0002-netflix-dynamic-catalog-system.md`
**Status**: Draft
**Created**: 2025-12-10

---

## Overview

Netflix 스타일의 동적 Row 기반 홈페이지 구현 태스크입니다.

---

## Phase 1: Core API (Week 1)

### 1.1 Backend - Row API

- [ ] **1.1.1** `RowService` 클래스 생성
  - 파일: `backend/src/services/row_service.py`
  - 메서드: `get_homepage_rows(user_id: int | None) -> list[RowData]`
  - 의존성: `JellyfinService`

- [ ] **1.1.2** `GET /api/v1/home` 엔드포인트
  - 파일: `backend/src/api/v1/home.py`
  - 라우터 등록: `backend/src/main.py`
  - 응답 스키마: `RowData[]`

- [ ] **1.1.3** Row 스키마 정의
  - 파일: `backend/src/schemas/row.py`
  - 타입: `RowConfig`, `RowData`, `RowItem`, `RowFilter`

- [ ] **1.1.4** `recently_added` Row 구현
  - Jellyfin API: `get_contents(sort_by="DateCreated", sort_order="desc")`
  - 캐시 TTL: 5분

- [ ] **1.1.5** `library` Row 구현 (동적)
  - Jellyfin API: `get_libraries()`
  - 각 라이브러리별 Row 자동 생성
  - 캐시 TTL: 5분

### 1.2 Backend - Jellyfin 연동

- [ ] **1.2.1** `JellyfinService.get_libraries()` 메서드
  - 파일: `backend/src/services/jellyfin.py`
  - 반환: `list[Library]`

- [ ] **1.2.2** `JellyfinService.get_contents()` 필터 확장
  - 파라미터: `library_id`, `sort_by`, `sort_order`
  - 기존 메서드 확장

### 1.3 Backend - 캐싱

- [ ] **1.3.1** Row 캐시 키 정의
  - `wsoptv:home:rows` (전체 Row, 5분)
  - `wsoptv:home:library:{id}` (라이브러리별, 5분)

- [ ] **1.3.2** Redis 캐시 구현
  - 파일: `backend/src/services/cache.py`
  - 데코레이터: `@cached(ttl=300)`

---

## Phase 2: Frontend UI (Week 2)

### 2.1 홈페이지 컴포넌트

- [ ] **2.1.1** `HomePage.svelte` 구현
  - 파일: `frontend/src/routes/+page.svelte`
  - API 호출: `GET /api/v1/home`
  - Row 렌더링 루프

- [ ] **2.1.2** `ContentRow.svelte` 컴포넌트
  - 파일: `frontend/src/lib/components/home/ContentRow.svelte`
  - Props: `row: RowData`
  - 가로 스크롤 + 스냅

- [ ] **2.1.3** `ContentCard.svelte` 컴포넌트
  - 파일: `frontend/src/lib/components/home/ContentCard.svelte`
  - Props: `item: RowItem`
  - 썸네일 + 진행률 바 + 정보

- [ ] **2.1.4** `RowSkeleton.svelte` 로딩 스켈레톤
  - 파일: `frontend/src/lib/components/home/RowSkeleton.svelte`
  - Row 로딩 상태 표시

### 2.2 API 클라이언트

- [ ] **2.2.1** Home API 함수
  - 파일: `frontend/src/lib/api/home.ts`
  - 함수: `fetchHomeRows(): Promise<RowData[]>`

- [ ] **2.2.2** Row 타입 정의
  - 파일: `frontend/src/lib/types/row.ts`
  - 타입: `RowData`, `RowItem`, `RowType`

### 2.3 스타일링

- [ ] **2.3.1** 가로 스크롤 스타일
  - `overflow-x: auto`
  - `scroll-snap-type: x mandatory`
  - 스크롤바 숨김/스타일링

- [ ] **2.3.2** 카드 호버 효과
  - Scale transform
  - 그림자 효과
  - 정보 오버레이

---

## Phase 3: Browse & Personalization (Week 3)

### 3.1 Browse API

- [ ] **3.1.1** `GET /api/v1/browse` 엔드포인트
  - 파일: `backend/src/api/v1/browse.py`
  - Query: `library`, `sort`, `page`, `limit`
  - 페이지네이션 응답

- [ ] **3.1.2** Browse 스키마
  - 파일: `backend/src/schemas/browse.py`
  - 타입: `BrowseParams`, `BrowseResponse`

### 3.2 Browse UI

- [ ] **3.2.1** `BrowsePage.svelte` 구현
  - 파일: `frontend/src/routes/browse/+page.svelte`
  - 그리드 레이아웃
  - 필터 사이드바

- [ ] **3.2.2** `FilterBar.svelte` 컴포넌트
  - 파일: `frontend/src/lib/components/browse/FilterBar.svelte`
  - 라이브러리 필터
  - 정렬 옵션

- [ ] **3.2.3** `ContentGrid.svelte` 컴포넌트
  - 파일: `frontend/src/lib/components/browse/ContentGrid.svelte`
  - 반응형 그리드
  - 무한 스크롤

### 3.3 Continue Watching

- [ ] **3.3.1** `continue_watching` Row 구현
  - 파일: `backend/src/services/row_service.py`
  - DB: `watch_progress` 테이블 조회
  - 사용자 인증 필요

- [ ] **3.3.2** 진행률 API
  - `POST /api/v1/watch/{id}/progress`
  - 파일: `backend/src/api/v1/watch.py`

### 3.4 Trending Row

- [ ] **3.4.1** `trending` Row 구현
  - 파일: `backend/src/services/row_service.py`
  - DB: `view_events` 테이블 (최근 7일)
  - 캐시 TTL: 1시간

---

## Phase 4: Cleanup & Testing (Week 4)

### 4.1 코드 정리

- [ ] **4.1.1** 기존 카탈로그 API 비활성화
  - 파일: `backend/src/main.py`
  - `catalogs` 라우터 주석 처리 (이미 완료됨)

- [ ] **4.1.2** Frontend 기존 카탈로그 코드 제거
  - `frontend/src/lib/api/content.ts` 정리

### 4.2 테스트

- [ ] **4.2.1** Backend 단위 테스트
  - 파일: `backend/tests/test_row_service.py`
  - `RowService` 메서드 테스트

- [ ] **4.2.2** API 통합 테스트
  - 파일: `backend/tests/test_home_api.py`
  - `/api/v1/home` 응답 검증

- [ ] **4.2.3** E2E 테스트
  - 파일: `apps/web/e2e/specs/home/home.spec.ts`
  - 홈페이지 Row 렌더링 테스트
  - 카드 클릭 네비게이션 테스트

### 4.3 문서 업데이트

- [ ] **4.3.1** API 문서 업데이트
  - 파일: `docs/lld/0003-lld-api.md`
  - `/api/v1/home`, `/api/v1/browse` 추가

- [ ] **4.3.2** LLD 업데이트
  - 파일: `docs/lld/0001-lld-wsoptv-platform.md`
  - 홈페이지 아키텍처 반영

---

## Dependencies

### 신규 패키지
- 없음 (기존 스택 활용)

### 기존 코드 수정
| 파일 | 변경 내용 |
|------|----------|
| `backend/src/main.py` | home 라우터 등록 |
| `frontend/src/routes/+page.svelte` | 홈페이지 전면 재작성 |

---

## Acceptance Criteria

### Phase 1 완료 조건
- [ ] `/api/v1/home` API가 Row 데이터 반환
- [ ] Jellyfin 라이브러리별 Row 자동 생성
- [ ] Redis 캐시 적용

### Phase 2 완료 조건
- [ ] 홈페이지에 Row가 렌더링됨
- [ ] 가로 스크롤 + 스냅 동작
- [ ] 카드 클릭 시 `/watch/{id}`로 이동

### Phase 3 완료 조건
- [ ] Browse 페이지 필터링 동작
- [ ] Continue Watching Row 표시 (로그인 사용자)
- [ ] Trending Row 표시

### Phase 4 완료 조건
- [ ] E2E 테스트 통과
- [ ] 문서 업데이트 완료
- [ ] 홈페이지 LCP < 2s

---

## Notes

- 기존 `catalogs`, `series` 테이블은 **삭제하지 않고 유지** (마이그레이션 데이터 보존)
- Jellyfin API 호출은 캐싱 필수 (과부하 방지)
- Continue Watching은 로그인 사용자만 표시
