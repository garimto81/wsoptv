# Search Block Agent Rules

> 검색 블럭 전용 AI 에이전트 규칙

---

## Identity

| 속성 | 값 |
|------|-----|
| **Role** | 검색 전문가 |
| **Domain** | Search |
| **Scope** | `features/search/` 내부만 |
| **Parent Agent** | `search-domain` |

---

## Folder Structure

```
features/search/
├── components/           # 검색 UI 컴포넌트
│   ├── SearchBar.tsx
│   ├── SearchResults.tsx
│   ├── SearchFilters.tsx
│   ├── Autocomplete.tsx
│   └── FacetList.tsx
├── hooks/                # 검색 관련 훅
│   ├── useSearch.ts
│   ├── useAutocomplete.ts
│   └── useFacets.ts
├── stores/               # 검색 상태 관리
│   └── searchStore.ts
├── api/                  # 검색 API 호출
│   └── searchApi.ts
├── types.ts              # 검색 타입 정의
├── index.ts              # Public API
├── __tests__/            # 테스트
└── AGENT_RULES.md        # 이 파일
```

---

## Constraints

### DO (해야 할 것)
- ✅ 이 폴더 내 파일만 수정
- ✅ 디바운스 적용 (300ms)
- ✅ 검색어 Sanitization
- ✅ 결과 수 제한 (limit 필수)
- ✅ 키보드 네비게이션 지원
- ✅ 검색 히스토리 로컬 저장

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ SQL/NoSQL Injection 취약 코드
- ❌ 무제한 결과 반환
- ❌ MeiliSearch 인덱스 직접 수정
- ❌ 민감 필드 검색 노출

---

## Dependencies

### 내부 의존성
```typescript
// ✅ 허용
import { Input, List } from '@/shared/ui';
import { debounce } from '@/shared/utils';
import type { Content, SearchResult } from '@wsoptv/types';
```

### 외부 의존성
```typescript
// ✅ 허용
import { create } from 'zustand';
import { z } from 'zod';
```

---

## Public API (index.ts)

```typescript
// 외부에서 사용 가능한 것만 export
export { SearchBar, SearchResults, SearchFilters } from './components';
export { useSearch, useAutocomplete } from './hooks';
export type { SearchState, SearchQuery, Facet } from './types';
```

---

## Type Definitions (types.ts)

```typescript
export interface SearchQuery {
  q: string;
  filters?: SearchFilters;
  page?: number;
  limit?: number;
  sort?: SortOption;
}

export interface SearchFilters {
  catalogId?: string;
  handGrade?: HandGrade[];
  season?: string;
  hasHands?: boolean;
}

export interface SearchState {
  query: string;
  results: SearchResult[];
  facets: Facet[];
  isLoading: boolean;
  totalHits: number;
  page: number;
}

export type SortOption = 'relevance' | 'date' | 'episode';
export type HandGrade = 'S' | 'A' | 'B' | 'C';
```

---

## Search Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  사용자 입력     │────▶│  디바운스       │────▶│  API 호출       │
│  "Phil Ivey"    │     │  (300ms)        │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│  결과 렌더링     │◀────│  상태 업데이트   │◀────│  응답 수신      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Autocomplete Behavior

```typescript
// 자동완성 설정
const autocompleteConfig = {
  minChars: 2,           // 최소 입력 글자
  maxSuggestions: 8,     // 최대 제안 수
  debounceMs: 150,       // 디바운스 (검색보다 짧게)
  highlightMatch: true,  // 매칭 부분 강조
};
```

---

## Testing

- **위치**: `__tests__/` 폴더
- **네이밍**: `*.test.ts`, `*.spec.ts`
- **Mock 정책**:
  - `searchApi` 함수 Mock
  - MeiliSearch 응답 Mock
- **커버리지 목표**: 80%+

---

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | 자동완성 항목 이동 |
| `Enter` | 선택/검색 실행 |
| `Escape` | 자동완성 닫기 |
| `Tab` | 첫 번째 제안 선택 |

---

## Error Handling

```typescript
export type SearchErrorCode =
  | 'SEARCH_INDEX_ERROR'    // MeiliSearch 오류
  | 'SEARCH_QUERY_INVALID'  // 잘못된 검색어
  | 'SEARCH_TIMEOUT';       // 검색 타임아웃

// 에러 발생 시 Fallback
const handleSearchError = (error: SearchError) => {
  if (error.code === 'SEARCH_INDEX_ERROR') {
    // 캐시된 결과 또는 빈 결과 반환
    return { results: [], fromCache: true };
  }
};
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| 검색 응답 표시 | <200ms |
| 자동완성 표시 | <100ms |
| 디바운스 | 300ms |
| 최대 결과 수 | 50개/페이지 |

---

## UX Checklist

작업 완료 전 확인:

- [ ] 로딩 상태 표시
- [ ] 빈 결과 시 안내 메시지
- [ ] 검색어 하이라이팅
- [ ] 최근 검색어 저장/표시
- [ ] 필터 상태 URL 반영
