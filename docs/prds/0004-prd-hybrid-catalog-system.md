# PRD: Hybrid Catalog System (PostgreSQL + Jellyfin)

**Version**: 1.0.0
**Date**: 2025-12-11
**Author**: Claude Code
**Status**: Draft
**Related**:
- `docs/prds/0003-prd-dynamic-catalog-system.md` (기존 PRD)
- `docs/architecture/0002-netflix-dynamic-catalog-system.md`

---

## 1. Executive Summary

기존 **Jellyfin-only 동적 카탈로그 시스템**을 **PostgreSQL catalogs/series + Jellyfin 하이브리드 아키텍처**로 전환합니다.

### 1.1 배경

현재 구현된 시스템의 문제점:
- Jellyfin 물리 폴더(5개) 기반 Row 생성 → **WSOP 1,268개가 단일 Row로 뭉침**
- PostgreSQL에 이미 존재하는 `catalogs`(8개) / `series`(24개) 테이블 미활용
- pokervod.db에서 마이그레이션된 정제 데이터 버림

### 1.2 핵심 변경점

| 항목 | 기존 (0003-prd) | 신규 (하이브리드) |
|------|----------------|------------------|
| **Row 소스** | Jellyfin Libraries (5개) | PostgreSQL catalogs/series (24개) |
| **데이터 구조** | 물리 폴더 기반 | 논리적 분류 (Catalog → Series) |
| **WSOP Row** | 1개 (1,268개 뭉침) | 16개 Series별 분리 |
| **콘텐츠 조회** | Jellyfin API 직접 | series_id → contents → jellyfin_id |
| **확장성** | 폴더 추가 필요 | DB 레코드 추가만 |

### 1.3 목표

- **세분화된 Row**: WSOP Europe 2024, WSOP Las Vegas 2024 등 Series 단위 Row
- **기존 데이터 활용**: 마이그레이션된 catalog/series 구조 사용
- **NAS 파일 이동 불필요**: 물리 폴더 재구성 없이 논리 분류 적용
- **코드 오염 방지**: Feature Flag 기반 점진적 전환

---

## 2. Problem Statement

### 2.1 현재 데이터 불일치

```
┌─────────────────────────────────────────────────────────────────────┐
│                    현재 데이터 구조 비교                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Jellyfin (물리 폴더)              PostgreSQL (논리 구조)            │
│  ───────────────────              ────────────────────               │
│                                                                      │
│  ┌─────────────┐                  ┌─────────────┐                   │
│  │ WSOP        │ 1,268개          │ WSOP        │ → 16 Series       │
│  │ (1 폴더)    │ 뭉침             │ (1 catalog) │   → 2,152 contents│
│  └─────────────┘                  └─────────────┘                   │
│                                                                      │
│  ┌─────────────┐                  ┌─────────────┐                   │
│  │ PAD         │                  │ PAD         │ → 2 Series        │
│  │ (1 폴더)    │                  │ (1 catalog) │   → 88 contents   │
│  └─────────────┘                  └─────────────┘                   │
│                                                                      │
│  ┌─────────────┐                  ┌─────────────┐                   │
│  │ HCL         │                  │ HCL         │ → 2 Series        │
│  │ (1 폴더)    │                  │ (1 catalog) │   → 232 contents  │
│  └─────────────┘                  └─────────────┘                   │
│                                                                      │
│  5 Libraries                      8 Catalogs → 24 Series            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 문서 vs 실제 불일치

| 문서 | 명시된 내용 | 실제 상태 |
|------|------------|----------|
| `0003-prd` | "PostgreSQL에 카탈로그 저장 안 함" | `catalogs`, `series` 테이블 존재 |
| `home-domain.md` | "PostgreSQL 저장 금지" | 8 catalogs, 24 series 저장됨 |
| `row_service.py` | "동적 생성 원칙" | DB에 구조화된 데이터 있음 |

---

## 3. Solution Overview

### 3.1 하이브리드 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Hybrid Catalog Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Frontend                    Backend                                 │
│  ────────                    ───────                                 │
│                                                                      │
│  GET /api/v1/home     →     RowService                              │
│       │                          │                                   │
│       │                          ├─── PostgreSQL ───┐               │
│       │                          │    catalogs (8)  │               │
│       │                          │    series (24)   │  Row 구조      │
│       │                          │    contents      │               │
│       │                          │                  │               │
│       │                          ├─── Jellyfin ─────┤               │
│       │                          │    Libraries     │  콘텐츠 상세   │
│       │                          │    Items         │  스트리밍      │
│       │                          │    Thumbnails    │               │
│       │                          └──────────────────┘               │
│       │                                                              │
│       ▼                                                              │
│  HomePage                                                            │
│  ├── Row: "WSOP Europe 2024" (series_id=1)                          │
│  ├── Row: "WSOP Las Vegas 2024" (series_id=2)                       │
│  ├── Row: "Poker After Dark S12" (series_id=17)                     │
│  └── Row: "HCL Season 2025" (series_id=19)                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 플로우

```
┌───────────────────────────────────────────────────────────────────────┐
│                         Data Flow                                      │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. Row 구조 조회 (PostgreSQL)                                         │
│     ┌──────────────────────────────────────────────────┐              │
│     │ SELECT s.id, s.title, s.year, c.name as catalog  │              │
│     │ FROM series s                                     │              │
│     │ JOIN catalogs c ON s.catalog_id = c.id           │              │
│     │ ORDER BY c.sort_order, s.year DESC               │              │
│     └──────────────────────────────────────────────────┘              │
│                              │                                         │
│                              ▼                                         │
│  2. Series별 콘텐츠 조회 (PostgreSQL)                                  │
│     ┌──────────────────────────────────────────────────┐              │
│     │ SELECT jellyfin_id, title, episode_num           │              │
│     │ FROM contents                                     │              │
│     │ WHERE series_id = :series_id                     │              │
│     │ ORDER BY episode_num                              │              │
│     └──────────────────────────────────────────────────┘              │
│                              │                                         │
│                              ▼                                         │
│  3. 콘텐츠 상세 조회 (Jellyfin) - Optional Enrichment                  │
│     ┌──────────────────────────────────────────────────┐              │
│     │ GET /Items/{jellyfin_id}                         │              │
│     │ → thumbnail_url, duration, date_created          │              │
│     └──────────────────────────────────────────────────┘              │
│                                                                        │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 4. Functional Requirements

