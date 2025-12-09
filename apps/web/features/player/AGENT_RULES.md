# Player Block Agent Rules

> 비디오 플레이어 블럭 전용 AI 에이전트 규칙

---

## Identity

| 속성 | 값 |
|------|-----|
| **Role** | 비디오 플레이어 전문가 |
| **Domain** | Stream (Frontend) |
| **Scope** | `features/player/` 내부만 |
| **Parent Agent** | `stream-domain` |

---

## Folder Structure

```
features/player/
├── components/           # 플레이어 UI 컴포넌트
│   ├── VideoPlayer.tsx
│   ├── PlayerControls.tsx
│   ├── Timeline.tsx
│   ├── HandOverlay.tsx
│   └── SkipButtons.tsx
├── hooks/                # 플레이어 관련 훅
│   ├── usePlayer.ts
│   ├── useTimeline.ts
│   └── useHandNavigation.ts
├── stores/               # 플레이어 상태 관리
│   └── playerStore.ts
├── api/                  # 스트리밍 API 호출
│   └── streamApi.ts
├── types.ts              # 플레이어 타입 정의
├── index.ts              # Public API
├── __tests__/            # 테스트
└── AGENT_RULES.md        # 이 파일
```

---

## Constraints

### DO (해야 할 것)
- ✅ 이 폴더 내 파일만 수정
- ✅ HLS.js 라이브러리 사용
- ✅ 핸드 타임라인 구간 정확히 처리
- ✅ 키보드 단축키 지원
- ✅ 반응형 레이아웃 적용
- ✅ 접근성 (a11y) 고려

### DON'T (하지 말 것)
- ❌ `features/` 외부 파일 직접 수정
- ❌ 원본 비디오 URL 클라이언트 노출
- ❌ 무한 재시도 (최대 3회)
- ❌ 하드코딩된 비디오 경로
- ❌ 동기 blocking 작업

---

## Dependencies

### 내부 의존성
```typescript
// ✅ 허용
import { Button, Slider } from '@/shared/ui';
import { formatTime } from '@/shared/utils';
import type { Hand, Content } from '@wsoptv/types';
import { useAuth } from '@/features/auth';  // 인증 상태
```

### 외부 의존성
```typescript
// ✅ 허용
import Hls from 'hls.js';
import { create } from 'zustand';
```

---

## Public API (index.ts)

```typescript
// 외부에서 사용 가능한 것만 export
export { VideoPlayer } from './components';
export { usePlayer, useTimeline } from './hooks';
export type { PlayerState, TimelineSegment } from './types';
```

---

## Type Definitions (types.ts)

```typescript
export interface PlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  buffered: number;
  volume: number;
  isMuted: boolean;
  quality: QualityLevel;
  isFullscreen: boolean;
}

export interface TimelineSegment {
  type: 'hand' | 'shuffle' | 'break';
  startSec: number;
  endSec: number;
  hand?: Hand;
}

export type QualityLevel = 'auto' | '1080p' | '720p' | '480p';
```

---

## Player Events

```typescript
// 플레이어에서 발생하는 커스텀 이벤트
type PlayerEvent =
  | 'handenter'      // 핸드 구간 진입
  | 'handleave'      // 핸드 구간 이탈
  | 'nonhandsegment' // 비핸드 구간 진입
  | 'skiptohand'     // 다음 핸드로 스킵
  | 'highlightsonly' // 하이라이트만 보기
  | 'qualitychange'  // 품질 변경
  | 'error';         // 에러 발생
```

---

## HLS Configuration

```typescript
const hlsConfig = {
  maxBufferLength: 30,
  maxMaxBufferLength: 60,
  startLevel: -1,  // auto
  capLevelToPlayerSize: true,
  progressive: true,
};
```

---

## Testing

- **위치**: `__tests__/` 폴더
- **네이밍**: `*.test.ts`, `*.spec.ts`
- **Mock 정책**:
  - HLS.js Mock
  - Video Element Mock
  - Timeline Mock
- **커버리지 목표**: 75%+

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | 재생/일시정지 |
| `←` / `→` | 5초 뒤로/앞으로 |
| `↑` / `↓` | 볼륨 증가/감소 |
| `M` | 음소거 토글 |
| `F` | 전체화면 토글 |
| `N` | 다음 핸드로 이동 |
| `P` | 이전 핸드로 이동 |

---

## Error Handling

```typescript
export type PlayerErrorCode =
  | 'PLAYER_SOURCE_ERROR'    // 소스 로드 실패
  | 'PLAYER_NETWORK_ERROR'   // 네트워크 오류
  | 'PLAYER_DECODE_ERROR'    // 디코딩 오류
  | 'PLAYER_TIMEOUT';        // 로딩 타임아웃

// 재시도 정책
const retryPolicy = {
  maxAttempts: 3,
  backoffMs: 1000,
  multiplier: 2,
};
```

---

## Performance Checklist

작업 완료 전 확인:

- [ ] 불필요한 리렌더링 방지 (memo, useMemo)
- [ ] 이벤트 리스너 정리 (cleanup)
- [ ] 메모리 누수 없음
- [ ] 60fps 유지 (Timeline 애니메이션)
- [ ] Lazy loading 적용
