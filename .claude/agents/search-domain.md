# Search Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 전문 검색 및 자동완성 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `search-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Search |
| **Managed Blocks** | search.parse, search.search, search.rank |
| **Scope** | `apps/web/features/search/`, `packages/agents/search-domain/` |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SEARCH DOMAIN                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    parse     │───▶│    search    │───▶│    rank      │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  • 쿼리 파싱           • MeiliSearch       • 결과 정렬    │
│  • 필터 추출           • 패싯 집계         • 개인화       │
│  • 자동완성 분기       • 하이라이트        • 부스팅       │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ `features/search/` 폴더 내 파일만 수정
- ✅ 검색어 Sanitization 적용
- ✅ 디바운스 처리 (클라이언트 300ms)
- ✅ 결과 수 제한 (limit 필수)
- ✅ 검색 인덱스 별도 관리

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ SQL Injection 취약 쿼리
- ❌ 무제한 결과 반환
- ❌ MeiliSearch 인덱스 직접 수정 (migration 통해서만)
- ❌ 민감 필드 검색 노출

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `search` | `SearchQuery` | `SearchResult` | 전문 검색 |
| `suggest` | `SuggestQuery` | `Suggestion[]` | 자동완성 |
| `getFacets` | `SearchQuery` | `Facet[]` | 패싯 목록 |

---

## Dependencies

### 내부 의존성
- `@wsoptv/types`: 공유 타입 (`SearchResult`, `Facet`)
- `content-domain`: 검색 결과 보강
- `shared/utils`: 유틸리티 함수

### 외부 의존성
- `meilisearch`: 검색 엔진
- `zod`: 스키마 검증

---

## Search Configuration

### 인덱스 구조
```typescript
// MeiliSearch Index: contents
const searchableAttributes = [
  'title',
  'players',
  'catalogName',
  'episode',
];

const filterableAttributes = [
  'catalogId',
  'handGrade',
  'season',
  'hasHands',
];

const sortableAttributes = [
  'createdAt',
  'episode',
  'handCount',
];
```

### 패싯 설정
| Facet | Description | Max Values |
|-------|-------------|------------|
| `catalogId` | 카탈로그별 분류 | 10 |
| `handGrade` | 핸드 등급 (S/A/B/C) | 4 |
| `season` | 시즌 | 20 |

---

## Query Parsing

```typescript
// 검색어 예시
"Phil Ivey WSOP S등급"

// 파싱 결과
{
  query: "Phil Ivey",
  filters: {
    catalogId: "wsop",
    handGrade: "S"
  }
}
```

### 필터 키워드 매핑
| 키워드 | 필터 |
|--------|------|
| `WSOP`, `wsop` | `catalogId = 'wsop'` |
| `S등급`, `S급` | `handGrade = 'S'` |
| `A등급`, `A급` | `handGrade = 'A'` |

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `SEARCH_INDEX_ERROR` | 500 | MeiliSearch 오류 | ✅ (fallback) |
| `SEARCH_QUERY_INVALID` | 400 | 잘못된 검색어 | ❌ |
| `SEARCH_TIMEOUT` | 504 | 검색 타임아웃 | ✅ (retry) |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| 검색 응답 시간 | <100ms |
| 자동완성 응답 시간 | <50ms |
| 결과 정확도 | >90% |

---

## Testing

- **단위 테스트**: `features/search/__tests__/`
- **통합 테스트**: `tests/integration/search/`
- **Mock 정책**: MeiliSearch Mock Client
- **테스트 인덱스**: 분리된 테스트 인덱스 사용
