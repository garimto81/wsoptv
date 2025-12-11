# PRD: 동적 카탈로그 시스템 (Netflix-Style)

**Version**: 1.0.0
**Date**: 2025-12-10
**Author**: Claude Code
**Status**: Draft
**Related**: `docs/architecture/0002-netflix-dynamic-catalog-system.md`

---

## 1. Executive Summary

WSOPTV의 홈페이지를 **Netflix 스타일의 동적 Row 기반 단일 페이지**로 구현합니다. 기존 정적 카탈로그(Catalog → Series → Content)를 **Jellyfin 라이브러리 기반 동적 Row 시스템**으로 전환하여 사용자 경험을 개선합니다.

### 1.1 핵심 변경점

| 항목 | 기존 | 신규 |
|------|------|------|
| **홈페이지 구조** | 고정 카탈로그 목록 | 동적 Row 기반 단일 페이지 |
| **콘텐츠 계층** | Catalog → Series → Content (3단계) | Content + Tags (평면 + 메타데이터) |
| **카탈로그 저장** | PostgreSQL `catalogs` 테이블 | **저장 안 함** (런타임 생성) |
| **네비게이션** | 카탈로그 → 시리즈 → 콘텐츠 | 홈 Row → 콘텐츠 상세 (2단계) |
| **데이터 소스** | PostgreSQL 테이블 | Jellyfin API 실시간 호출 |

### 1.2 목표

- **사용자 경험**: 스크롤만으로 모든 콘텐츠 탐색
- **개인화**: Continue Watching, Trending 등 동적 Row
- **확장성**: 새 라이브러리 추가 시 자동 Row 생성
- **유지보수**: Jellyfin이 카탈로그 역할을 대체 (중복 관리 제거)

---

## 2. Problem Statement

### 2.1 현재 문제점

1. **정적 카탈로그의 한계**
   - PostgreSQL에 미리 저장된 `catalog_title` 기반
   - 새 라이브러리 추가 시 DB 업데이트 필요
   - Jellyfin과 이중 관리 발생

2. **사용자 경험 저하**
   - 3단계 네비게이션 (홈 → 카탈로그 → 시리즈 → 콘텐츠)
   - 개인화 Row 없음 (Continue Watching, 추천 등)
   - 새 콘텐츠 발견 어려움

3. **기술적 비효율**
   - Jellyfin에 이미 라이브러리 구조 존재
   - PostgreSQL `catalogs`, `series` 테이블 중복
   - 스캔 → DB 저장 → 조회 파이프라인 복잡

### 2.2 기대 효과

| 항목 | 현재 | 목표 |
|------|------|------|
| 콘텐츠 접근 단계 | 3단계 | **2단계** |
| 새 라이브러리 반영 | 수동 (DB 업데이트) | **자동** (Jellyfin 즉시 반영) |
| 개인화 Row | 없음 | **4종** (Continue, Recent, Trending, Recommended) |
| DB 테이블 | catalogs, series 필요 | **불필요** (삭제 가능) |

---

## 3. Solution Overview

### 3.1 동적 Row 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WSOPTV Homepage                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Continue Watching ───────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Recently Added ──────────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ WSOP (Library) ─────────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ HCL (Library) ──────────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Trending Now ───────────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 플로우

```
Frontend                    Backend                      Jellyfin
   │                           │                            │
   │  GET /api/v1/home         │                            │
   │ ─────────────────────────▶│                            │
   │                           │                            │
   │                           │  RowService.get_homepage_rows()
   │                           │  ┌────────────────────────┐│
   │                           │  │ 1. Continue Watching   ││
   │                           │  │    → PostgreSQL        ││
   │                           │  │                        ││
   │                           │  │ 2. Recently Added      ││
   │                           │  │    → Jellyfin API ─────┼┼──▶ Items
   │                           │  │                        ││
   │                           │  │ 3. For each Library    ││
   │                           │  │    → Jellyfin API ─────┼┼──▶ Libraries
   │                           │  │                        ││
   │                           │  │ 4. Trending            ││
   │                           │  │    → PostgreSQL        ││
   │                           │  └────────────────────────┘│
   │                           │                            │
   │◀───────────────────────── │  { rows: [...] }          │
   │  RowData[]                │                            │
```

