# PRD: WSOPTV - Poker VOD Streaming Platform

**Version**: 1.3.0
**Date**: 2025-12-09
**Author**: Claude Code
**Status**: Draft

---

## 1. Executive Summary

WSOPTV는 18TB+ 포커 방송 아카이브(WSOP, HCL, PAD, GGMillions 등)를 기반으로 한 초대 기반 포커 VOD 스트리밍 플랫폼입니다. 일반 포커 팬을 대상으로 핸드 타임코드 기반 탐색, 개인화 추천, 고품질 스트리밍 경험을 제공합니다.

### 1.1 Vision

> "모든 포커 팬이 좋아하는 플레이어의 명장면을 쉽게 찾고, 자신만의 시청 경험을 만들어가는 플랫폼"

### 1.2 Key Differentiators

| 차별점 | 설명 |
|--------|------|
| **핸드 중심 탐색** | 타임코드 기반 핸드 이동, 플레이어/등급별 필터링 |
| **개인화 추천** | 시청 이력 기반 맞춤 콘텐츠 추천 |
| **초대 기반 커뮤니티** | 품질 높은 시청자 커뮤니티 구축 |

---

## 2. Problem Statement

### 2.1 현재 Pain Points

1. **콘텐츠 접근성**: 18TB+ 아카이브가 NAS에 산재, 체계적 탐색 불가
2. **핸드 검색 어려움**: 특정 플레이어나 핸드를 찾으려면 전체 영상 시청 필요
3. **개인화 부재**: 모든 사용자에게 동일한 콘텐츠 노출
4. **시청 연속성**: 이어보기, 시청 기록 관리 불가

### 2.2 Target Users

**Primary**: 일반 포커 팬
- 연령대: 25-45세
- 관심사: WSOP, High Stakes Poker, 유명 플레이어 경기
- 니즈: 명장면 탐색, 특정 플레이어 팔로우, 편한 시청 경험

**Secondary**: 포커 학습자
- 전략 학습 목적의 핸드 분석
- 반복 시청, 북마크 기능 활용

---

## 3. Solution Overview

### 3.1 High-Level Architecture (Docker 기반)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WSOPTV Platform (Docker Network)                      │
│                         Network: wsoptv-network                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐         │
│  │    frontend    │    │    backend     │    │   transcoder   │         │
│  │   (SvelteKit)  │───▶│   (FastAPI)    │───▶│   (FFmpeg)     │         │
│  │   Port 3000    │    │   Port 8001    │    │   Worker       │         │
│  └────────────────┘    └───────┬────────┘    └────────────────┘         │
│                                │                                         │
│           ┌────────────────────┼────────────────────┐                   │
│           │                    │                    │                   │
│     ┌─────▼─────┐       ┌──────▼──────┐      ┌──────▼──────┐           │
│     │ PostgreSQL│       │ MeiliSearch │      │    Redis    │           │
│     │   :5432   │       │    :7700    │      │    :6379    │           │
│     └───────────┘       └─────────────┘      └─────────────┘           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Volumes                                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │   │
│  │  │ postgres │  │  meili   │  │  redis   │  │  hls-segments    │  │   │
│  │  │  -data   │  │  -data   │  │  -data   │  │  (transcoded)    │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    External Mount (NAS)                           │   │
│  │                    //10.10.100.122/GGPNAs/ARCHIVE                 │   │
│  │                    → /mnt/nas (read-only)                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Docker Services

| Service | Image | Port | 역할 |
|---------|-------|------|------|
| **frontend** | node:20-alpine | 3000 | SvelteKit UI |
| **backend** | python:3.11-slim | 8001 | FastAPI Server |
| **postgres** | postgres:16-alpine | 5432 | Primary Database |
| **meilisearch** | getmeili/meilisearch:v1.6 | 7700 | 전문 검색 |
| **redis** | redis:7-alpine | 6379 | 캐싱, 작업 큐 |
| **transcoder** | jrottenberg/ffmpeg:6 | - | HLS 트랜스코딩 Worker |

### 3.3 Data Flow (스트리밍 중계 구조)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Streaming Architecture                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐      ┌──────────────────────┐      ┌─────────────┐    │
│  │   NAS   │      │   중계 서버 (Frontend) │      │   시청자    │    │
│  │  18TB+  │─────▶│   (Proxy + Cache)     │─────▶│   Browser   │    │
│  └─────────┘      └──────────────────────┘      └─────────────┘    │
│       │                     │                                        │
│       │              ┌──────┴──────┐                                │
│       │              │  HLS 변환   │                                │
│       │              │  (on-demand)│                                │
│       │              └─────────────┘                                │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐                     │
│  │ Backend │─────▶│PostgreSQL│     │  Redis  │                     │
│  │  API    │      │   DB    │      │ Cache   │                     │
│  └─────────┘      └─────────┘      └─────────┘                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

요청 흐름:
1. 시청자 → Frontend (중계 서버) → 비디오 요청
2. Frontend → NAS → 원본 파일 읽기
3. Frontend → HLS 변환 (실시간 또는 캐시)
4. Frontend → 시청자 (HLS 스트림 전달)
```

**중계 서버 역할**:

| 역할 | 설명 |
|------|------|
| **Proxy** | NAS 파일을 시청자에게 중계 |
| **HLS 변환** | MP4 → HLS 실시간 트랜스먹싱 |
| **캐싱** | 인기 콘텐츠 HLS 세그먼트 캐시 |
| **인증** | 승인된 사용자만 스트림 접근 |
| **대역폭 제어** | 동시 접속자 제한, 품질 조절 |

---

## 4. Feature Requirements

### 4.1 MVP Features (Phase 1)

#### F1. 검색 + 브라우징
**Priority**: P0 (Must Have)

| 기능 | 설명 |
|------|------|
| 카탈로그 브라우징 | WSOP, HCL, PAD 등 카탈로그별 탐색 |
| 시리즈/콘텐츠 계층 | Series → Contents 구조 탐색 |
| 전문 검색 | MeiliSearch 기반 제목/플레이어/태그 검색 |
| 필터링 | 카탈로그, 플레이어, 핸드 등급, 연도별 필터 |
| 자동완성 | 검색어 자동완성 (플레이어명, 이벤트명) |

```typescript
// 검색 API 예시
interface SearchRequest {
  query: string;
  filters?: {
    catalog_id?: string;
    player_id?: number;
    hand_grade?: 'S' | 'A' | 'B' | 'C';
    year?: number;
  };
  page?: number;
  limit?: number;
}