### 4.1 FR-1: Series 기반 Row 생성

**Priority**: P0 (필수)

#### 4.1.1 RowService 수정

```python
class RowService:
    """하이브리드 Row 생성 서비스"""

    async def get_homepage_rows(
        self,
        user_id: int | None = None,
        limit_per_row: int = 20,
    ) -> HomeRowsResponse:
        rows: list[RowData] = []

        # 1. Recently Added (Jellyfin - 유지)
        rows.append(await self._build_recently_added_row(limit_per_row))

        # 2. Continue Watching (PostgreSQL - 유지)
        if user_id:
            rows.append(await self._build_continue_watching_row(user_id))

        # 3. Series Rows (PostgreSQL - 신규)
        if settings.USE_HYBRID_CATALOG:  # Feature Flag
            series_rows = await self._build_series_rows(limit_per_row)
            rows.extend(series_rows)
        else:
            # Fallback: 기존 Jellyfin Library 기반
            library_rows = await self._build_library_rows(limit_per_row)
            rows.extend(library_rows)

        # 4. Trending (PostgreSQL - 유지)
        rows.append(await self._build_trending_row())

        return HomeRowsResponse(rows=[r for r in rows if r.items])

    async def _build_series_rows(self, limit: int) -> list[RowData]:
        """PostgreSQL series 테이블 기반 Row 생성"""
        rows: list[RowData] = []

        # Series 목록 조회 (catalog 순서, year 내림차순)
        series_list = await self.db.execute(
            select(Series)
            .join(Catalog)
            .order_by(Catalog.sort_order, Series.year.desc())
        )

        for series in series_list.scalars():
            # Series별 콘텐츠 조회
            contents = await self.db.execute(
                select(Content)
                .where(Content.series_id == series.id)
                .order_by(Content.episode_num)
                .limit(limit)
            )

            items = [
                await self._content_to_row_item(content)
                for content in contents.scalars()
            ]

            if items:
                rows.append(RowData(
                    id=f"series_{series.id}",
                    type=RowType.SERIES,  # 신규 타입
                    title=series.title,
                    items=items,
                    view_all_url=f"/browse?series={series.id}",
                    total_count=series.content_count,
                    filter=RowFilter(series_id=series.id),
                ))

        return rows

    async def _content_to_row_item(self, content: Content) -> RowItem:
        """Content → RowItem 변환 (Jellyfin enrichment 포함)"""
        # 기본 정보 (PostgreSQL)
        item = RowItem(
            id=content.jellyfin_id or str(content.id),
            title=content.title,
            year=content.year,
        )

        # Jellyfin enrichment (썸네일, duration)
        if content.jellyfin_id:
            jellyfin_item = await self.jellyfin.get_item(content.jellyfin_id)
            if jellyfin_item:
                item.thumbnail_url = self.jellyfin.get_thumbnail_url(
                    jellyfin_item.id, "Primary", max_width=400
                )
                item.duration_sec = jellyfin_item.duration_seconds

        return item
```

### 4.2 FR-2: Feature Flag 기반 전환

**Priority**: P0 (필수)

#### 4.2.1 설정 추가