### 3.3 Row 타입 정의

| Row Type | 데이터 소스 | 정렬 기준 | 예시 |
|----------|------------|----------|------|
| `continue_watching` | PostgreSQL watch_history | Last watched (desc) | "Continue Watching" |
| `recently_added` | Jellyfin DateCreated | DateCreated (desc) | "Recently Added" |
| `library` | Jellyfin Library ID | DateCreated (desc) | "WSOP", "HCL", "PAD" |
| `trending` | PostgreSQL view_count (7d) | Views (desc) | "Trending Now" |
| `top_rated` | PostgreSQL hand grade S/A | Grade + views | "Top Rated Hands" |
| `tag` | Content tags | Popularity | "High Stakes", "All-In" |
| `player` | Hand players | Appearance count | "Phil Ivey Collection" |

---

## 4. Functional Requirements

### 4.1 FR-1: Homepage Row API

**Priority**: P0 (필수)

#### 4.1.1 GET /api/v1/home

홈페이지에 표시할 모든 Row를 반환합니다.

**Request:**
```
GET /api/v1/home
Authorization: Bearer {token}  (선택, Continue Watching용)
```

**Response:**
```json
{
  "data": {
    "rows": [
      {
        "id": "continue_watching",
        "type": "continue_watching",
        "title": "Continue Watching",
        "items": [
          {
            "id": "abc123",
            "title": "WSOP 2024 Main Event Day 1",
            "thumbnailUrl": "/thumbnails/abc123.jpg",
            "duration": 7200,
            "progress": 45,
            "libraryName": "WSOP"
          }
        ],
        "viewAllUrl": "/history"
      },
      {
        "id": "recently_added",
        "type": "recently_added",
        "title": "Recently Added",
        "items": [...],
        "viewAllUrl": "/browse?sort=recent"
      },
      {
        "id": "library_wsop",
        "type": "library",
        "title": "WSOP",
        "items": [...],
        "filter": {"libraryId": "abc123"},
        "viewAllUrl": "/browse?library=abc123"
      }
    ]
  }
}
```

#### 4.1.2 RowService 구현

```python
class RowService:
    """동적 Row 생성 서비스"""

    async def get_homepage_rows(self, user_id: int | None = None) -> list[RowData]:
        rows = []

        # 1. Continue Watching (로그인 사용자만)
        if user_id:
            rows.append(await self._get_continue_watching(user_id))

        # 2. Recently Added
        rows.append(await self._get_recently_added())

        # 3. Library Rows (Jellyfin)
        libraries = await self.jellyfin.get_libraries()
        for lib in libraries:
            rows.append(await self._get_library_row(lib.id, lib.name))

        # 4. Trending
        rows.append(await self._get_trending())

        return [row for row in rows if row.items]  # 빈 Row 제외
```

### 4.2 FR-2: Browse API (View All)

**Priority**: P0 (필수)

#### 4.2.1 GET /api/v1/browse

필터/정렬이 적용된 콘텐츠 목록을 반환합니다.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `library` | string | Jellyfin Library ID |
| `tag` | string | Tag filter |
| `player` | number | Player ID |
| `sort` | string | recent, popular, title |
| `page` | number | Page number (default: 1) |
| `limit` | number | Items per page (default: 20) |

**Response:**
```json
{
  "data": {
    "items": [...],
    "total": 150,
    "page": 1,
    "limit": 20,
    "hasNext": true,
    "filters": {
      "library": {"id": "abc123", "name": "WSOP"},
      "appliedFilters": ["library"]
    }
  }
}
```

### 4.3 FR-3: Continue Watching

**Priority**: P1 (중요)

사용자의 시청 진행 상황을 추적하고 이어보기 기능을 제공합니다.

#### 4.3.1 PostgreSQL 테이블 (기존 활용)