interface SearchResponse {
  results: Content[];
  total: number;
  facets: {
    catalogs: Record<string, number>;
    players: Record<string, number>;
    hand_grades: Record<string, number>;
  };
}
```

#### F2. 스트리밍 재생
**Priority**: P0 (Must Have)

| 기능 | 설명 |
|------|------|
| 비디오 플레이어 | Video.js 기반 커스텀 플레이어 |
| 적응형 스트리밍 | HLS 세그먼트 기반 ABR (Adaptive Bitrate) |
| 기본 컨트롤 | 재생/일시정지, 시크, 볼륨, 전체화면 |
| 재생 속도 | 0.5x, 1x, 1.25x, 1.5x, 2x |
| 이어보기 | 마지막 시청 위치 저장/복원 |

**스트리밍 아키텍처 권장안**:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    NAS      │────▶│   FFmpeg     │────▶│    HLS      │
│  (원본 MP4) │     │  Transcoder  │     │  Segments   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌───────────────────────────┘
                    │
              ┌─────▼─────┐     ┌──────────────┐
              │  Backend  │────▶│   Frontend   │
              │   (HLS    │     │  (Video.js)  │
              │  Proxy)   │     │              │
              └───────────┘     └──────────────┘
```

**HLS 트랜스코딩 프리셋**:

| Quality | Resolution | Bitrate | Segment |
|---------|------------|---------|---------|
| 1080p | 1920x1080 | 5 Mbps | 6초 |
| 720p | 1280x720 | 2.5 Mbps | 6초 |
| 480p | 854x480 | 1 Mbps | 6초 |
| 360p | 640x360 | 500 Kbps | 6초 |

#### F3. 핸드 타임코드 탐색
**Priority**: P0 (Must Have)

| 기능 | 설명 |
|------|------|
| 타임코드 마커 | 프로그레스 바에 핸드 시작 지점 표시 |
| 핸드 목록 | 영상 내 핸드 목록 표시 (사이드바) |
| 핸드 점프 | 특정 핸드로 즉시 이동 |
| 핸드 정보 | 플레이어, 팟 크기, 핸드 등급 표시 |
| 다음/이전 핸드 | 키보드 단축키로 핸드 간 이동 |

```typescript
interface Hand {
  id: number;
  file_id: string;
  start_sec: number;
  end_sec: number;
  players: string[];
  pot_size_bb?: number;
  hand_grade?: 'S' | 'A' | 'B' | 'C';
  tags?: string[];
  is_all_in?: boolean;
  is_showdown?: boolean;
}
```

### 4.2 Phase 2 Features

#### F4. 사용자 인증 (관리자 승인 기반)
**Priority**: P1

| 기능 | 설명 |
|------|------|
| 회원가입 | 아이디 / 비밀번호 / 비밀번호 확인 |
| 관리자 승인 | 가입 후 관리자 승인 대기 상태 |
| 세션 관리 | JWT 기반 인증, 7일 유효 |
| 사용자 프로필 | 닉네임, 선호 플레이어 설정 |

```typescript
// 회원가입 Flow
interface RegisterRequest {
  username: string;      // 아이디
  password: string;      // 비밀번호
  password_confirm: string;  // 비밀번호 확인
  display_name?: string; // 닉네임 (선택)
}

// 사용자 상태
type UserStatus = 'pending' | 'approved' | 'rejected' | 'suspended';
```

#### F5. 시청 기록 및 통계
**Priority**: P1

| 기능 | 설명 |
|------|------|
| 시청 기록 | 최근 시청 콘텐츠 목록 |
| 이어보기 | 진행률 기반 자동 이어보기 |
| 완료 표시 | 90% 이상 시청 시 완료 표시 |
| 통계 대시보드 | 총 시청 시간, 선호 카탈로그 등 |

#### F6. 개인화 추천 (규칙 기반)
**Priority**: P1

| 기능 | 설명 |
|------|------|
| 시청 기반 추천 | 시청 이력 분석 → 유사 콘텐츠 |
| 플레이어 팔로우 | 선호 플레이어 콘텐츠 우선 노출 |
| 트렌딩 | 인기 콘텐츠 실시간 표시 |
| 홈 구성 | 개인화된 홈 화면 Row 구성 |

**추천 규칙 예시**:

```python
def get_recommendations(user_id: int) -> list[Content]:
    rules = [
        # Rule 1: 선호 플레이어 콘텐츠
        ("favorite_players", 0.4),
        # Rule 2: 시청한 시리즈의 다른 에피소드
        ("same_series", 0.3),
        # Rule 3: 비슷한 핸드 등급
        ("similar_hand_grade", 0.2),
        # Rule 4: 인기 콘텐츠
        ("trending", 0.1),
    ]
    # ... 점수 기반 정렬
```

### 4.3 Phase 3 Features (Advanced Playback)

| 기능 | 설명 |
|------|------|
| **Hand-to-Hand Skip** | 핸드 사이 카드 섞는 구간 자동 스킵 |
| **하이라이트 모아보기** | 등급 높은 핸드(S, A)만 연속 재생 |
| **스마트 스킵** | 비핸드 구간 자동 감지 및 건너뛰기 |
| **핸드 등급 필터** | S/A/B/C 등급별 필터링 재생 |

**Hand-to-Hand Skip 상세**:

```typescript
interface SkipConfig {
  skip_shuffle: boolean;     // 카드 섞는 구간 스킵
  skip_breaks: boolean;      // 휴식 구간 스킵
  min_hand_grade: 'S' | 'A' | 'B' | 'C' | null;  // 최소 핸드 등급
  auto_next_hand: boolean;   // 핸드 종료 시 다음 핸드로 자동 이동
}

// 재생 모드
type PlaybackMode =
  | 'full'           // 전체 재생
  | 'hands_only'     // 핸드만 재생 (셔플 스킵)
  | 'highlights'     // S, A 등급만
  | 'custom';        // 사용자 설정
```

**스킵 버튼 UI (Netflix 스타일 오버레이)**:

