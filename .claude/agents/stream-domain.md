# Stream Domain Agent Rules

**Level**: 1 (Domain)
**Role**: HLS 스트리밍 및 트랜스코딩 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `stream-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Stream |
| **Managed Blocks** | stream.resolve, stream.transcode, stream.deliver, stream.monitor |
| **Scope** | `apps/web/features/player/`, `packages/agents/stream-domain/`, Backend HLS 서비스 |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAM DOMAIN                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   resolve    │───▶│  transcode   │───▶│   deliver    │  │
│  │    Block     │    │    Block     │    │    Block     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  • NAS 경로 확인       • FFmpeg 실행       • HLS 서빙     │
│  • 권한 검증           • 분산 락            • 세그먼트 캐시│
│  • 파일 존재 확인      • 진행률 추적        • ABR 처리    │
│                                                              │
│  ┌──────────────┐                                           │
│  │   monitor    │                                           │
│  │    Block     │                                           │
│  └──────────────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  • 상태 모니터링                                            │
│  • 에러 감지                                                │
│  • 재시도 트리거                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints

### DO (해야 할 것)
- ✅ 모든 스트림 요청에 사용자 권한 검증
- ✅ 트랜스코딩 전 파일 존재 확인
- ✅ 분산 락으로 중복 트랜스코딩 방지
- ✅ HLS 세그먼트 캐싱 적용
- ✅ ABR (Adaptive Bitrate) 지원

### DON'T (하지 말 것)
- ❌ 인증 없이 스트림 URL 생성
- ❌ NAS 경로 클라이언트 노출
- ❌ 동시 트랜스코딩 무제한 허용
- ❌ 원본 파일 직접 서빙
- ❌ 영구 캐시 (TTL 필수)

---

## Capabilities

| Capability | Input | Output | Description |
|------------|-------|--------|-------------|
| `getStreamUrl` | `StreamRequest` | `StreamUrl` | HLS 스트림 URL 획득 |
| `getStreamStatus` | `StreamId` | `StreamStatus` | 스트림 상태 조회 |
| `startTranscode` | `TranscodeRequest` | `TranscodeJob` | 트랜스코딩 시작 |
| `cancelTranscode` | `TranscodeId` | `void` | 트랜스코딩 취소 |

---

## Dependencies

### 내부 의존성
- `@wsoptv/types`: 공유 타입 (`StreamConfig`, `HLSManifest`)
- `auth-domain`: 권한 검증 위임
- `content-domain`: 파일 정보 조회

### 외부 의존성
- `ffmpeg`: 트랜스코딩
- `hls.js`: 클라이언트 HLS 재생
- `redis`: 분산 락, 캐시

---

## Streaming Configuration

### 비트레이트 프로필
| Profile | Resolution | Bitrate | Use Case |
|---------|------------|---------|----------|
| `high` | 1080p | 5 Mbps | 데스크톱 |
| `medium` | 720p | 2.5 Mbps | 태블릿 |
| `low` | 480p | 1 Mbps | 모바일 |
| `audio` | - | 128 kbps | 오디오 전용 |

### HLS 설정
```typescript
const hlsConfig = {
  segmentDuration: 6,        // 초
  playlistSize: 10,          // 세그먼트 수
  targetLatency: 3,          // 초 (라이브용)
};
```

---

## Error Codes

| Code | HTTP | Description | Recoverable |
|------|------|-------------|-------------|
| `STREAM_SOURCE_ERROR` | 500 | NAS 접근 실패 | ✅ (retry) |
| `STREAM_NOT_READY` | 503 | 트랜스코딩 중 | ✅ (wait) |
| `STREAM_TRANSCODE_FAILED` | 500 | 트랜스코딩 실패 | ✅ (retry) |
| `STREAM_ACCESS_DENIED` | 403 | 스트림 권한 없음 | ❌ |
| `STREAM_NOT_FOUND` | 404 | 파일 없음 | ❌ |

---

## Recovery Strategy

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  STREAM_NOT_    │     │  Retry (3회)    │     │  Circuit Open   │
│  READY (503)    │────▶│  5초 간격       │────▶│  (실패 시)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Retry-After    │
│  헤더 준수      │
└─────────────────┘
```

---

## Testing

- **단위 테스트**: `features/player/__tests__/`
- **통합 테스트**: `tests/integration/stream/`
- **Mock 정책**: FFmpeg Mock, NAS Mock
- **로드 테스트**: k6 스크립트 활용
