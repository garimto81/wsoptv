# Content Domain Agent Rules

**Level**: 1 (Domain)
**Role**: 콘텐츠 및 핸드 데이터 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `content-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Content |
| **Managed Blocks** | content.query, content.cache, content.response, content.hands, content.timeline |
| **Scope** | `apps/web/features/content/`, `packages/agents/content-domain/` |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTENT DOMAIN                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    query     │───▶│    cache     │───▶│   response   │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                                   │
│  ┌──────┴───────┐                                          │
│  ▼              ▼                                          │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │    hands     │───▶│   timeline   │                      │
│  │    Block     │    │    Block     │                      │
│  └──────────────┘    └──────────────┘                      │
│         │                   │                              │
│         ▼                   ▼                              │
│  • 핸드 데이터         • 타임라인 구축                     │
│  • 등급 필터           • 구간 인덱싱                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ `features/content/` 폴더 내 파일만 수정
- ✅ 모든 DB 조회 시 페이지네이션 적용
- ✅ 캐시 키에 버전 포함
- ✅ Eager Loading으로 N+1 방지
- ✅ 핸드 등급 기반 필터링 제공

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ 무한 결과 반환 (limit 필수)
- ❌ 캐시 무효화 없이 데이터 수정
- ❌ Stream 도메인 직접 호출
- ❌ 민감한 사용자 정보 노출

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `getContent` | `ContentId` | `ContentDetail` | 콘텐츠 상세 조회 |
| `listContents` | `ContentListQuery` | `PaginatedList<Content>` | 콘텐츠 목록 조회 |
| `getHands` | `ContentId` | `Hand[]` | 핸드 목록 조회 |
| `buildTimeline` | `Hand[]` | `TimelineIndex` | 타임라인 인덱스 생성 |
| `invalidateCache` | `ContentId` | `void` | 캐시 무효화 |

---

## Dependencies

### 내부 의존성
- `@wsoptv/types`: 공유 타입 (`Content`, `Hand`, `Episode`)
- `@wsoptv/hands`: 핸드 처리 라이브러리
- `shared/utils`: 유틸리티 함수

### 외부 의존성
- `drizzle-orm`: ORM
- `redis`: 캐시
- `zod`: 스키마 검증

---

## Data Models

### Content
```typescript
interface Content {
  id: number;
  catalogId: string;
  title: string;
  episode?: number;
  season?: string;
  fileId: number;
  durationSec: number;
  thumbnailUrl?: string;
}
```

### Hand
```typescript
interface Hand {
  id: number;
  contentId: number;
  handNumber: number;
  grade: 'S' | 'A' | 'B' | 'C';
  startSec: number;
  endSec: number;
  players: string[];
  potSize?: number;
}
```

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `CONTENT_NOT_FOUND` | 404 | 콘텐츠 없음 | ❌ |
| `CONTENT_ACCESS_DENIED` | 403 | 접근 권한 없음 | ❌ |
| `CACHE_MISS` | - | 캐시 미스 | ✅ (DB 조회) |
| `INVALID_PAGE` | 400 | 잘못된 페이지 | ❌ |

---

## Caching Strategy

| 데이터 | TTL | 무효화 조건 |
|--------|-----|------------|
| 콘텐츠 상세 | 10분 | 콘텐츠 수정 시 |
| 핸드 목록 | 30분 | 핸드 추가/수정 시 |
| 타임라인 | 1시간 | 핸드 변경 시 |
| 콘텐츠 목록 | 5분 | 새 콘텐츠 추가 시 |

---

## Testing

- **단위 테스트**: `features/content/__tests__/`
- **통합 테스트**: `tests/integration/content/`
- **Mock 정책**: DB 쿼리 Mock, Redis Mock
- **테스트 데이터**: fixtures/ 폴더 활용