비핸드 구간(카드 섞기, 휴식 등) 진입 시 플레이어 하단에 버튼 자동 표시:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                        Video Player                             │
│                                                                 │
│                                                                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   ┌──────────────────┐  ┌─────────────────────────┐    │   │
│  │   │  핸드 모아보기   │  │  하이라이트 핸드만 보기  │    │   │
│  │   │    (셔플 스킵)   │  │      (S, A 등급만)      │    │   │
│  │   └──────────────────┘  └─────────────────────────┘    │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ├──────────────────●───────────────────────────────────────┤  │
│  00:45:30                                           02:30:00   │
└─────────────────────────────────────────────────────────────────┘
```

**버튼 동작**:

| 버튼 | 동작 | 스킵 대상 |
|------|------|----------|
| **핸드 모아보기** | 다음 핸드 시작점으로 점프 | 카드 섞기, 휴식 구간 |
| **하이라이트 핸드만 보기** | S, A 등급 핸드만 연속 재생 | 셔플 + B, C 등급 핸드 |

**표시 조건**:

```typescript
interface SkipButtonConfig {
  // 버튼 표시 조건
  show_when: 'non_hand_segment';  // 비핸드 구간 진입 시
  auto_hide_after: 5;             // 5초 후 자동 숨김
  position: 'bottom-center';      // 플레이어 하단 중앙

  // 버튼 종류
  buttons: [
    {
      id: 'skip_to_hand',
      label: '핸드 모아보기',
      sublabel: '(셔플 스킵)',
      action: 'jump_to_next_hand'
    },
    {
      id: 'highlights_only',
      label: '하이라이트 핸드만 보기',
      sublabel: '(S, A 등급만)',
      action: 'enable_highlight_mode'
    }
  ]
}
```

**Svelte 컴포넌트 예시**:

```svelte
<!-- SkipButtons.svelte -->
<script>
  export let isNonHandSegment = false;
  export let onSkipToHand: () => void;
  export let onHighlightsOnly: () => void;

  let visible = false;
  let hideTimer: number;

  $: if (isNonHandSegment) {
    visible = true;
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => visible = false, 5000);
  }
</script>

{#if visible}
  <div class="skip-buttons" transition:fade>
    <button class="skip-btn" on:click={onSkipToHand}>
      <span class="label">핸드 모아보기</span>
      <span class="sublabel">(셔플 스킵)</span>
    </button>
    <button class="skip-btn highlight" on:click={onHighlightsOnly}>
      <span class="label">하이라이트 핸드만 보기</span>
      <span class="sublabel">(S, A 등급만)</span>
    </button>
  </div>
{/if}

<style>
  .skip-buttons {
    position: absolute;
    bottom: 80px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
  }
  .skip-btn {
    background: rgba(255, 255, 255, 0.95);
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    cursor: pointer;
    transition: transform 0.2s;
  }
  .skip-btn:hover {
    transform: scale(1.05);
  }
  .skip-btn.highlight {
    background: #e50914;  /* Netflix Red */
    color: white;
  }
</style>
```

---

## 5. Technical Requirements

### 5.1 Frontend Stack (권장: SvelteKit)

**선택 근거**:
- **번들 크기**: SvelteKit 런타임 1.6KB vs React 42KB - 빠른 초기 로드
- **TTI (Time to Interactive)**: 컴파일 타임 최적화로 빠른 인터랙션
- **성능**: 가상 DOM 없이 직접 DOM 조작 → 비디오 플레이어와 궁합 우수
- **학습 곡선**: 직관적인 문법, 빠른 개발 속도

**대안: Next.js**
- 생태계 성숙도가 필요한 경우
- Netflix, Hulu 등 비디오 플랫폼에서 검증된 스택
- React 개발자 채용 용이성

| 항목 | 선택 | 근거 |
|------|------|------|
| Framework | SvelteKit | 성능, 번들 크기 |
| Styling | Tailwind CSS | 유틸리티 기반, 빠른 개발 |
| Video Player | Video.js + HLS.js | 성숙한 생태계, HLS 지원 |
| State | Svelte Stores | 내장 상태 관리 |
| HTTP Client | Fetch API | 내장, 경량 |

```typescript
// SvelteKit 프로젝트 구조
wsoptv-frontend/
├── src/
│   ├── routes/
│   │   ├── +page.svelte           // 홈
│   │   ├── +layout.svelte         // 레이아웃
│   │   ├── catalog/[id]/          // 카탈로그 상세
│   │   ├── series/[id]/           // 시리즈 상세
│   │   ├── watch/[id]/            // 비디오 재생
│   │   ├── search/                // 검색
│   │   └── profile/               // 사용자 프로필
│   ├── lib/
│   │   ├── components/
│   │   │   ├── VideoPlayer.svelte
│   │   │   ├── HandTimeline.svelte
│   │   │   └── SearchBar.svelte
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   └── player.ts
│   │   └── api/
│   │       └── client.ts
│   └── app.html
├── static/
├── svelte.config.js
└── package.json
```

### 5.2 Backend Stack (FastAPI)

기존 archive-analyzer의 FastAPI 구조 확장:

```
wsoptv-backend/
├── src/
│   ├── main.py                    # FastAPI 앱
│   ├── api/
│   │   ├── v1/
│   │   │   ├── catalogs.py
│   │   │   ├── contents.py
│   │   │   ├── search.py
│   │   │   ├── streaming.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── recommendations.py
│   │   └── deps.py                # Dependencies
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── content.py
│   │   └── watch_history.py
│   ├── services/
│   │   ├── search_service.py
│   │   ├── streaming_service.py
│   │   └── recommendation_service.py
│   └── utils/
│       └── transcoder.py
├── tests/
├── requirements.txt
└── Dockerfile
```

### 5.3 Streaming Architecture (권장: HLS 하이브리드)

**선택 근거**:
- **호환성**: HLS는 모든 현대 브라우저/기기 지원
- **적응형 스트리밍**: 네트워크 상태에 따른 자동 품질 조절
- **세그먼트 캐싱**: 인기 콘텐츠 프리트랜스코딩으로 즉시 재생

**하이브리드 전략**:

```python
class StreamingStrategy:
    """스트리밍 전략 결정"""

    def get_strategy(self, content_id: str) -> str:
        view_count = self.get_view_count(content_id)

        if view_count > 100:
            # 인기 콘텐츠: 프리트랜스코딩된 HLS
            return "pre_transcoded_hls"
        else:
            # 비인기 콘텐츠: 온디맨드 트랜스코딩
            return "on_demand_hls"
```

**FFmpeg HLS 트랜스코딩 명령**:

```bash
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]split=4[v1][v2][v3][v4]; \
    [v1]scale=1920:1080[v1out]; \
    [v2]scale=1280:720[v2out]; \
    [v3]scale=854:480[v3out]; \
    [v4]scale=640:360[v4out]" \
  -map "[v1out]" -c:v:0 libx264 -b:v:0 5M \
  -map "[v2out]" -c:v:1 libx264 -b:v:1 2.5M \
  -map "[v3out]" -c:v:2 libx264 -b:v:2 1M \
  -map "[v4out]" -c:v:3 libx264 -b:v:3 500K \
  -map 0:a -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_list_size 0 \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0 v:3,a:0" \
  stream_%v/playlist.m3u8
