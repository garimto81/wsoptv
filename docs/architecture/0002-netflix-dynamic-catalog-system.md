# Netflix 스타일 동적 카탈로그 시스템 설계서

**Version**: 2.0.0
**Date**: 2025-12-11
**Author**: Claude Code
**Status**: Updated (Hybrid Architecture)

> **⚠️ 업데이트**: v2.0.0에서 하이브리드 아키텍처로 전환
> - 기존: Jellyfin Libraries 기반 Row (5개)
> - 신규: PostgreSQL catalogs/series 기반 Row (24개) + Jellyfin enrichment
> - PRD: `docs/prds/0004-prd-hybrid-catalog-system.md`

---

## 1. Executive Summary

WSOPTV의 카탈로그 시스템을 Netflix 스타일의 **동적 Row 기반 단일 홈페이지**로 재설계합니다.

### 1.1 핵심 변경점

| 항목 | 기존 설계 | 새 설계 |
|------|----------|---------|
| **홈페이지 구조** | 고정 카탈로그 목록 나열 | 동적 Row 기반 단일 페이지 |
| **콘텐츠 계층** | Catalog → Series → Content (3단계) | Content + Tags (평면 + 메타데이터) |
| **카탈로그 개념** | 고정 엔티티 (WSOP, HCL) | 동적 필터/태그 (런타임 생성) |
| **네비게이션** | 카탈로그 선택 → 시리즈 → 콘텐츠 | 홈 Row → 콘텐츠 상세 (2단계) |
| **데이터 소스** | PostgreSQL catalogs 테이블 | Jellyfin Libraries + Tags |

### 1.2 Netflix 패턴 적용

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
│  ┌─ WSOP (Library Filter) ───────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ HCL (Library Filter) ────────────────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ High Stakes Hands (Tag Filter) ──────────────────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ Featured Players: Phil Ivey (Player Filter) ─────────────────────┐  │
│  │ [Card] [Card] [Card] [Card] [Card] →                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture

### 2.1 데이터 모델 (평면 구조)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Content-Centric Model                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐                                                         │
│  │   Content   │ ← 핵심 엔티티 (Jellyfin Item)                           │
│  │  - id       │                                                         │
│  │  - title    │     ┌──────────────┐                                    │
│  │  - duration │────▶│     Tags     │ ← 메타데이터 기반 분류              │
│  │  - created  │     │ - library    │   (WSOP, HCL, S-grade 등)          │
│  │  - ...      │     │ - player     │                                    │
│  └─────────────┘     │ - grade      │                                    │
│         │            │ - year       │                                    │
│         │            └──────────────┘                                    │
│         ▼                                                                 │
│  ┌─────────────┐                                                         │
│  │    Hands    │ ← 포커 특화 메타데이터                                   │
│  │ - timecode  │                                                         │
│  │ - players   │                                                         │
│  │ - grade     │                                                         │
│  └─────────────┘                                                         │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Row 시스템

#### Row Types (하이브리드 아키텍처)

| Row Type | 데이터 소스 | 정렬 기준 | 예시 | Feature Flag |
|----------|------------|----------|------|--------------|
| `continue_watching` | PostgreSQL watch_progress | Last watched (desc) | "Continue Watching" | 공통 |
| `recently_added` | Jellyfin DateCreated | DateCreated (desc) | "Recently Added" | 공통 |
| **`series`** | **PostgreSQL series** | **year (desc)** | **"WSOP Europe 2024"** | **USE_HYBRID_CATALOG=true** |
| `library` | Jellyfin Library ID | DateCreated (desc) | "WSOP", "HCL" | USE_HYBRID_CATALOG=false (레거시) |
| `tag` | Content tags | Popularity/Date | "High Stakes", "All-In" | 공통 |
| `player` | Hand players | Appearance count | "Phil Ivey", "Tom Dwan" | 공통 |
| `trending` | PostgreSQL view_events | Views (desc) | "Trending Now" | 공통 |
| `top_rated` | Hand grade S/A | Grade + views | "Top Rated Hands" | 공통 |