```sql
-- 기존 watch_progress 테이블 활용
CREATE TABLE watch_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content_id VARCHAR(100) NOT NULL,  -- Jellyfin Item ID
    progress_sec INTEGER NOT NULL,
    duration_sec INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.3.2 API

```
POST /api/v1/watch/{item_id}/progress
{
  "progress_sec": 1800,
  "duration_sec": 7200
}
```

### 4.4 FR-4: Trending Row

**Priority**: P2 (보통)

최근 7일간 조회수 기반 인기 콘텐츠를 표시합니다.

#### 4.4.1 PostgreSQL 테이블 (기존 활용)

```sql
-- 기존 view_events 테이블 활용
SELECT content_id, COUNT(*) as view_count
FROM view_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY content_id
ORDER BY view_count DESC
LIMIT 20;
```

---

## 5. Non-Functional Requirements

### 5.1 NFR-1: 성능

| 메트릭 | 목표 |
|--------|------|
| `/api/v1/home` 응답 시간 | < 500ms |
| Row당 캐시 TTL | 5분 |
| Jellyfin API 호출 | 캐시 적용 |
| 동시 사용자 | 100명 |

### 5.2 NFR-2: 캐싱

```python
CACHE_CONFIG = {
    "home_rows": {
        "ttl": 300,  # 5분
        "key": "wsoptv:home:rows"
    },
    "library_row": {
        "ttl": 300,  # 5분
        "key": "wsoptv:home:library:{id}"
    },
    "trending": {
        "ttl": 3600,  # 1시간
        "key": "wsoptv:home:trending"
    },
    "user_continue": {
        "ttl": 60,  # 1분
        "key": "wsoptv:user:{id}:continue"
    }
}
```

### 5.3 NFR-3: 확장성

- 새 Jellyfin 라이브러리 추가 시 자동 Row 생성
- Row 순서/활성화 여부 설정 가능 (Admin)
- 새 Row 타입 추가 용이 (플러그인 아키텍처)

---

## 6. User Interface

### 6.1 홈페이지 (/)

**컴포넌트 구조:**
```
src/lib/components/
├── home/
│   ├── HomePage.svelte          # 홈페이지 메인
│   ├── ContentRow.svelte        # 동적 Row 컴포넌트
│   ├── ContentCard.svelte       # Row 내 카드
│   └── RowSkeleton.svelte       # 로딩 스켈레톤
├── browse/
│   ├── BrowsePage.svelte        # View All 페이지
│   ├── FilterBar.svelte         # 필터 UI
│   └── ContentGrid.svelte       # 그리드 레이아웃
```

### 6.2 ContentRow 컴포넌트

```svelte
<section class="content-row">
  <div class="row-header">
    <h2>{row.title}</h2>
    {#if row.viewAllUrl}
      <a href={row.viewAllUrl}>View All →</a>
    {/if}
  </div>

  <div class="row-items">
    {#each row.items as item}
      <ContentCard {item} />
    {/each}
  </div>
</section>
```

### 6.3 ContentCard 컴포넌트

```svelte
<article class="content-card">
  <a href="/watch/{item.id}">
    <div class="thumbnail">
      <img src={item.thumbnailUrl} alt={item.title} />
      {#if item.progress}
        <div class="progress-bar" style="width: {item.progress}%" />
      {/if}
      <span class="duration">{formatDuration(item.duration)}</span>
    </div>
    <h3>{item.title}</h3>
    <span class="library">{item.libraryName}</span>
  </a>
</article>
```

---

## 7. URL Structure

| URL | 설명 |
|-----|------|
| `/` | 홈페이지 (동적 Row 목록) |
| `/browse` | 전체 브라우징 |
| `/browse?library={id}` | 라이브러리 필터 |
| `/browse?sort=recent` | 최신순 정렬 |
| `/watch/{id}` | 콘텐츠 재생 |
| `/history` | 시청 기록 |

---

## 8. Data Migration

### 8.1 삭제 대상 (선택)

기존 정적 카탈로그 관련 테이블은 **삭제 가능**합니다:

```sql
-- 삭제 대상 테이블 (옵션)
-- catalogs, series (Jellyfin이 대체)

-- 유지 테이블
-- users, watch_progress, view_events, hands, hand_players, players
```

### 8.2 Jellyfin Item ID 연결

기존 PostgreSQL의 `hands` 테이블은 Jellyfin Item ID로 연결합니다:

```sql
-- content_id를 Jellyfin Item ID로 변경
ALTER TABLE hands ADD COLUMN jellyfin_item_id VARCHAR(100);
UPDATE hands SET jellyfin_item_id = (
    SELECT file_id FROM files WHERE files.id = hands.file_id
);
```

---

## 9. Implementation Phases

### Phase 1: Core API (MVP)

**기간**: 1주

| 태스크 | 설명 | 우선순위 |
|--------|------|---------|
| 1.1 | `GET /api/v1/home` 엔드포인트 | P0 |
| 1.2 | `RowService` 구현 | P0 |
| 1.3 | Jellyfin 라이브러리 → Row 변환 | P0 |
| 1.4 | `recently_added` Row | P0 |
| 1.5 | Redis 캐싱 | P1 |

### Phase 2: Frontend UI

**기간**: 1주

| 태스크 | 설명 | 우선순위 |
|--------|------|---------|
| 2.1 | `HomePage.svelte` 구현 | P0 |
| 2.2 | `ContentRow.svelte` 구현 | P0 |
| 2.3 | `ContentCard.svelte` 구현 | P0 |
| 2.4 | 가로 스크롤 + 스냅 | P1 |
| 2.5 | `RowSkeleton.svelte` (로딩) | P1 |

### Phase 3: Browse & Personalization

**기간**: 1주

| 태스크 | 설명 | 우선순위 |
|--------|------|---------|
| 3.1 | `GET /api/v1/browse` 엔드포인트 | P0 |
| 3.2 | `BrowsePage.svelte` 구현 | P0 |
| 3.3 | Continue Watching Row | P1 |
| 3.4 | Trending Row | P2 |
| 3.5 | View All 페이지 | P1 |

### Phase 4: Cleanup & Optimization

**기간**: 1주

| 태스크 | 설명 | 우선순위 |
|--------|------|---------|
| 4.1 | 기존 정적 카탈로그 코드 제거 | P2 |
| 4.2 | E2E 테스트 | P0 |
| 4.3 | 성능 최적화 | P1 |
| 4.4 | 문서 업데이트 | P2 |

---

## 10. Success Metrics

| 메트릭 | 목표 | 측정 방법 |
|--------|------|----------|
| 홈페이지 로드 시간 | < 2s | Lighthouse LCP |
| API 응답 시간 | < 500ms | Backend 로그 |
| Row당 콘텐츠 클릭률 | > 5% | 이벤트 로그 |
| Continue Watching 사용률 | > 30% | 활성 사용자 대비 |

---

## 11. Risks & Mitigations

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| Jellyfin API 지연 | 홈페이지 로딩 지연 | Redis 캐싱 (5분 TTL) |
| Jellyfin 다운 | 홈페이지 표시 불가 | Fallback 정적 데이터 |
| 과도한 API 호출 | Jellyfin 부하 | 배치 요청 + 캐싱 |
| Row 순서 혼란 | UX 저하 | Admin 설정 UI 제공 |

---

## 12. Related Documents

| 문서 | 설명 |
|------|------|
| `docs/architecture/0002-netflix-dynamic-catalog-system.md` | 상세 아키텍처 설계 |
| `docs/prds/0001-prd-wsoptv-platform.md` | 플랫폼 PRD (수정 필요) |
| `docs/lld/0003-lld-api.md` | API 명세 (수정 필요) |
| `.claude/agents/content-domain.md` | 콘텐츠 도메인 에이전트 |

---

## 13. Appendix

### A. Row Configuration Schema

```typescript
interface RowConfig {
  id: string;
  type: RowType;
  title: string;
  filter?: RowFilter;
  sortBy?: SortField;
  sortOrder?: 'asc' | 'desc';
  limit: number;
  enabled: boolean;
  position: number;
}

interface RowFilter {
  libraryId?: string;
  tags?: string[];
  playerId?: number;
  handGrade?: HandGrade[];
  dateRange?: DateRange;
  userId?: number;
}

type RowType =
  | 'continue_watching'
  | 'recently_added'
  | 'library'
  | 'trending'
  | 'top_rated'
  | 'tag'
  | 'player'
  | 'custom';
```

### B. Row Item Schema

```typescript
interface RowItem {
  id: string;              // Jellyfin Item ID
  title: string;
  thumbnailUrl: string;
  duration: number;        // seconds
  year?: number;
  libraryName: string;
  progress?: number;       // 시청 진행률 (0-100)
  handCount?: number;
  topGrade?: HandGrade;
}
```

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-10 | Claude Code | Initial draft |