```

### 5.4 Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.9'

networks:
  wsoptv-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  postgres-data:
  meili-data:
  redis-data:
  hls-segments:

services:
  # ============================================
  # Database Services
  # ============================================
  postgres:
    image: postgres:16-alpine
    container_name: wsoptv-postgres
    networks:
      wsoptv-network:
        ipv4_address: 172.28.1.1
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: wsoptv
      POSTGRES_USER: wsoptv
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-wsoptv_secret}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U wsoptv"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  meilisearch:
    image: getmeili/meilisearch:v1.6
    container_name: wsoptv-meili
    networks:
      wsoptv-network:
        ipv4_address: 172.28.1.2
    ports:
      - "7700:7700"
    environment:
      MEILI_MASTER_KEY: ${MEILI_MASTER_KEY:-wsoptv_meili_key}
      MEILI_ENV: development
    volumes:
      - meili-data:/meili_data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: wsoptv-redis
    networks:
      wsoptv-network:
        ipv4_address: 172.28.1.3
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ============================================
  # Application Services
  # ============================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: wsoptv-backend
    networks:
      wsoptv-network:
        ipv4_address: 172.28.2.1
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://wsoptv:${POSTGRES_PASSWORD:-wsoptv_secret}@postgres:5432/wsoptv
      MEILI_URL: http://meilisearch:7700
      MEILI_MASTER_KEY: ${MEILI_MASTER_KEY:-wsoptv_meili_key}
      REDIS_URL: redis://redis:6379/0
      NAS_MOUNT_PATH: /mnt/nas
      HLS_SEGMENTS_PATH: /hls-segments
    volumes:
      - /mnt/nas:/mnt/nas:ro                    # NAS 마운트 (읽기 전용)
      - hls-segments:/hls-segments              # HLS 세그먼트
    depends_on:
      postgres:
        condition: service_healthy
      meilisearch:
        condition: service_started
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: wsoptv-frontend
    networks:
      wsoptv-network:
        ipv4_address: 172.28.2.2
    ports:
      - "3000:3000"
    environment:
      PUBLIC_API_URL: http://backend:8001
      ORIGIN: http://localhost:3000
    depends_on:
      - backend
    restart: unless-stopped

  transcoder:
    image: jrottenberg/ffmpeg:6-alpine
    container_name: wsoptv-transcoder
    networks:
      wsoptv-network:
        ipv4_address: 172.28.2.3
    entrypoint: ["tail", "-f", "/dev/null"]     # Worker 대기 상태
    volumes:
      - /mnt/nas:/mnt/nas:ro
      - hls-segments:/hls-segments
    restart: unless-stopped

  # ============================================
  # Migration & Data Sync
  # ============================================
  migrator:
    build:
      context: ./backend
      dockerfile: Dockerfile.migrator
    container_name: wsoptv-migrator
    networks:
      - wsoptv-network
    environment:
      DATABASE_URL: postgresql://wsoptv:${POSTGRES_PASSWORD:-wsoptv_secret}@postgres:5432/wsoptv
      SQLITE_SOURCE: /data/pokervod.db
    volumes:
      - ./shared-data:/data:ro
    depends_on:
      postgres:
        condition: service_healthy
    profiles:
      - migrate                                 # docker compose --profile migrate up
```

### 5.5 Database Schema (PostgreSQL)