> **신규 (v2.0)**: `series` 타입 추가 - PostgreSQL `catalogs`/`series` 테이블 기반
> - WSOP 1개 폴더 → 16개 Series Row로 분리
> - PAD 1개 폴더 → 2개 Series Row (Season 12, 13)
> - 총 5개 Library → 24개 Series Row

#### Row Configuration

```typescript
interface RowConfig {
  id: string;
  type: RowType;
  title: string;
  filter: RowFilter;
  sortBy: SortField;
  sortOrder: 'asc' | 'desc';
  limit: number;
  enabled: boolean;
  position: number;  // 홈페이지 내 순서
}

interface RowFilter {
  libraryId?: string;      // Jellyfin Library UUID
  tags?: string[];         // 태그 필터
  playerId?: number;       // 플레이어 필터
  handGrade?: HandGrade[]; // 핸드 등급 필터
  dateRange?: DateRange;   // 날짜 범위
  userId?: number;         // 사용자별 (Continue Watching)
}

type RowType =
  | 'continue_watching'
  | 'recently_added'
  | 'library'
  | 'tag'
  | 'player'
  | 'trending'
  | 'top_rated'
  | 'custom';
```

### 2.3 Dynamic Row Generation

```python
# services/row_service.py

class RowService:
    """동적 Row 생성 서비스"""

    def __init__(self, jellyfin: JellyfinService):
        self.jellyfin = jellyfin

    async def get_homepage_rows(
        self,
        user_id: int | None = None
    ) -> list[RowData]:
        """홈페이지 Row 목록 생성"""
        rows = []

        # 1. Continue Watching (로그인 사용자만)
        if user_id:
            rows.append(await self._get_continue_watching(user_id))

        # 2. Recently Added (전체)
        rows.append(await self._get_recently_added())

        # 3. Library Rows (Jellyfin Libraries)
        libraries = await self.jellyfin.get_libraries()
        for lib in libraries:
            rows.append(await self._get_library_row(lib.id, lib.name))

        # 4. Tag-based Rows (설정된 태그들)
        for tag_config in self._get_tag_row_configs():
            rows.append(await self._get_tag_row(tag_config))

        # 5. Trending (조회수 기반)
        rows.append(await self._get_trending())

        return [row for row in rows if row.items]  # 빈 Row 제외

    async def _get_library_row(
        self,
        library_id: str,
        library_name: str
    ) -> RowData:
        """라이브러리 기반 Row"""
        contents = await self.jellyfin.get_contents(
            library_id=library_id,
            limit=20,
        )
        return RowData(
            id=f"library_{library_id}",
            type="library",
            title=library_name,
            items=contents.items,
            filter={"libraryId": library_id},
            viewAllUrl=f"/browse?library={library_id}",
        )
```

---

## 3. API Design

### 3.1 Homepage API

```
GET /api/v1/home
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
        "items": [...],
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
        "id": "library_abc123",
        "type": "library",
        "title": "WSOP",
        "items": [...],
        "filter": {"libraryId": "abc123"},
        "viewAllUrl": "/browse?library=abc123"
      },
      {
        "id": "library_def456",
        "type": "library",
        "title": "HCL",
        "items": [...],
        "filter": {"libraryId": "def456"},
        "viewAllUrl": "/browse?library=def456"
      }
    ]
  }
}
```

### 3.2 Browse API (View All)

```
GET /api/v1/browse
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `library` | string | Jellyfin Library ID |
| `tag` | string | Tag filter |
| `player` | number | Player ID |
| `grade` | string | Hand grade (S,A,B,C) |
| `sort` | string | recent, popular, title |
| `page` | number | Page number |
| `limit` | number | Items per page |

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

### 3.3 Row Item Schema

```typescript
interface RowItem {
  id: string;              // Jellyfin Item ID
  title: string;
  thumbnailUrl: string;
  duration: number;        // seconds
  year?: number;
  libraryName: string;     // 출처 라이브러리
  progress?: number;       // 시청 진행률 (0-100)
  handCount?: number;      // 핸드 수
  topGrade?: HandGrade;    // 최고 핸드 등급
}
```

---

## 4. Frontend Components

### 4.1 Component Structure

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
└── shared/
    └── LibrarySelector.svelte   # 라이브러리 필터 드롭다운
```