```python
# backend/src/core/config.py
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # Hybrid Catalog Feature Flag
    USE_HYBRID_CATALOG: bool = Field(
        default=False,
        description="PostgreSQL catalogs/series 기반 Row 생성 활성화"
    )
```

#### 4.2.2 전환 전략

| 단계 | USE_HYBRID_CATALOG | 동작 |
|------|-------------------|------|
| 1. 기존 유지 | `false` | Jellyfin Library 기반 Row (현재) |
| 2. 테스트 환경 | `true` (dev) | Series 기반 Row 테스트 |
| 3. 점진적 전환 | `true` (prod) | 모든 환경에서 Series Row |
| 4. 정리 | - | 기존 `_build_library_rows` 제거 |

### 4.3 FR-3: RowType 확장

**Priority**: P1 (중요)

```python
class RowType(str, Enum):
    CONTINUE_WATCHING = "continue_watching"
    RECENTLY_ADDED = "recently_added"
    LIBRARY = "library"          # 기존 (Jellyfin 폴더)
    SERIES = "series"            # 신규 (PostgreSQL series)
    CATALOG = "catalog"          # 신규 (PostgreSQL catalog 그룹)
    TRENDING = "trending"
    TOP_RATED = "top_rated"
```

### 4.4 FR-4: Browse 페이지 확장

**Priority**: P1 (중요)

```
GET /api/v1/browse?series={series_id}
GET /api/v1/browse?catalog={catalog_id}
```

| 파라미터 | 설명 |
|---------|------|
| `series` | Series ID로 필터링 |
| `catalog` | Catalog ID로 필터링 (하위 모든 Series 포함) |
| `library` | 기존 Jellyfin Library 필터 (하위 호환) |

---

## 5. Non-Functional Requirements

### 5.1 NFR-1: 성능

| 메트릭 | 기존 | 목표 |
|--------|------|------|
| Row 조회 | Jellyfin API 5회 | PostgreSQL 1회 + Jellyfin N회 (캐시) |
| 캐시 TTL | 5분 | 동일 |
| 콜드 스타트 | ~2s | ~1s (DB 쿼리 최적화) |

### 5.2 NFR-2: 하위 호환성

- 기존 `/api/v1/home` 응답 스키마 유지
- Frontend 변경 불필요 (RowData 스키마 동일)
- `library` 파라미터 계속 지원

### 5.3 NFR-3: 롤백 가능성

```bash
# 문제 발생 시 즉시 롤백
USE_HYBRID_CATALOG=false docker compose restart backend
```

---

## 6. Database Schema

### 6.1 기존 테이블 (활용)

```sql
-- catalogs (8개)
CREATE TABLE catalogs (
    id VARCHAR(50) PRIMARY KEY,  -- 'wsop', 'hcl', 'pad'
    name VARCHAR(100) NOT NULL,
    display_title VARCHAR(200) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0
);

-- series (24개)
CREATE TABLE series (
    id SERIAL PRIMARY KEY,
    catalog_id VARCHAR(50) REFERENCES catalogs(id),
    title VARCHAR(200) NOT NULL,  -- 'WSOP Europe 2024'
    year INTEGER NOT NULL,
    season_num INTEGER,
    description TEXT,
    thumbnail_url VARCHAR(500)
);

-- contents (2,524개)
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES series(id),
    jellyfin_id VARCHAR(100),  -- Jellyfin Item ID (매핑 키)
    title VARCHAR(500) NOT NULL,
    episode_num INTEGER,
    year INTEGER,
    duration_sec INTEGER,
    thumbnail_url VARCHAR(500)
);
```

### 6.2 Jellyfin ID 매핑 확인

```sql
-- jellyfin_id 매핑 상태 확인
SELECT
    COUNT(*) as total,
    COUNT(jellyfin_id) as mapped,
    COUNT(*) - COUNT(jellyfin_id) as unmapped
FROM contents;
```

**필요 시**: 마이그레이션 스크립트로 jellyfin_id 매핑 보완

---

## 7. Implementation Phases

### Phase 1: Feature Flag 및 기반 작업 (1일)

| 태스크 | 파일 | 설명 |
|--------|------|------|
| 1.1 | `backend/src/core/config.py` | `USE_HYBRID_CATALOG` 설정 추가 |
| 1.2 | `backend/src/schemas/row.py` | `RowType.SERIES` 추가 |
| 1.3 | `.env.example` | 환경 변수 문서화 |

### Phase 2: RowService 수정 (2일)

| 태스크 | 파일 | 설명 |
|--------|------|------|
| 2.1 | `backend/src/services/row_service.py` | `_build_series_rows()` 구현 |
| 2.2 | `backend/src/services/row_service.py` | `_content_to_row_item()` 구현 |
| 2.3 | `backend/src/services/row_service.py` | Feature Flag 분기 적용 |

### Phase 3: Browse API 확장 (1일)