```sql
-- docker/postgres/init.sql
-- PostgreSQL 16 Schema for WSOPTV Platform

-- =====================================================
-- 1. Core Tables (기존 pokervod.db 마이그레이션)
-- =====================================================

CREATE TABLE IF NOT EXISTS catalogs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    display_title VARCHAR(300),
    title_source VARCHAR(20) DEFAULT 'rule_based',
    title_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS series (
    id SERIAL PRIMARY KEY,
    catalog_id VARCHAR(50) REFERENCES catalogs(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    season_num INTEGER,
    year INTEGER,
    description TEXT,
    episode_count INTEGER DEFAULT 0,
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    country VARCHAR(50),
    avatar_url TEXT,
    total_hands INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(200) PRIMARY KEY,
    nas_path TEXT UNIQUE NOT NULL,
    filename VARCHAR(500) NOT NULL,
    size_bytes BIGINT,
    duration_sec FLOAT,
    resolution VARCHAR(20),
    codec VARCHAR(50),
    fps FLOAT,
    bitrate_kbps INTEGER,
    hls_ready BOOLEAN DEFAULT FALSE,
    hls_path TEXT,
    analysis_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contents (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES series(id) ON DELETE CASCADE,
    file_id VARCHAR(200) REFERENCES files(id),
    episode_num INTEGER,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    duration_sec FLOAT,
    thumbnail_url TEXT,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hands (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    file_id VARCHAR(200) REFERENCES files(id),
    hand_number INTEGER,
    start_sec FLOAT NOT NULL,
    end_sec FLOAT NOT NULL,
    winner VARCHAR(100),
    pot_size_bb FLOAT,
    is_all_in BOOLEAN DEFAULT FALSE,
    is_showdown BOOLEAN DEFAULT FALSE,
    players TEXT[],
    cards_shown TEXT[],
    board TEXT,
    hand_grade VARCHAR(1) CHECK (hand_grade IN ('S', 'A', 'B', 'C')),
    tags TEXT[],
    highlight_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_players (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'featured',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(content_id, player_id)
);

CREATE TABLE IF NOT EXISTS content_tags (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(content_id, tag_id)
);

-- =====================================================
-- 2. User & Auth Tables
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,       -- 아이디
    password_hash VARCHAR(255) NOT NULL,        -- bcrypt 해시
    display_name VARCHAR(100),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
    approved_by INTEGER REFERENCES users(id),   -- 승인한 관리자
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- 관리자 승인 대기 목록 뷰
CREATE VIEW pending_users AS
SELECT id, username, display_name, created_at
FROM users
WHERE status = 'pending'
ORDER BY created_at ASC;

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    device_info TEXT,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 3. Watch History & Progress
-- =====================================================

CREATE TABLE IF NOT EXISTS watch_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES contents(id) ON DELETE CASCADE,
    progress_sec FLOAT NOT NULL,
    duration_sec FLOAT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, content_id)
);

CREATE TABLE IF NOT EXISTS view_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content_id INTEGER REFERENCES contents(id),
    session_id VARCHAR(64),
    event_type VARCHAR(20) NOT NULL,  -- 'play', 'pause', 'seek', 'complete'
    position_sec FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 4. Personalization
-- =====================================================

CREATE TABLE IF NOT EXISTS user_favorite_players (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, player_id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_quality VARCHAR(10) DEFAULT '1080p',
    autoplay BOOLEAN DEFAULT TRUE,
    preferred_catalogs TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendation_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recommendations JSONB NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 5. Indexes
-- =====================================================

-- Content Search
CREATE INDEX idx_contents_series ON contents(series_id);
CREATE INDEX idx_contents_file ON contents(file_id);
CREATE INDEX idx_contents_view_count ON contents(view_count DESC);

-- Hands
CREATE INDEX idx_hands_content ON hands(content_id);
CREATE INDEX idx_hands_file ON hands(file_id);
CREATE INDEX idx_hands_grade ON hands(hand_grade);
CREATE INDEX idx_hands_players ON hands USING GIN(players);
CREATE INDEX idx_hands_tags ON hands USING GIN(tags);
CREATE INDEX idx_hands_timecode ON hands(content_id, start_sec);

-- Users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

-- Watch Progress
CREATE INDEX idx_watch_progress_user ON watch_progress(user_id);
CREATE INDEX idx_watch_progress_updated ON watch_progress(updated_at DESC);

-- View Events (시계열)
CREATE INDEX idx_view_events_user_time ON view_events(user_id, created_at DESC);
CREATE INDEX idx_view_events_content ON view_events(content_id);

-- =====================================================
-- 6. Triggers
-- =====================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER files_updated_at
    BEFORE UPDATE ON files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER watch_progress_updated_at
    BEFORE UPDATE ON watch_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Increment view count
CREATE OR REPLACE FUNCTION increment_view_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.event_type = 'play' THEN
        UPDATE contents SET view_count = view_count + 1 WHERE id = NEW.content_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER view_event_count_trigger
    AFTER INSERT ON view_events
    FOR EACH ROW EXECUTE FUNCTION increment_view_count();
```

### 5.6 Search (MeiliSearch)

Docker 컨테이너에서 실행되는 MeiliSearch:

```python
# 인덱스 설정
SEARCH_INDEX_CONFIG = {
    "primaryKey": "id",
    "searchableAttributes": [
        "title",
        "description",
        "player_names",
        "tags",
        "catalog_name",
        "series_title"
    ],
    "filterableAttributes": [
        "catalog_id",
        "series_id",
        "player_ids",
        "hand_grade",
        "year",
        "duration_sec"
    ],
    "sortableAttributes": [
        "created_at",
        "view_count",
        "duration_sec"
    ],
    "rankingRules": [
        "words",
        "typo",
        "proximity",
        "attribute",
        "sort",
        "exactness"
    ]
}
```

---

## 6. UI/UX Design

### 6.0 Tone & Manner (WSOP 브랜드 가이드)

WSOP 공식 로고와 브랜드 아이덴티티에 맞춘 프리미엄 포커 플랫폼 디자인:

**브랜드 컬러 팔레트**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WSOPTV Color Palette                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Primary Colors (WSOP 시그니처)                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│  │  GOLD   │  │  BLACK  │  │   RED   │                         │
│  │ #D4AF37 │  │ #1A1A1A │  │ #C41E3A │                         │
│  │ 메인    │  │ 배경    │  │ 액센트  │                         │
│  └─────────┘  └─────────┘  └─────────┘                         │
│                                                                 │
│  Secondary Colors                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  CREAM  │  │  GRAY   │  │ BRONZE  │  │  WHITE  │           │
│  │ #F5F5DC │  │ #2D2D2D │  │ #CD7F32 │  │ #FFFFFF │           │
│  │ 텍스트  │  │ 카드    │  │ 보조    │  │ 강조    │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│                                                                 │
│  Semantic Colors                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│  │ SUCCESS │  │ WARNING │  │  ERROR  │                         │
│  │ #2E8B57 │  │ #DAA520 │  │ #DC143C │                         │
│  │ 승리    │  │ 올인    │  │ 패배    │                         │
│  └─────────┘  └─────────┘  └─────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**타이포그래피**:

| 용도 | 폰트 | 스타일 |
|------|------|--------|
| **로고/타이틀** | Cinzel, Trajan Pro | Bold, Uppercase |
| **헤딩** | Oswald, Montserrat | Semi-Bold |
| **본문** | Inter, Roboto | Regular, 16px |
| **숫자/통계** | Roboto Mono | Medium |

**디자인 원칙**:

| 원칙 | 적용 |
|------|------|
| **프리미엄** | 골드 액센트, 그라데이션, 미묘한 광택 효과 |
| **다크 모드 기본** | 블랙 배경 (#1A1A1A) + 크림 텍스트 |
| **클래식 & 모던** | 전통적 포커 요소 + 현대적 UI |
| **가독성** | 고대비, 충분한 여백, 명확한 계층 |

**컴포넌트 스타일**:

```css
/* Tailwind CSS 커스텀 테마 */
:root {
  /* WSOP Primary */
  --wsop-gold: #D4AF37;
  --wsop-gold-light: #E5C158;
  --wsop-gold-dark: #B8962E;

  /* Background */
  --wsop-black: #1A1A1A;
  --wsop-black-light: #2D2D2D;
  --wsop-black-dark: #0D0D0D;

  /* Accent */
  --wsop-red: #C41E3A;
  --wsop-bronze: #CD7F32;
  --wsop-cream: #F5F5DC;
}

/* 버튼 스타일 */
.btn-primary {
  background: linear-gradient(135deg, var(--wsop-gold), var(--wsop-gold-dark));
  color: var(--wsop-black);
  font-weight: 600;
  border: none;
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--wsop-gold-light), var(--wsop-gold));
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
}

/* 카드 스타일 */
.content-card {
  background: var(--wsop-black-light);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.content-card:hover {
  border-color: var(--wsop-gold);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  transform: translateY(-4px);
}

/* 핸드 등급 배지 */
.badge-grade-s { background: var(--wsop-gold); color: var(--wsop-black); }
.badge-grade-a { background: var(--wsop-red); color: white; }
.badge-grade-b { background: var(--wsop-bronze); color: white; }
.badge-grade-c { background: var(--wsop-black-light); color: var(--wsop-cream); }
```

**UI 예시 (다크 테마)**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ██████  WSOPTV                    [검색]        [프로필]       │
│  ██████                                           (Gold 아이콘)  │
├─────────────────────────────────────────────────────────────────┤
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░ HERO BANNER (Black + Gold Gradient) ░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│                          [▶ 시청하기] (Gold Button)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ━━ WSOP 2024 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ [더보기 →]   │
│  (Gold underline)                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │           │
│  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │           │
│  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │  │ ▓▓▓▓▓▓▓ │           │
│  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤           │
│  │Main Evnt│  │High Roll│  │  Day 3  │  │Final Tbl│           │
│  │ [S]Gold │  │ [A]Red  │  │ 2h 30m  │  │ 1h 45m  │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│  (Dark card with Gold border on hover)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Background: #1A1A1A (WSOP Black)
Text: #F5F5DC (Cream)
Accent: #D4AF37 (Gold)
```

**아이콘 스타일**:

| 아이콘 | 스타일 | 색상 |
|--------|--------|------|
| 재생 버튼 | Filled | Gold |
| 핸드 등급 | Badge | 등급별 |
| 네비게이션 | Outline | Cream |
| 플레이어 | Filled | Gold |
| 설정 | Outline | Cream |

**반응형 브레이크포인트**:

| 이름 | 너비 | 레이아웃 |
|------|------|----------|
| Mobile | < 640px | 단일 컬럼 |
| Tablet | 640px - 1024px | 2-3 컬럼 |
| Desktop | > 1024px | 4-5 컬럼 |
| TV/Large | > 1440px | 6+ 컬럼 |

### 6.1 홈페이지 레이아웃

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  [검색바                    ]  [프로필]                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Hero Banner (추천 콘텐츠)                │ │
│  │                                                           │ │
│  │   WSOP 2024 Main Event - Phil Ivey vs Daniel Negreanu    │ │
│  │                        [▶ 시청하기]                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  이어보기                                              [더보기] │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │  ▶  │ │     │ │     │ │     │ │     │                      │
│  │ 75% │ │ 30% │ │ 50% │ │ 10% │ │ 20% │                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
│                                                                 │
│  WSOP                                                  [더보기] │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │     │ │     │ │     │ │     │ │     │                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
│                                                                 │
│  HCL (High Stakes Poker)                               [더보기] │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │     │ │     │ │     │ │     │ │     │                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
│                                                                 │
│  추천 콘텐츠                                           [더보기] │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │     │ │     │ │     │ │     │ │     │                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 비디오 재생 페이지

```
┌─────────────────────────────────────────────────────────────────┐
│  [←] WSOP 2024 Main Event - Day 3                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │                     Video Player                          │ │
│  │                                                           │ │
│  │                         [▶]                               │ │
│  │                                                           │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ [▶] 00:45:30 / 02:30:00  [■■■●■■■■■■■■■■■] [🔊] [⚙] [⛶]│ │
│  │              ▲ ▲ ▲ ▲ ▲ ▲ ▲ (핸드 마커)                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────┬──────────────────────────────┐ │
│  │ 핸드 목록 (15)             │ 콘텐츠 정보                   │ │
│  │ ─────────────────────────  │ ──────────────────────────── │ │
│  │ ▶ #1 00:05:30 [S] All-in  │ WSOP 2024 Main Event         │ │
│  │   Phil Ivey vs Negreanu   │ Day 3 - Final Table          │ │
│  │                            │                              │ │
│  │ #2 00:12:45 [A] Bluff     │ 출연: Phil Ivey, Daniel      │ │
│  │   Hellmuth vs Dwan        │ Negreanu, Phil Hellmuth      │ │
│  │                            │                              │ │
│  │ #3 00:25:10 [A] Hero Call │ 재생시간: 2시간 30분          │ │
│  │   Antonius vs Ivey        │ 조회수: 1,234                 │ │
│  │                            │                              │ │
│  │ #4 00:35:00 [B] Fold      │ 태그: all-in, final-table    │ │
│  │   ...                     │                              │ │
│  └────────────────────────────┴──────────────────────────────┘ │
│                                                                 │
│  관련 콘텐츠                                                    │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                              │
│  │     │ │     │ │     │ │     │                              │
│  └─────┘ └─────┘ └─────┘ └─────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 검색 결과 페이지

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  [Phil Ivey                 🔍]  [프로필]               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │ 필터                │  │ "Phil Ivey" 검색 결과 (156건)   │  │
│  │ ─────────────────── │  │                                 │  │
│  │ 카탈로그            │  │ ┌─────────────────────────────┐ │  │
│  │ ☑ WSOP             │  │ │ [썸네일] Phil Ivey's        │ │  │
│  │ ☑ HCL              │  │ │          Legendary Bluff    │ │  │
│  │ ☐ PAD              │  │ │          WSOP 2024 | 15분   │ │  │
│  │                     │  │ │          [S] All-in        │ │  │
│  │ 핸드 등급           │  │ └─────────────────────────────┘ │  │
│  │ ☑ S (Must-Watch)   │  │ ┌─────────────────────────────┐ │  │
│  │ ☑ A (Great)        │  │ │ [썸네일] Ivey vs Dwan       │ │  │
│  │ ☐ B (Good)         │  │ │          High Stakes S10    │ │  │
│  │ ☐ C (Standard)     │  │ │          2시간 30분         │ │  │
│  │                     │  │ └─────────────────────────────┘ │  │
│  │ 연도                │  │ ┌─────────────────────────────┐ │  │
│  │ [2024    ▼]        │  │ │ ...                         │ │  │
│  │                     │  │ └─────────────────────────────┘ │  │
│  │ 재생시간            │  │                                 │  │
│  │ ○ 전체             │  │ [1] [2] [3] ... [16]            │  │
│  │ ○ 30분 미만        │  │                                 │  │
│  │ ○ 1시간 미만       │  │                                 │  │
│  │ ○ 1시간 이상       │  │                                 │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. API Specification

### 7.1 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/catalogs` | 카탈로그 목록 |
| GET | `/api/v1/catalogs/{id}` | 카탈로그 상세 |
| GET | `/api/v1/series` | 시리즈 목록 |
| GET | `/api/v1/series/{id}` | 시리즈 상세 |
| GET | `/api/v1/contents/{id}` | 콘텐츠 상세 |
| GET | `/api/v1/contents/{id}/hands` | 콘텐츠 핸드 목록 |
| GET | `/api/v1/search` | 검색 |
| GET | `/api/v1/stream/{id}` | HLS 스트리밍 |
| POST | `/api/v1/auth/login` | 로그인 |
| POST | `/api/v1/auth/register` | 회원가입 (초대 코드) |
| GET | `/api/v1/users/me` | 현재 사용자 |
| GET | `/api/v1/users/me/watch-history` | 시청 기록 |
| POST | `/api/v1/users/me/watch-progress` | 시청 진행률 저장 |
| GET | `/api/v1/recommendations` | 추천 콘텐츠 |

### 7.2 API Examples

```typescript
// GET /api/v1/contents/{id}
{
  "id": 123,
  "title": "WSOP 2024 Main Event - Day 3",
  "series": {
    "id": 5,
    "title": "WSOP 2024",
    "catalog_id": "wsop"
  },
  "duration_sec": 9000,
  "players": [
    {"id": 1, "name": "Phil Ivey"},
    {"id": 2, "name": "Daniel Negreanu"}
  ],
  "tags": ["final-table", "all-in"],
  "hands_count": 15,
  "view_count": 1234,
  "stream_url": "/api/v1/stream/123/master.m3u8"
}

// GET /api/v1/contents/{id}/hands
{
  "hands": [
    {
      "id": 1,
      "start_sec": 330,
      "end_sec": 420,
      "players": ["Phil Ivey", "Daniel Negreanu"],
      "hand_grade": "S",
      "tags": ["all-in", "bluff"],
      "pot_size_bb": 1500
    },
    // ...
  ]
}

// GET /api/v1/search?q=Phil+Ivey&catalog_id=wsop&hand_grade=S
{
  "results": [...],
  "total": 156,
  "facets": {
    "catalogs": {"wsop": 100, "hcl": 56},
    "hand_grades": {"S": 30, "A": 80, "B": 46}
  }
}
```

---

## 8. Non-Functional Requirements

### 8.1 Performance

| Metric | Target |
|--------|--------|
| 초기 페이지 로드 | < 2초 |
| 검색 응답 시간 | < 200ms |
| 비디오 버퍼링 시작 | < 3초 |
| Time to Interactive | < 1.5초 |

### 8.2 Scalability

| Metric | Target |
|--------|--------|
| 동시 사용자 | 100명 (Phase 1) |
| 콘텐츠 수 | 3,000+ |
| 저장 용량 | 18TB+ |

### 8.3 Security

| 항목 | 구현 |
|------|------|
| 인증 | JWT (HS256) |
| 세션 유효기간 | 7일 |
| 초대 코드 | 32자 랜덤 문자열, 7일 만료 |
| API Rate Limiting | 100 req/min per user |
| HTTPS | 필수 |

### 8.4 Browser Support

| Browser | Version |
|---------|---------|
| Chrome | 90+ |
| Firefox | 90+ |
| Safari | 14+ |
| Edge | 90+ |

---

## 9. Development Phases

### Phase 1: MVP (Core Features)

**기간**: TBD
**목표**: 기본 VOD 플랫폼 기능

| 작업 | 우선순위 |
|------|----------|
| 프로젝트 셋업 (SvelteKit + FastAPI) | P0 |
| 카탈로그/시리즈/콘텐츠 API | P0 |
| MeiliSearch 검색 통합 | P0 |
| HLS 스트리밍 프록시 | P0 |
| Video.js 플레이어 | P0 |
| 핸드 타임코드 UI | P0 |
| 기본 UI/UX | P0 |

### Phase 2: User Features

**기간**: TBD
**목표**: 사용자 기능 및 개인화

| 작업 | 우선순위 |
|------|----------|
| 초대 기반 인증 | P1 |
| Google OAuth | P1 |
| 시청 기록 저장 | P1 |
| 이어보기 기능 | P1 |
| 규칙 기반 추천 | P1 |
| 홈 화면 개인화 | P1 |

### Phase 3: Enhancement

**기간**: TBD
**목표**: 고급 기능 및 AI 통합

| 작업 | 우선순위 |
|------|----------|
| ML 추천 (Gorse) | P2 |
| AI 하이라이트 | P2 |
| 소셜 기능 | P2 |
| 모바일 최적화 | P2 |
| 분석 대시보드 | P2 |

---

## 10. Success Metrics

### 10.1 Key Performance Indicators (KPIs)

| Metric | Target (Phase 1) |
|--------|------------------|
| 월간 활성 사용자 (MAU) | 50+ |
| 평균 세션 시간 | 30분+ |
| 콘텐츠 완료율 | 40%+ |
| 검색 성공률 | 80%+ |
| 핸드 점프 사용률 | 60%+ |

### 10.2 User Satisfaction

| Metric | Target |
|--------|--------|
| NPS (Net Promoter Score) | 40+ |
| 버퍼링 불만 | < 5% |
| 검색 만족도 | 4.0/5.0+ |

---

## 11. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 대용량 파일 스트리밍 성능 | High | High | HLS 세그먼트 캐싱, CDN 검토 |
| 트랜스코딩 지연 | Medium | Medium | 인기 콘텐츠 프리트랜스코딩 |
| 사용자 확보 | Medium | High | 초대 기반으로 품질 유지 |
| 저작권 이슈 | Low | High | 초대 기반 비공개 운영 |

---

## 12. Appendix

### 12.1 기술 리서치 출처

- [SvelteKit vs Next.js 2025 비교](https://prismic.io/blog/sveltekit-vs-nextjs)
- [HLS 스트리밍 가이드 2025](https://www.videosdk.live/developer-hub/hls/hls-live-streaming)
- [Media Server Hosting 가이드](https://www.videosdk.live/developer-hub/media-server/media-server-hosting)
- [Open Source Streaming Server](https://datarhei.com/)
- [VOD Platform Content Patterns](D:\AI\claude01\archive-analyzer\docs\VOD_PLATFORM_CONTENT_PATTERNS.md)

### 12.2 Docker 인프라

| 컴포넌트 | 컨테이너명 | 포트 | IP (내부) |
|----------|------------|------|-----------|
| PostgreSQL | wsoptv-postgres | 5432 | 172.28.1.1 |
| MeiliSearch | wsoptv-meili | 7700 | 172.28.1.2 |
| Redis | wsoptv-redis | 6379 | 172.28.1.3 |
| Backend | wsoptv-backend | 8001 | 172.28.2.1 |
| Frontend | wsoptv-frontend | 3000 | 172.28.2.2 |
| Transcoder | wsoptv-transcoder | - | 172.28.2.3 |

### 12.3 Docker 명령어

```bash
# 전체 서비스 시작
docker compose up -d

# 로그 확인
docker compose logs -f backend

# 개별 서비스 재시작
docker compose restart backend

# PostgreSQL 접속
docker exec -it wsoptv-postgres psql -U wsoptv -d wsoptv

# SQLite → PostgreSQL 마이그레이션 (최초 1회)
docker compose --profile migrate up migrator

# HLS 트랜스코딩 실행
docker exec wsoptv-transcoder ffmpeg -i /mnt/nas/path/to/video.mp4 \
  -c:v libx264 -c:a aac -f hls \
  -hls_time 6 -hls_list_size 0 \
  /hls-segments/video_id/playlist.m3u8

# 볼륨 백업
docker run --rm -v wsoptv_postgres-data:/data -v $(pwd):/backup \
  alpine tar cvf /backup/postgres-backup.tar /data

# 전체 중지 및 정리
docker compose down
docker compose down -v  # 볼륨 포함 삭제 (주의!)
```

### 12.4 로컬 네트워크 구성

```
┌─────────────────────────────────────────────────────────────────┐
│                     Host Machine (Windows)                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Docker Network: wsoptv-network                 │ │
│  │                  Subnet: 172.28.0.0/16                      │ │
│  │                                                              │ │
│  │  Database Tier (172.28.1.x)                                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │ │
│  │  │PostgreSQL│  │MeiliSearch│ │  Redis   │                  │ │
│  │  │ .1.1     │  │  .1.2    │  │  .1.3    │                  │ │
│  │  └──────────┘  └──────────┘  └──────────┘                  │ │
│  │                                                              │ │
│  │  Application Tier (172.28.2.x)                              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │ │
│  │  │ Backend  │  │ Frontend │  │Transcoder│                  │ │
│  │  │  .2.1    │  │  .2.2    │  │  .2.3    │                  │ │
│  │  └──────────┘  └──────────┘  └──────────┘                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Exposed Ports:                                                  │
│  ├── localhost:3000  → Frontend                                  │
│  ├── localhost:8001  → Backend API                               │
│  ├── localhost:5432  → PostgreSQL                                │
│  ├── localhost:7700  → MeiliSearch                               │
│  └── localhost:6379  → Redis                                     │
│                                                                  │
│  Volume Mounts:                                                  │
│  ├── //10.10.100.122/GGPNAs/ARCHIVE → /mnt/nas (read-only)      │
│  └── D:/AI/claude01/shared-data → /data (migrator only)         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 12.5 기존 데이터 마이그레이션 (pokervod.db → PostgreSQL)

```python
# backend/scripts/migrate_sqlite_to_postgres.py
"""
SQLite(pokervod.db) → PostgreSQL 마이그레이션 스크립트
실행: docker compose --profile migrate up migrator
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch

SQLITE_PATH = "/data/pokervod.db"
PG_DSN = "postgresql://wsoptv:wsoptv_secret@postgres:5432/wsoptv"

TABLES_TO_MIGRATE = [
    "catalogs",
    "series",
    "players",
    "files",
    "contents",
    "content_players",
    "content_tags",
    "tags",
    "hands",
]

def migrate():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(PG_DSN)

    for table in TABLES_TO_MIGRATE:
        print(f"Migrating {table}...")
        cursor = sqlite_conn.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            continue

        columns = [desc[0] for desc in cursor.description]
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """

        with pg_conn.cursor() as pg_cursor:
            execute_batch(pg_cursor, insert_sql, [tuple(row) for row in rows])

        pg_conn.commit()
        print(f"  Migrated {len(rows)} rows")

    sqlite_conn.close()
    pg_conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
```

### 12.6 데이터 현황

| 항목 | 수량 |
|------|------|
| 총 파일 | 2,100+ |
| 총 용량 | 18TB+ |
| Series | 12개 |
| Contents | 2,938개 |
| Players | 833개 |
| Tags | 5개 |

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-09 | Claude Code | Initial draft |
| 1.1.0 | 2025-12-09 | Claude Code | Docker 기반 로컬 네트워크 아키텍처 적용, SQLite → PostgreSQL 변경 |
| 1.2.0 | 2025-12-09 | Claude Code | 인증 방식 변경 (초대→관리자승인), Phase 3 핸드 스킵 기능 추가, 스트리밍 중계 구조 명확화 |
| 1.3.0 | 2025-12-09 | Claude Code | WSOP 브랜드 톤앤매너 가이드 추가 (컬러, 타이포, 컴포넌트 스타일) |

---

**Next Steps**: `/todo` 실행하여 작업 목록 생성