### 4.2 ContentRow Component

```svelte
<!-- ContentRow.svelte -->
<script lang="ts">
  import type { RowData } from '$lib/types';
  import ContentCard from './ContentCard.svelte';

  interface Props {
    row: RowData;
  }

  let { row }: Props = $props();
</script>

<section class="content-row">
  <div class="row-header">
    <h2 class="row-title">{row.title}</h2>
    {#if row.viewAllUrl}
      <a href={row.viewAllUrl} class="view-all">View All →</a>
    {/if}
  </div>

  <div class="row-items">
    {#each row.items as item (item.id)}
      <ContentCard {item} />
    {/each}
  </div>
</section>

<style>
  .content-row {
    margin-bottom: var(--spacing-xl);
  }

  .row-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
  }

  .row-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text);
  }

  .view-all {
    color: var(--color-primary);
    text-decoration: none;
    font-size: 0.875rem;
  }

  .row-items {
    display: flex;
    gap: var(--spacing-md);
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding-bottom: var(--spacing-sm);
  }

  .row-items::-webkit-scrollbar {
    height: 4px;
  }
</style>
```

### 4.3 HomePage Component

```svelte
<!-- HomePage.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import ContentRow from './ContentRow.svelte';
  import RowSkeleton from './RowSkeleton.svelte';
  import { api } from '$lib/api';
  import type { RowData } from '$lib/types';

  let rows = $state<RowData[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  onMount(async () => {
    try {
      const response = await api.get('/home');
      rows = response.data.rows;
    } catch (e) {
      error = 'Failed to load content';
    } finally {
      loading = false;
    }
  });
</script>

<main class="homepage">
  {#if loading}
    {#each Array(5) as _, i}
      <RowSkeleton />
    {/each}
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    {#each rows as row (row.id)}
      <ContentRow {row} />
    {/each}
  {/if}
</main>
```

---

## 5. Data Migration

### 5.1 Jellyfin Integration

기존 PostgreSQL 기반 카탈로그 시스템을 Jellyfin으로 전환:

| 기존 PostgreSQL | Jellyfin 대체 |
|----------------|---------------|
| `catalogs` 테이블 | Jellyfin Libraries |
| `series` 테이블 | Jellyfin Collections (선택) |
| `contents` 테이블 | Jellyfin Items |
| `files` 테이블 | Jellyfin MediaSources |

### 5.2 유지되는 PostgreSQL 테이블

```sql
-- 사용자 관련 (PostgreSQL 유지)
users, user_sessions, watch_history, bookmarks, favorites

-- 포커 특화 메타데이터 (PostgreSQL 유지)
hands, hand_players, players

-- 삭제 대상
catalogs, series, contents, files
```

### 5.3 핸드 데이터 연결

```sql
-- Jellyfin Item ID와 핸드 연결
CREATE TABLE content_hands (
    id SERIAL PRIMARY KEY,
    jellyfin_item_id VARCHAR(100) NOT NULL,  -- Jellyfin UUID
    hand_id INTEGER REFERENCES hands(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_content_hands_jellyfin ON content_hands(jellyfin_item_id);
```

---

## 6. URL Structure

### 6.1 라우팅

| URL | 설명 |
|-----|------|
| `/` | 홈페이지 (동적 Row 목록) |
| `/browse` | 전체 브라우징 |
| `/browse?library={id}` | 라이브러리 필터 |
| `/browse?tag={name}` | 태그 필터 |
| `/browse?player={id}` | 플레이어 필터 |
| `/watch/{id}` | 콘텐츠 재생 |
| `/search?q={query}` | 검색 결과 |

