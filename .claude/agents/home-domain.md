# Home Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 동적 카탈로그 및 홈페이지 Row 시스템 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `home-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Home (Dynamic Catalog) |
| **Managed Blocks** | home.rows, home.browse, home.personalization |
| **Scope** | `backend/src/services/row_service.py`, `backend/src/api/v1/home.py`, `frontend/src/lib/components/home/` |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      HOME DOMAIN                             │
│              (동적 카탈로그 시스템)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    rows      │───▶│    browse    │    │personalization│  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  • Row 생성             • 필터링           • Continue Watching│
│  • 라이브러리 Row       • 정렬             • Trending        │
│  • 캐싱                 • 페이지네이션     • 추천            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ jellyfin-domain │ (의존)
                    │   • Libraries   │
                    │   • Items       │
                    └─────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ `RowService`를 통해 모든 Row 생성
- ✅ Jellyfin API 호출은 `JellyfinService`를 통해서만
- ✅ Row 데이터 캐싱 필수 (TTL 5분)
- ✅ 빈 Row는 응답에서 제외
- ✅ 로그인 사용자만 `continue_watching` Row 표시
- ✅ 모든 Row에 `viewAllUrl` 포함

### DON'T (하지 말 것)
- ❌ PostgreSQL에 카탈로그 데이터 저장 (동적 생성 원칙)
- ❌ Jellyfin API 직접 호출 (반드시 JellyfinService 경유)
- ❌ 무한 Row 생성 (최대 10개 Row)
- ❌ 캐시 없이 Jellyfin 호출 (과부하 방지)
- ❌ 다른 도메인 테이블 직접 조작

### 📊 데이터 소스 분리

| 데이터 | 소스 | 테이블/API |
|--------|------|-----------|
| Library Row | Jellyfin | `GET /Libraries` |
| Recently Added | Jellyfin | `GET /Items?sortBy=DateCreated` |
| Continue Watching | PostgreSQL | `watch_progress` |
| Trending | PostgreSQL | `view_events` |

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `getHomepageRows` | `userId?` | `RowData[]` | 홈페이지 Row 목록 |
| `getLibraryRow` | `libraryId` | `RowData` | 특정 라이브러리 Row |
| `getBrowseContents` | `BrowseParams` | `PaginatedList<Content>` | 필터링된 콘텐츠 |
| `getContinueWatching` | `userId` | `RowData` | 이어보기 Row |
| `getTrending` | - | `RowData` | 인기 콘텐츠 Row |

---

## Dependencies

### 내부 의존성
- **jellyfin-domain**: 라이브러리/아이템 조회
- **auth-domain**: 사용자 인증 (Continue Watching용)

### 외부 의존성
- `redis`: Row 캐싱
- `jellyfin-api`: 외부 미디어 서버

---

## Data Models

### RowData
```typescript
interface RowData {
  id: string;              // Row 고유 ID
  type: RowType;           // 'library' | 'recently_added' | ...
  title: string;           // 표시 제목
  items: RowItem[];        // Row 내 아이템 목록
  filter?: RowFilter;      // 적용된 필터
  viewAllUrl: string;      // "View All" 링크
}
```

### RowItem
```typescript
interface RowItem {
  id: string;              // Jellyfin Item ID
  title: string;
  thumbnailUrl: string;
  duration: number;        // seconds
  libraryName: string;
  progress?: number;       // 시청 진행률 (0-100)
}
```

### RowType
```typescript
type RowType =
  | 'continue_watching'    // 이어보기
  | 'recently_added'       // 최근 추가
  | 'library'              // 라이브러리별
  | 'trending'             // 인기
  | 'top_rated'            // 최고 평점
  | 'tag'                  // 태그 기반
  | 'player';              // 플레이어 기반
```

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `JELLYFIN_UNAVAILABLE` | 503 | Jellyfin 서버 접속 불가 | ✅ (캐시 반환) |
| `CACHE_MISS` | - | Row 캐시 미스 | ✅ (Jellyfin 호출) |
| `INVALID_LIBRARY` | 404 | 존재하지 않는 라이브러리 | ❌ |
| `USER_NOT_AUTHENTICATED` | 401 | Continue Watching 인증 필요 | ❌ |

