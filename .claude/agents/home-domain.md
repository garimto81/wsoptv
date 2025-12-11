# Home Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 동적 카탈로그 및 홈페이지 Row 시스템 관리
**Updated**: 2025-12-11 (Hybrid Catalog System 반영)

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `home-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Home (Hybrid Catalog) |
| **Managed Blocks** | home.rows, home.browse, home.personalization |
| **Scope** | `backend/src/services/row_service.py`, `backend/src/api/v1/home.py`, `frontend/src/lib/components/home/` |
| **Feature Flag** | `USE_HYBRID_CATALOG` |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      HOME DOMAIN (Hybrid)                            │
│              (PostgreSQL catalogs/series + Jellyfin)                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │    rows      │───▶│    browse    │    │personalization│          │
│  │    Block     │    │    Block     │    │    Block     │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  • Series Row (신규)   • Series 필터     • Continue Watching       │
│  • Library Row (레거시) • Catalog 필터   • Trending                │
│  • 캐싱                • 페이지네이션    • 추천                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │   PostgreSQL    │             │ jellyfin-domain │
    │  • catalogs(8)  │             │   • Libraries   │
    │  • series(24)   │             │   • Items       │
    │  • contents     │             │   • Thumbnails  │
    └─────────────────┘             └─────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ `RowService`를 통해 모든 Row 생성
- ✅ **Feature Flag 분기 필수** (`USE_HYBRID_CATALOG`)
- ✅ **기존 코드 보존**: `_build_library_rows()` 수정 금지
- ✅ Jellyfin API 호출은 `JellyfinService`를 통해서만
- ✅ Row 데이터 캐싱 필수 (TTL 5분)
- ✅ 빈 Row는 응답에서 제외
- ✅ 로그인 사용자만 `continue_watching` Row 표시
- ✅ 모든 Row에 `viewAllUrl` 포함
- ✅ **PostgreSQL catalogs/series 테이블 활용** (하이브리드 모드)

### DON'T (하지 말 것)
- ❌ ~~PostgreSQL에 카탈로그 데이터 저장~~ → **허용됨 (하이브리드)**
- ❌ 기존 `_build_library_rows()` 함수 수정
- ❌ Jellyfin API 직접 호출 (반드시 JellyfinService 경유)
- ❌ 무한 Row 생성 (최대 30개 Row - Series 기준)
- ❌ 캐시 없이 Jellyfin/DB 호출 (과부하 방지)
- ❌ 다른 도메인 테이블 직접 조작
- ❌ **Frontend 변경** (이 작업 범위 외)

### 📊 데이터 소스 분리 (하이브리드)

| 데이터 | 소스 | 테이블/API | Feature Flag |
|--------|------|-----------|--------------|
| **Series Row** | PostgreSQL | `catalogs`, `series`, `contents` | `USE_HYBRID_CATALOG=true` |
| Library Row | Jellyfin | `GET /Libraries` | `USE_HYBRID_CATALOG=false` |
| Recently Added | Jellyfin | `GET /Items?sortBy=DateCreated` | 공통 |
| Continue Watching | PostgreSQL | `watch_progress` | 공통 |
| Trending | PostgreSQL | `view_events` | 공통 |
| 썸네일/Duration | Jellyfin | `GET /Items/{id}` | 공통 (enrichment) |

---

## Feature Flag Strategy

### USE_HYBRID_CATALOG

```python
# backend/src/core/config.py
USE_HYBRID_CATALOG: bool = False  # 기본값: 기존 동작

# 전환 패턴 (row_service.py)
if settings.USE_HYBRID_CATALOG:
    # 신규: PostgreSQL series 기반 Row
    rows = await self._build_series_rows(limit)
else:
    # 기존: Jellyfin Library 기반 Row (보존)
    rows = await self._build_library_rows(limit)
```

### 전환 단계

| 단계 | 환경 | USE_HYBRID_CATALOG | 검증 |
|------|------|-------------------|------|
| 1 | 개발 | `true` | Series Row 테스트 |
| 2 | 스테이징 | `true` | 통합 테스트 |
| 3 | 프로덕션 | `true` | 모니터링 |
| 4 | 정리 | - | 레거시 코드 제거 |

### 롤백 절차

```bash
# 즉시 롤백
USE_HYBRID_CATALOG=false docker compose restart backend
```

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `getHomepageRows` | `userId?` | `RowData[]` | 홈페이지 Row 목록 |
| `getSeriesRow` | `seriesId` | `RowData` | **신규**: 특정 Series Row |
| `getLibraryRow` | `libraryId` | `RowData` | 특정 라이브러리 Row (레거시) |
| `getBrowseContents` | `BrowseParams` | `PaginatedList<Content>` | 필터링된 콘텐츠 |
| `getContinueWatching` | `userId` | `RowData` | 이어보기 Row |
| `getTrending` | - | `RowData` | 인기 콘텐츠 Row |

---

## Dependencies

### 내부 의존성
- **jellyfin-domain**: 썸네일/duration enrichment
- **auth-domain**: 사용자 인증 (Continue Watching용)

### 외부 의존성
- `redis`: Row 캐싱
- `jellyfin-api`: 외부 미디어 서버
- **`postgresql`**: catalogs, series, contents 테이블

---

## Data Models

### RowData
```typescript
interface RowData {
  id: string;              // Row 고유 ID
  type: RowType;           // 'series' | 'library' | 'recently_added' | ...
  title: string;           // 표시 제목
  items: RowItem[];        // Row 내 아이템 목록
  filter?: RowFilter;      // 적용된 필터
  viewAllUrl: string;      // "View All" 링크
  totalCount?: number;     // 전체 아이템 수
}
```

### RowItem
```typescript
interface RowItem {
  id: string;              // Jellyfin Item ID 또는 Content ID
  title: string;
  thumbnailUrl?: string;   // Jellyfin enrichment
  duration?: number;       // seconds (Jellyfin enrichment)
  libraryName?: string;    // 레거시 호환
  seriesName?: string;     // 신규: Series 이름
  year?: number;
  progress?: number;       // 시청 진행률 (0-100)
}
```

### RowType (확장)
```typescript
type RowType =
  | 'continue_watching'    // 이어보기
  | 'recently_added'       // 최근 추가
  | 'series'               // ★ 신규: PostgreSQL Series 기반
  | 'catalog'              // ★ 신규: Catalog 그룹
  | 'library'              // 레거시: Jellyfin 라이브러리
  | 'trending'             // 인기
  | 'top_rated'            // 최고 평점
  | 'tag'                  // 태그 기반
  | 'player';              // 플레이어 기반