| 태스크 | 파일 | 설명 |
|--------|------|------|
| 3.1 | `backend/src/api/v1/home.py` | `series`, `catalog` 파라미터 추가 |
| 3.2 | `backend/src/schemas/row.py` | `BrowseParams` 확장 |

### Phase 4: 테스트 및 검증 (1일)

| 태스크 | 파일 | 설명 |
|--------|------|------|
| 4.1 | `backend/tests/services/test_row_service.py` | 단위 테스트 |
| 4.2 | - | E2E 테스트 (Feature Flag ON/OFF) |

### Phase 5: 문서 업데이트 (0.5일)

| 태스크 | 파일 | 설명 |
|--------|------|------|
| 5.1 | `docs/architecture/0002-...md` | 아키텍처 문서 수정 |
| 5.2 | `.claude/agents/home-domain.md` | Agent 규칙 수정 |

---

## 8. Code Isolation Strategy (코드 오염 방지)

### 8.1 변경 범위 제한

```yaml
# 이 PRD의 허용 변경 범위

primary:  # 자유롭게 수정 가능
  - "backend/src/services/row_service.py"
  - "backend/src/schemas/row.py"
  - "backend/tests/services/test_row_service.py"

secondary:  # 최소 변경만
  - "backend/src/core/config.py"  # USE_HYBRID_CATALOG만 추가
  - "backend/src/api/v1/home.py"  # series/catalog 파라미터만

forbidden:  # 절대 수정 금지
  - "backend/src/services/jellyfin.py"  # 기존 로직 유지
  - "backend/src/models/*.py"  # 스키마 변경 없음
  - "frontend/**"  # 프론트엔드 변경 불필요
```

### 8.2 Feature Flag 원칙

```python
# ✅ 올바른 패턴: 기존 코드 보존
if settings.USE_HYBRID_CATALOG:
    rows = await self._build_series_rows(limit)
else:
    rows = await self._build_library_rows(limit)  # 기존 코드 그대로

# ❌ 잘못된 패턴: 기존 코드 수정
# def _build_library_rows(self, limit):  # 기존 함수 수정 금지
```

### 8.3 롤백 체크리스트

- [ ] `USE_HYBRID_CATALOG=false`로 기존 동작 확인
- [ ] 기존 테스트 모두 통과
- [ ] Frontend 변경 없이 동작

---

## 9. Success Metrics

| 메트릭 | 기존 | 목표 | 측정 방법 |
|--------|------|------|----------|
| Row 개수 | 6개 (5 Library + Recent) | 25개 (24 Series + Recent) | API 응답 |
| WSOP 세분화 | 1 Row | 16 Rows | Series 카운트 |
| API 응답 시간 | ~800ms | ~500ms | 로그 분석 |
| 캐시 히트율 | 70% | 80% | Redis 통계 |

---

## 10. Risks & Mitigations

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| jellyfin_id 매핑 누락 | 일부 콘텐츠 썸네일 없음 | Fallback 썸네일 + 매핑 스크립트 |
| 24개 Row 과다 | UX 저하 | Catalog 그룹핑 또는 최대 Row 제한 |
| 성능 저하 | 응답 시간 증가 | Eager loading + 캐싱 강화 |
| 롤백 필요 | 서비스 중단 | Feature Flag 즉시 OFF 가능 |

---

## 11. Related Documents

| 문서 | 관계 |
|------|------|
| `docs/prds/0003-prd-dynamic-catalog-system.md` | 기존 PRD (이 문서로 대체) |
| `docs/architecture/0002-netflix-dynamic-catalog-system.md` | 수정 필요 |
| `.claude/agents/home-domain.md` | Agent 규칙 수정 필요 |
| `docs/architecture/0003-code-isolation-agent-system.md` | 코드 오염 방지 참조 |

---

## 12. Appendix

### A. 현재 데이터 현황

```sql
-- Catalog별 Series/Content 카운트
SELECT
    c.name as catalog,
    COUNT(DISTINCT s.id) as series_count,
    COUNT(DISTINCT ct.id) as content_count
FROM catalogs c
LEFT JOIN series s ON s.catalog_id = c.id
LEFT JOIN contents ct ON ct.series_id = s.id
GROUP BY c.id, c.name
ORDER BY c.sort_order;

-- 결과:
-- WSOP     | 16 | 2152
-- PAD      |  2 |   88
-- HCL      |  2 |  232
-- MPP      |  3 |   22
-- GGPOKER  |  1 |   30
-- ...
```

### B. Feature Flag 환경 변수

```env
# .env
USE_HYBRID_CATALOG=false  # 기본값: 기존 동작

# .env.development
USE_HYBRID_CATALOG=true   # 개발 환경: 신규 기능 테스트

# .env.production
USE_HYBRID_CATALOG=false  # 프로덕션: 검증 후 활성화
```

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-11 | Claude Code | Initial draft |