---

## Caching Strategy

| Row Type | TTL | 캐시 키 |
|----------|-----|---------|
| `recently_added` | 5분 | `wsoptv:home:recent` |
| `library` | 5분 | `wsoptv:home:library:{id}` |
| `trending` | 1시간 | `wsoptv:home:trending` |
| `continue_watching` | 1분 | `wsoptv:user:{id}:continue` |
| 전체 Row | 5분 | `wsoptv:home:rows` |

### 캐시 무효화 조건

| 이벤트 | 무효화 대상 |
|--------|------------|
| Jellyfin 라이브러리 추가 | `wsoptv:home:rows`, `wsoptv:home:library:*` |
| 새 콘텐츠 추가 | `wsoptv:home:recent`, `wsoptv:home:library:{id}` |
| 사용자 시청 | `wsoptv:user:{id}:continue` |
| 조회수 변경 | `wsoptv:home:trending` (1시간 후 자연 만료) |

---

## Fallback Strategy

Jellyfin 장애 시 폴백:

```python
async def get_homepage_rows(self, user_id: int | None) -> list[RowData]:
    try:
        # 1. 캐시 확인
        cached = await self.cache.get("wsoptv:home:rows")
        if cached:
            return cached

        # 2. Jellyfin 호출
        rows = await self._build_rows(user_id)
        await self.cache.set("wsoptv:home:rows", rows, ttl=300)
        return rows

    except JellyfinUnavailableError:
        # 3. Fallback: 만료된 캐시라도 반환
        stale_cache = await self.cache.get("wsoptv:home:rows", ignore_ttl=True)
        if stale_cache:
            return stale_cache

        # 4. 최후 수단: PostgreSQL 기반 정적 Row
        return await self._get_fallback_rows()
```

---

## Testing

- **단위 테스트**: `backend/tests/services/test_row_service.py`
- **통합 테스트**: `backend/tests/api/test_home.py`
- **E2E 테스트**: `apps/web/e2e/specs/home/`
- **Mock 정책**: Jellyfin API Mock, Redis Mock

### 테스트 케이스

| 케이스 | 설명 |
|--------|------|
| `test_homepage_rows_anonymous` | 비로그인 사용자 Row (Continue Watching 없음) |
| `test_homepage_rows_authenticated` | 로그인 사용자 Row (Continue Watching 포함) |
| `test_library_row_generation` | Jellyfin 라이브러리 → Row 변환 |
| `test_cache_hit` | 캐시 히트 시 Jellyfin 미호출 |
| `test_jellyfin_unavailable` | Jellyfin 장애 시 폴백 |

---

## Integration Points

- **Orchestrator**: 홈페이지 관련 작업 라우팅
- **jellyfin-domain**: 라이브러리/아이템 데이터 제공
- **auth-domain**: 사용자 인증 토큰 검증

---

## File Structure

```
Backend:
  backend/src/
  ├── api/v1/
  │   ├── home.py         # GET /api/v1/home
  │   └── browse.py       # GET /api/v1/browse
  ├── services/
  │   └── row_service.py  # RowService 클래스
  └── schemas/
      ├── row.py          # RowData, RowItem, RowFilter
      └── browse.py       # BrowseParams, BrowseResponse

Frontend:
  frontend/src/lib/
  ├── components/home/
  │   ├── HomePage.svelte
  │   ├── ContentRow.svelte
  │   ├── ContentCard.svelte
  │   └── RowSkeleton.svelte
  ├── components/browse/
  │   ├── BrowsePage.svelte
  │   ├── FilterBar.svelte
  │   └── ContentGrid.svelte
  └── api/
      └── home.ts         # fetchHomeRows()

AGENT_RULES:
  frontend/src/lib/components/home/AGENT_RULES.md
```