### 6.2 네비게이션 플로우

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Navigation Flow                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Home (/)                                                             │
│    │                                                                  │
│    ├── Click Card ──────────────────────▶ Watch (/watch/{id})        │
│    │                                                                  │
│    ├── Click "View All" ────────────────▶ Browse (/browse?...)       │
│    │                                         │                        │
│    │                                         └── Click Card ─▶ Watch │
│    │                                                                  │
│    └── Click Header Nav ────────────────▶ Browse (empty filter)      │
│                                                                       │
│  Header Navigation:                                                   │
│    [Home] [Browse ▼] [Search]                                        │
│             │                                                         │
│             ├── All Content                                           │
│             ├── WSOP (library filter)                                 │
│             ├── HCL (library filter)                                  │
│             └── PAD (library filter)                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 7. Configuration

### 7.1 Row 설정 (Admin)

```typescript
// 관리자가 설정 가능한 Row 구성
interface HomeRowConfig {
  rows: RowConfig[];
  defaultLimit: number;
  refreshInterval: number;  // 캐시 갱신 주기 (초)
}

const defaultConfig: HomeRowConfig = {
  rows: [
    {
      id: 'continue_watching',
      type: 'continue_watching',
      title: 'Continue Watching',
      position: 0,
      limit: 10,
      enabled: true,
    },
    {
      id: 'recently_added',
      type: 'recently_added',
      title: 'Recently Added',
      position: 1,
      limit: 20,
      enabled: true,
    },
    // Libraries are auto-generated from Jellyfin
    {
      id: 'trending',
      type: 'trending',
      title: 'Trending Now',
      position: 100,  // After libraries
      limit: 20,
      enabled: true,
    },
  ],
  defaultLimit: 20,
  refreshInterval: 300,  // 5분
};
```

### 7.2 캐싱 전략

```python
# Redis 캐싱
CACHE_KEYS = {
    "home_rows": "wsoptv:home:rows",           # 전체 Row 캐시 (5분)
    "library_row": "wsoptv:home:library:{id}", # 라이브러리별 캐시 (5분)
    "trending": "wsoptv:home:trending",        # 트렌딩 캐시 (1시간)
    "user_history": "wsoptv:user:{id}:history",# 사용자별 (실시간)
}
```

---

## 8. Benefits

### 8.1 사용자 경험

| 항목 | 개선 효과 |
|------|----------|
| **발견성** | 홈에서 모든 콘텐츠 노출 (스크롤만으로 탐색) |
| **개인화** | Continue Watching으로 이어보기 경험 |
| **접근성** | 2단계 네비게이션 (Home → Watch) |

### 8.2 기술적 장점

| 항목 | 개선 효과 |
|------|----------|
| **확장성** | 새 라이브러리 추가 시 자동 Row 생성 |
| **유연성** | Row 순서/타입 Admin에서 변경 가능 |
| **성능** | Row 단위 캐싱으로 빠른 로드 |
| **유지보수** | Jellyfin 라이브러리 = 카탈로그 (중복 관리 제거) |

---

## 9. Implementation Phases

### Phase 1: Core (MVP)
- [ ] `/api/v1/home` 엔드포인트
- [ ] HomePage, ContentRow 컴포넌트
- [ ] Jellyfin Library 기반 Row 자동 생성

### Phase 2: Personalization
- [ ] Continue Watching Row
- [ ] User watch history 연동

### Phase 3: Advanced
- [ ] Tag-based Row
- [ ] Trending Row (조회수 기반)
- [ ] Admin Row 설정 UI

---

## 10. Related Documents

| 문서 | 설명 |
|------|------|
| `docs/prds/0001-prd-wsoptv-platform.md` | PRD (수정 필요) |
| `docs/lld/0001-lld-wsoptv-platform.md` | LLD Master (수정 필요) |
| `docs/lld/0002-lld-modules.md` | 모듈/타입 정의 (수정 필요) |
| `docs/lld/0003-lld-api.md` | API 명세 (수정 필요) |