```

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `JELLYFIN_UNAVAILABLE` | 503 | Jellyfin 서버 접속 불가 | ✅ (캐시/DB 반환) |
| `CACHE_MISS` | - | Row 캐시 미스 | ✅ (DB/Jellyfin 호출) |
| `INVALID_LIBRARY` | 404 | 존재하지 않는 라이브러리 | ❌ |
| `INVALID_SERIES` | 404 | 존재하지 않는 Series | ❌ |
| `USER_NOT_AUTHENTICATED` | 401 | Continue Watching 인증 필요 | ❌ |

---

## Caching Strategy

| Row Type | TTL | 캐시 키 |
|----------|-----|---------|
| `recently_added` | 5분 | `wsoptv:home:recent` |
| `series` | 5분 | `wsoptv:home:series:{id}` |
| `library` | 5분 | `wsoptv:home:library:{id}` |
| `trending` | 1시간 | `wsoptv:home:trending` |
| `continue_watching` | 1분 | `wsoptv:user:{id}:continue` |
| 전체 Row (Hybrid) | 5분 | `wsoptv:home:rows:hybrid` |
| 전체 Row (Legacy) | 5분 | `wsoptv:home:rows:legacy` |

---

## Testing

- **단위 테스트**: `backend/tests/services/test_row_service.py`
- **통합 테스트**: `backend/tests/api/test_home.py`
- **E2E 테스트**: `apps/web/e2e/specs/home/`
- **Mock 정책**: Jellyfin API Mock, Redis Mock, DB Fixture

### 테스트 케이스 (확장)

| 케이스 | 설명 | Feature Flag |
|--------|------|--------------|
| `test_homepage_rows_anonymous` | 비로그인 사용자 Row | 공통 |
| `test_homepage_rows_authenticated` | 로그인 사용자 Row | 공통 |
| `test_series_row_generation` | **신규**: Series → Row 변환 | ON |
| `test_library_row_generation` | Library → Row 변환 | OFF |
| `test_content_to_row_item` | Content + Jellyfin enrichment | ON |
| `test_cache_hit` | 캐시 히트 시 미호출 | 공통 |
| `test_jellyfin_unavailable` | Jellyfin 장애 시 폴백 | 공통 |
| `test_feature_flag_off_fallback` | Flag OFF 시 레거시 동작 | OFF |

---

## Code Isolation Scope

이 도메인 작업 시 변경 허용 범위:

```yaml
# .claude/scopes/hybrid-catalog-scope.yaml 참조

primary:  # 자유롭게 수정
  - "backend/src/services/row_service.py"
  - "backend/src/schemas/row.py"
  - "backend/tests/services/test_row_service.py"

secondary:  # 최소 변경만
  - "backend/src/core/config.py"  # USE_HYBRID_CATALOG만
  - "backend/src/api/v1/home.py"  # 파라미터 추가만

forbidden:  # 수정 금지
  - "backend/src/services/jellyfin.py"
  - "backend/src/models/*.py"
  - "frontend/**"
```

---

## File Structure

```
Backend:
  backend/src/
  ├── api/v1/
  │   └── home.py           # GET /api/v1/home, /browse
  ├── services/
  │   └── row_service.py    # RowService (하이브리드)
  ├── schemas/
  │   └── row.py            # RowData, RowItem, RowType
  └── core/
      └── config.py         # USE_HYBRID_CATALOG

Frontend: (변경 없음)
  frontend/src/lib/
  ├── components/home/
  │   ├── ContentRow.svelte
  │   ├── ContentCard.svelte
  │   └── RowSkeleton.svelte
  └── api/
      └── home.ts

Scope Definition:
  .claude/scopes/hybrid-catalog-scope.yaml

PRD:
  docs/prds/0004-prd-hybrid-catalog-system.md
```

---

## Related Documents

| 문서 | 관계 |
|------|------|
| `docs/prds/0004-prd-hybrid-catalog-system.md` | 현재 PRD |
| `docs/prds/0003-prd-dynamic-catalog-system.md` | 이전 PRD (레거시) |
| `.claude/scopes/hybrid-catalog-scope.yaml` | 코드 격리 범위 |
| `docs/architecture/0003-code-isolation-agent-system.md` | 오염 방지 참조 |
