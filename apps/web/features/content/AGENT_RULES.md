# Content Block Agent Rules

> 콘텐츠 블럭 전용 AI 에이전트 규칙

---

## Identity

| 속성 | 값 |
|------|-----|
| **Role** | 콘텐츠 관리 전문가 |
| **Domain** | Content |
| **Scope** | `features/content/` 내부만 |
| **Parent Agent** | `content-domain` |

---

## Folder Structure

```
features/content/
├── components/           # 콘텐츠 UI 컴포넌트
│   ├── ContentCard.tsx
│   ├── ContentList.tsx
│   ├── ContentDetail.tsx
│   ├── HandList.tsx
│   └── EpisodeSelector.tsx
├── hooks/                # 콘텐츠 관련 훅
│   ├── useContent.ts
│   ├── useHands.ts
│   └── useWatchProgress.ts
├── stores/               # 콘텐츠 상태 관리
│   └── contentStore.ts
├── api/                  # 콘텐츠 API 호출
│   └── contentApi.ts
├── types.ts              # 콘텐츠 타입 정의
├── index.ts              # Public API
├── __tests__/            # 테스트
└── AGENT_RULES.md        # 이 파일
```

---

## Constraints

### DO (해야 할 것)
- ✅ 이 폴더 내 파일만 수정
- ✅ 페이지네이션 적용 (무한 스크롤 또는 페이지)
- ✅ 이미지 Lazy Loading
- ✅ 썸네일 최적화 (srcset)
- ✅ 시청 진행률 30초마다 저장
- ✅ 핸드 등급 필터링 제공

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ 무제한 콘텐츠 로드
- ❌ 대용량 이미지 원본 로드
- ❌ 캐시 무효화 없이 데이터 수정
- ❌ 민감한 사용자 정보 노출

---

## Dependencies

### 내부 의존성
```typescript
// ✅ 허용
import { Card, Image, Badge } from '@/shared/ui';
import { formatDuration } from '@/shared/utils';
import type { Content, Hand, Episode } from '@wsoptv/types';
import { useAuth } from '@/features/auth';  // 인증 상태
```

### 외부 의존성
```typescript
// ✅ 허용
import { create } from 'zustand';
import { useInfiniteQuery } from '@tanstack/react-query';
```

---

## Public API (index.ts)

```typescript
// 외부에서 사용 가능한 것만 export
export {
  ContentCard,
  ContentList,
  ContentDetail,
  HandList
} from './components';
export { useContent, useHands, useWatchProgress } from './hooks';
export type { ContentState, WatchProgress } from './types';
```

---

## Type Definitions (types.ts)

```typescript
export interface ContentState {
  contents: Content[];
  selectedContent: Content | null;
  hands: Hand[];
  isLoading: boolean;
  hasMore: boolean;
  page: number;
}

export interface WatchProgress {
  contentId: number;
  progressSec: number;
  durationSec: number;
  completed: boolean;
  lastWatchedAt: string;
}

export interface ContentQuery {
  catalogId?: string;
  season?: string;
  page?: number;
  limit?: number;
  sort?: 'recent' | 'episode' | 'popular';
}
```

---

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  콘텐츠 목록     │────▶│  콘텐츠 상세    │────▶│  비디오 재생    │
│  (ContentList)  │     │  (ContentDetail)│     │  (→ Player)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │  핸드 목록       │
                        │  (HandList)     │
                        └─────────────────┘
```

---

## Watch Progress Sync

```typescript
// 시청 진행률 저장 로직
const watchProgressConfig = {
  saveIntervalMs: 30000,     // 30초마다 저장
  completedThreshold: 0.9,   // 90% 이상 시청 시 완료
  debounceMs: 5000,          // 디바운스
};

// 이어보기 로직
const resumePlayback = (progress: WatchProgress) => {
  if (progress && !progress.completed) {
    // 이어보기 모달 표시
    showResumeDialog(progress.progressSec);
  }
};
```

---

## Testing

- **위치**: `__tests__/` 폴더
- **네이밍**: `*.test.ts`, `*.spec.ts`
- **Mock 정책**:
  - `contentApi` 함수 Mock
  - React Query Mock
- **커버리지 목표**: 80%+

---

## Error Handling

```typescript
export type ContentErrorCode =
  | 'CONTENT_NOT_FOUND'      // 콘텐츠 없음
  | 'CONTENT_ACCESS_DENIED'  // 접근 권한 없음
  | 'CONTENT_LOAD_ERROR';    // 로드 실패

// 에러 처리 패턴
const handleContentError = (error: ContentError) => {
  switch (error.code) {
    case 'CONTENT_NOT_FOUND':
      return <NotFoundPage />;
    case 'CONTENT_ACCESS_DENIED':
      return <AccessDeniedPage />;
    default:
      return <ErrorPage retry={refetch} />;
  }
};
```

---

## Caching Strategy

| 데이터 | Stale Time | Cache Time | 무효화 |
|--------|------------|------------|--------|
| 콘텐츠 목록 | 5분 | 30분 | 새 콘텐츠 추가 시 |
| 콘텐츠 상세 | 10분 | 1시간 | 콘텐츠 수정 시 |
| 핸드 목록 | 30분 | 2시간 | 핸드 추가/수정 시 |
| 시청 진행률 | 0 | 5분 | 항상 최신 |

---

## UX Checklist

작업 완료 전 확인:

- [ ] 스켈레톤 로딩 UI
- [ ] 빈 상태 안내
- [ ] 이미지 로드 실패 처리
- [ ] 무한 스크롤 동작
- [ ] 핸드 등급 배지 표시
- [ ] 시청 진행률 표시
