# LLD: Modules (패키지 상세 설계)

**Version**: 2.0.0 | **Master**: [0001-lld-wsoptv-platform.md](./0001-lld-wsoptv-platform.md)

---

## 1. @wsoptv/types

공유 타입 정의 패키지. 모든 패키지의 기반.

### 1.1 Core Entities

```typescript
// packages/types/src/entities.ts

export interface Catalog {
  id: string;                    // 'wsop', 'hcl', 'pad'
  name: string;
  displayTitle: string;
  description?: string;
  thumbnailUrl?: string;
}

export interface Series {
  id: number;
  catalogId: string;
  title: string;
  year: number;
  seasonNum?: number;
  episodeCount: number;
  description?: string;
  thumbnailUrl?: string;
}

export interface Content {
  id: number;
  seriesId: number;
  fileId: string;
  episodeNum?: number;
  title: string;
  description?: string;
  durationSec: number;
  viewCount: number;
  thumbnailUrl?: string;
  createdAt: string;
}

export interface Hand {
  id: number;
  contentId: number;
  fileId: string;
  handNumber?: number;
  startSec: number;
  endSec: number;
  players: string[];
  winner?: string;
  potSizeBb?: number;
  grade: HandGrade;
  isAllIn: boolean;
  isShowdown: boolean;
  cardsShown?: string[];
  board?: string;
  tags: string[];
  highlightScore: number;
}

export type HandGrade = 'S' | 'A' | 'B' | 'C';

export interface Player {
  id: number;
  name: string;
  displayName: string;
  country?: string;
  avatarUrl?: string;
  totalHands: number;
  totalWins: number;
}

export interface File {
  id: string;
  nasPath: string;
  filename: string;
  sizeBytes: number;
  durationSec: number;
  resolution: string;
  codec: string;
  fps: number;
  bitrateKbps: number;
  hlsReady: boolean;
  hlsPath?: string;
}
```

### 1.2 User & Auth

```typescript
// packages/types/src/auth.ts

export interface User {
  id: number;
  username: string;
  displayName?: string;
  avatarUrl?: string;
  role: UserRole;
  status: UserStatus;
  createdAt: string;
  lastLoginAt?: string;
}

export type UserRole = 'user' | 'admin';
export type UserStatus = 'pending' | 'approved' | 'rejected' | 'suspended';

export interface Session {
  userId: number;
  token: string;
  refreshToken: string;  // Refresh Token 추가 (#12)
  expiresAt: string;
  deviceInfo?: string;
}

export interface WatchProgress {
  userId: number;
  contentId: number;
  progressSec: number;
  durationSec: number;
  completed: boolean;
  updatedAt: string;
  version: number;  // Race Condition 방지용 (#7)
}
```

### 1.3 Validation Schema (Input Validation #3)

```typescript
// packages/types/src/validation.ts

import { z } from 'zod';

// 사용자명: 4-50자, 영문/숫자/밑줄만
export const usernameSchema = z
  .string()
  .min(4, '아이디는 4자 이상이어야 합니다')
  .max(50, '아이디는 50자 이하여야 합니다')
  .regex(/^[a-zA-Z0-9_]+$/, '영문, 숫자, 밑줄만 사용 가능합니다');

// 비밀번호: 8자 이상, 대소문자+숫자 (#13)
export const passwordSchema = z
  .string()
  .min(8, '비밀번호는 8자 이상이어야 합니다')
  .max(128, '비밀번호는 128자 이하여야 합니다')
  .regex(/[A-Z]/, '대문자를 포함해야 합니다')
  .regex(/[a-z]/, '소문자를 포함해야 합니다')
  .regex(/[0-9]/, '숫자를 포함해야 합니다')
  .refine(
    (val) => !['password', '12345678', 'qwerty'].some(p => val.toLowerCase().includes(p)),
    '너무 쉬운 비밀번호입니다'
  );

export const registerRequestSchema = z.object({
  username: usernameSchema,
  password: passwordSchema,
  passwordConfirm: z.string(),
  displayName: z.string().min(2).max(100).optional()
}).refine(
  (data) => data.password === data.passwordConfirm,
  { message: '비밀번호가 일치하지 않습니다', path: ['passwordConfirm'] }
);

export const loginRequestSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1)
});

export const progressRequestSchema = z.object({
  contentId: z.number().int().positive(),
  progressSec: z.number().min(0),
  durationSec: z.number().positive(),
  version: z.number().int().optional()  // Optimistic Locking (#7)
});

export const searchRequestSchema = z.object({
  q: z.string().min(2).max(200),
  catalogId: z.string().optional(),
  playerId: z.number().int().positive().optional(),
  handGrade: z.enum(['S', 'A', 'B', 'C']).optional(),
  year: z.number().int().min(1970).max(2030).optional(),
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
  sort: z.enum(['relevance', 'date', 'views']).default('relevance')
});
```

### 1.4 HandSegment (통합 정의 #17)

```typescript
// packages/types/src/player.ts
// 단일 정의 - 모든 패키지에서 이 타입을 import

export interface HandSegment {
  type: 'hand' | 'shuffle' | 'break';
  startSec: number;
  endSec: number;
  hand?: Hand;
}
```

### 1.5 API Types

```typescript
// packages/types/src/api.ts

export interface ApiResponse<T> {
  data: T;
  meta?: {
    timestamp: string;
    requestId: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: string;
  path: string;
}

// 검색 필터 - 우선순위 명시 (#25)
export interface SearchFilters {
  catalogId?: string;      // 1순위: 카탈로그
  playerId?: number;       // 2순위: 플레이어
  handGrade?: HandGrade;   // 3순위: 핸드 등급
  year?: number;           // 4순위: 연도
  minDuration?: number;
  maxDuration?: number;
}

export interface SearchResult {
  results: Content[];
  total: number;
  facets: SearchFacets;
}

export interface SearchFacets {
  catalogs: Record<string, number>;
  players: Record<string, number>;
  handGrades: Record<string, number>;
  years: Record<number, number>;
}
```

---

## 2. @wsoptv/config

공유 설정 패키지.

```typescript
// packages/config/src/index.ts

export interface AppConfig {
  api: ApiConfig;
  player: PlayerDefaults;
  search: SearchConfig;
  auth: AuthConfig;
  security: SecurityConfig;  // 보안 설정 추가
  streaming: StreamingConfig;  // 스트리밍 설정 추가
}

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryCount: number;
}

export interface PlayerDefaults {
  autoplay: boolean;
  defaultQuality: VideoQuality;
  defaultPlaybackRate: number;
  skipButtonDelay: number;
  skipButtonDuration: number;
}

export type VideoQuality = '360p' | '480p' | '720p' | '1080p' | 'auto';

export interface SearchConfig {
  debounceMs: number;
  minQueryLength: number;
  defaultLimit: number;
  maxLimit: number;
}

// 인증 설정 - 환경별 분리 (#22)
export interface AuthConfig {
  accessTokenExpiry: number;   // 분 단위
  refreshTokenExpiry: number;  // 일 단위
  refreshThreshold: number;    // 시간 단위 - 이 시간 전에 갱신
}

// 보안 설정 (#5, #11, #14, #23)
export interface SecurityConfig {
  jwt: {
    algorithm: 'HS256';
    secretKeyEnv: 'JWT_SECRET';  // 환경변수 이름
    issuer: 'wsoptv';
    audience: 'wsoptv-client';
  };
  password: {
    algorithm: 'bcrypt';
    costFactor: 12;
    minLength: 8;
    maxLength: 128;
    requireUppercase: true;
    requireLowercase: true;
    requireDigit: true;
  };
  rateLimiting: {
    login: { requests: 5, windowMs: 60000 };       // 5회/분
    register: { requests: 3, windowMs: 3600000 };  // 3회/시간
    api: { requests: 100, windowMs: 60000 };       // 100회/분
    search: { requests: 30, windowMs: 60000 };     // 30회/분
    stream: { requests: 10, windowMs: 60000 };     // 10회/분
  };
  csrf: {
    enabled: true;
    cookieName: 'csrf_token';
    headerName: 'X-CSRF-Token';
  };
  https: {
    required: boolean;  // production에서 true
    hsts: {
      enabled: true;
      maxAge: 31536000;
      includeSubDomains: true;
    };
  };
}

// 스트리밍 설정 (#20, #29, #32)
export interface StreamingConfig {
  ffmpeg: {
    hwAccel: 'none' | 'cuda' | 'vaapi' | 'qsv';  // 하드웨어 가속 (#20)
    preset: 'ultrafast' | 'fast' | 'medium' | 'slow';
    threads: number;
  };
  hls: {
    segmentDuration: 6;
    playlistSize: 0;
    qualities: QualityConfig[];
  };
  cache: {
    manifestTtl: 3600;     // 1시간 (#29)
    segmentTtl: 86400;     // 24시간
    invalidateOnSourceChange: true;
  };
}

export interface QualityConfig {
  name: string;
  width: number;
  height: number;
  videoBitrate: string;
  audioBitrate: string;  // 오디오 비트레이트 명시 (#32)
}

// 환경별 기본값
export const defaultConfig: Record<'development' | 'production', AppConfig> = {
  development: {
    api: { baseUrl: '/api/v1', timeout: 30000, retryCount: 3 },
    player: {
      autoplay: true,
      defaultQuality: 'auto',
      defaultPlaybackRate: 1,
      skipButtonDelay: 500,
      skipButtonDuration: 5000
    },
    search: { debounceMs: 300, minQueryLength: 2, defaultLimit: 20, maxLimit: 100 },
    auth: {
      accessTokenExpiry: 1440,   // 24시간 (개발)
      refreshTokenExpiry: 30,    // 30일
      refreshThreshold: 12
    },
    security: {
      jwt: { algorithm: 'HS256', secretKeyEnv: 'JWT_SECRET', issuer: 'wsoptv', audience: 'wsoptv-client' },
      password: { algorithm: 'bcrypt', costFactor: 12, minLength: 8, maxLength: 128, requireUppercase: true, requireLowercase: true, requireDigit: true },
      rateLimiting: {
        login: { requests: 10, windowMs: 60000 },
        register: { requests: 10, windowMs: 3600000 },
        api: { requests: 1000, windowMs: 60000 },
        search: { requests: 100, windowMs: 60000 },
        stream: { requests: 50, windowMs: 60000 }
      },
      csrf: { enabled: false, cookieName: 'csrf_token', headerName: 'X-CSRF-Token' },
      https: { required: false, hsts: { enabled: false, maxAge: 0, includeSubDomains: false } }
    },
    streaming: {
      ffmpeg: { hwAccel: 'none', preset: 'fast', threads: 4 },
      hls: {
        segmentDuration: 6,
        playlistSize: 0,
        qualities: [
          { name: '720p', width: 1280, height: 720, videoBitrate: '2.5M', audioBitrate: '128k' },
          { name: '480p', width: 854, height: 480, videoBitrate: '1M', audioBitrate: '96k' },
          { name: '360p', width: 640, height: 360, videoBitrate: '500k', audioBitrate: '64k' }
        ]
      },
      cache: { manifestTtl: 3600, segmentTtl: 86400, invalidateOnSourceChange: true }
    }
  },
  production: {
    api: { baseUrl: '/api/v1', timeout: 30000, retryCount: 3 },
    player: {
      autoplay: true,
      defaultQuality: 'auto',
      defaultPlaybackRate: 1,
      skipButtonDelay: 500,
      skipButtonDuration: 5000
    },
    search: { debounceMs: 300, minQueryLength: 2, defaultLimit: 20, maxLimit: 100 },
    auth: {
      accessTokenExpiry: 15,     // 15분 (프로덕션)
      refreshTokenExpiry: 7,     // 7일
      refreshThreshold: 1
    },
    security: {
      jwt: { algorithm: 'HS256', secretKeyEnv: 'JWT_SECRET', issuer: 'wsoptv', audience: 'wsoptv-client' },
      password: { algorithm: 'bcrypt', costFactor: 12, minLength: 8, maxLength: 128, requireUppercase: true, requireLowercase: true, requireDigit: true },
      rateLimiting: {
        login: { requests: 5, windowMs: 60000 },
        register: { requests: 3, windowMs: 3600000 },
        api: { requests: 100, windowMs: 60000 },
        search: { requests: 30, windowMs: 60000 },
        stream: { requests: 10, windowMs: 60000 }
      },
      csrf: { enabled: true, cookieName: 'csrf_token', headerName: 'X-CSRF-Token' },
      https: { required: true, hsts: { enabled: true, maxAge: 31536000, includeSubDomains: true } }
    },
    streaming: {
      ffmpeg: { hwAccel: 'cuda', preset: 'medium', threads: 8 },  // GPU 가속 (#20)
      hls: {
        segmentDuration: 6,
        playlistSize: 0,
        qualities: [
          { name: '1080p', width: 1920, height: 1080, videoBitrate: '5M', audioBitrate: '128k' },
          { name: '720p', width: 1280, height: 720, videoBitrate: '2.5M', audioBitrate: '128k' },
          { name: '480p', width: 854, height: 480, videoBitrate: '1M', audioBitrate: '96k' },
          { name: '360p', width: 640, height: 360, videoBitrate: '500k', audioBitrate: '64k' }
        ]
      },
      cache: { manifestTtl: 3600, segmentTtl: 86400, invalidateOnSourceChange: true }
    }
  }
};
```

---

## 3. @wsoptv/player

비디오 플레이어 핵심 로직.

### 3.1 Types

```typescript
// packages/player/src/types.ts

import type { Hand } from '@wsoptv/types';
import type { HandSegment } from '@wsoptv/types';  // 통합 타입 사용 (#17)

export interface PlayerConfig {
  autoplay: boolean;
  quality: VideoQuality;
  playbackRate: number;
  volume: number;
  muted: boolean;
  skipConfig: SkipConfig;
  highlightModeConfig: HighlightModeConfig;  // 하이라이트 모드 설정 (#26)
}

export interface SkipConfig {
  enabled: boolean;
  skipShuffle: boolean;
  minHandGrade: HandGrade | null;
  autoNextHand: boolean;
  showSkipButtons: boolean;
}

// 하이라이트 모드 설정 (#26)
export interface HighlightModeConfig {
  enabled: boolean;
  minGrade: 'S' | 'A';
  onComplete: 'stop' | 'loop' | 'normal';  // 마지막 핸드 종료 후 동작
}

export interface PlayerState {
  status: 'idle' | 'loading' | 'playing' | 'paused' | 'ended' | 'error';
  currentTime: number;
  duration: number;
  buffered: TimeRange[];
  quality: VideoQuality;
  availableQualities: VideoQuality[];
  volume: number;
  muted: boolean;
  playbackRate: number;
  error?: PlayerError;
  highlightMode: boolean;  // 하이라이트 모드 상태
}

export interface TimeRange {
  start: number;
  end: number;
}

export interface PlayerError {
  code: string;
  message: string;
  recoverable: boolean;
}

export interface PlayerCallbacks {
  onStateChange?: (state: PlayerState) => void;
  onTimeUpdate?: (time: number) => void;
  onHandEnter?: (hand: Hand) => void;
  onHandExit?: (hand: Hand) => void;
  onNonHandSegment?: (segment: HandSegment) => void;
  onHighlightComplete?: () => void;  // 하이라이트 모드 종료 (#26)
  onError?: (error: PlayerError) => void;
}
```

### 3.2 Player Controller

```typescript
// packages/player/src/controller.ts

import Hls from 'hls.js';
import type { Hand } from '@wsoptv/types';
import type { PlayerConfig, PlayerState, PlayerCallbacks } from './types';
import type { HandSegment } from '@wsoptv/types';
import { buildTimeline, findCurrentSegment, TimelineIndex } from '@wsoptv/hands';

export class PlayerController {
  private video: HTMLVideoElement;
  private hls: Hls | null = null;
  private config: PlayerConfig;
  private callbacks: PlayerCallbacks;
  private hands: Hand[] = [];
  private timeline: HandSegment[] = [];
  private timelineIndex: TimelineIndex;  // 최적화된 인덱스 (#21)
  private currentSegment: HandSegment | null = null;
  private highlightHands: Hand[] = [];
  private highlightIndex: number = 0;

  constructor(
    video: HTMLVideoElement,
    config: Partial<PlayerConfig>,
    callbacks: PlayerCallbacks
  ) {
    this.video = video;
    this.config = { ...defaultPlayerConfig, ...config };
    this.callbacks = callbacks;
    this.timelineIndex = new TimelineIndex([]);
    this.setupEventListeners();
  }

  async loadSource(src: string, hands: Hand[] = []): Promise<void> {
    this.hands = hands;
    this.timeline = buildTimeline(hands, 0);
    this.timelineIndex = new TimelineIndex(this.timeline);

    if (Hls.isSupported()) {
      this.hls = new Hls({
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        startLevel: -1
      });
      this.hls.loadSource(src);
      this.hls.attachMedia(this.video);

      return new Promise((resolve, reject) => {
        this.hls!.on(Hls.Events.MANIFEST_PARSED, () => {
          this.timeline = buildTimeline(hands, this.video.duration);
          this.timelineIndex = new TimelineIndex(this.timeline);
          resolve();
        });
        this.hls!.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal) reject(new Error(data.details));
        });
      });
    } else if (this.video.canPlayType('application/vnd.apple.mpegurl')) {
      this.video.src = src;
      return new Promise(resolve => {
        this.video.addEventListener('loadedmetadata', () => {
          this.timeline = buildTimeline(hands, this.video.duration);
          this.timelineIndex = new TimelineIndex(this.timeline);
          resolve();
        }, { once: true });
      });
    }
  }

  play(): void { this.video.play(); }
  pause(): void { this.video.pause(); }
  seek(time: number): void { this.video.currentTime = time; }

  seekToHand(handId: number): void {
    const hand = this.hands.find(h => h.id === handId);
    if (hand) this.seek(hand.startSec);
  }

  skipToNextHand(): void {
    const next = this.hands.find(h => h.startSec > this.video.currentTime);
    if (next) this.seek(next.startSec);
  }

  skipToPrevHand(): void {
    const prev = [...this.hands]
      .reverse()
      .find(h => h.endSec < this.video.currentTime);
    if (prev) this.seek(prev.startSec);
  }

  // 하이라이트 모드 (#26)
  enableHighlightMode(minGrade: 'S' | 'A' = 'A'): void {
    const gradeOrder = { S: 0, A: 1, B: 2, C: 3 };
    this.highlightHands = this.hands
      .filter(h => gradeOrder[h.grade] <= gradeOrder[minGrade])
      .sort((a, b) => a.startSec - b.startSec);

    this.highlightIndex = 0;
    if (this.highlightHands.length > 0) {
      this.seek(this.highlightHands[0].startSec);
    }
  }

  disableHighlightMode(): void {
    this.highlightHands = [];
    this.highlightIndex = 0;
  }

  setQuality(quality: VideoQuality): void {
    if (!this.hls) return;
    const levelIndex = this.hls.levels.findIndex(l =>
      `${l.height}p` === quality
    );
    if (levelIndex >= 0) this.hls.currentLevel = levelIndex;
  }

  private setupEventListeners(): void {
    this.video.addEventListener('timeupdate', this.handleTimeUpdate.bind(this));
    this.video.addEventListener('play', () => this.notifyStateChange());
    this.video.addEventListener('pause', () => this.notifyStateChange());
    this.video.addEventListener('ended', () => this.notifyStateChange());
  }

  private handleTimeUpdate(): void {
    const time = this.video.currentTime;
    this.callbacks.onTimeUpdate?.(time);

    // 최적화된 세그먼트 탐색 (#21)
    const segment = this.timelineIndex.find(time);

    if (segment !== this.currentSegment) {
      if (this.currentSegment?.type === 'hand' && this.currentSegment.hand) {
        this.callbacks.onHandExit?.(this.currentSegment.hand);

        // 하이라이트 모드에서 핸드 종료 처리 (#26)
        if (this.highlightHands.length > 0) {
          this.handleHighlightHandEnd();
        }
      }

      this.currentSegment = segment;

      if (segment?.type === 'hand' && segment.hand) {
        this.callbacks.onHandEnter?.(segment.hand);
      } else if (segment?.type === 'shuffle' || segment?.type === 'break') {
        this.callbacks.onNonHandSegment?.(segment);
      }
    }
  }

  // 하이라이트 모드 핸드 종료 처리 (#26)
  private handleHighlightHandEnd(): void {
    this.highlightIndex++;

    if (this.highlightIndex >= this.highlightHands.length) {
      const { onComplete } = this.config.highlightModeConfig;

      switch (onComplete) {
        case 'stop':
          this.pause();
          this.callbacks.onHighlightComplete?.();
          break;
        case 'loop':
          this.highlightIndex = 0;
          this.seek(this.highlightHands[0].startSec);
          break;
        case 'normal':
          this.disableHighlightMode();
          break;
      }
    } else {
      this.seek(this.highlightHands[this.highlightIndex].startSec);
    }
  }

  private notifyStateChange(): void {
    this.callbacks.onStateChange?.(this.getState());
  }

  getState(): PlayerState {
    return {
      status: this.video.paused ? 'paused' : 'playing',
      currentTime: this.video.currentTime,
      duration: this.video.duration,
      buffered: this.getBufferedRanges(),
      quality: this.getCurrentQuality(),
      availableQualities: this.getAvailableQualities(),
      volume: this.video.volume,
      muted: this.video.muted,
      playbackRate: this.video.playbackRate,
      highlightMode: this.highlightHands.length > 0
    };
  }

  destroy(): void {
    this.hls?.destroy();
    this.video.removeEventListener('timeupdate', this.handleTimeUpdate);
  }
}
```

---

## 4. @wsoptv/hands

핸드 타임라인 로직.

```typescript
// packages/hands/src/index.ts

import type { Hand } from '@wsoptv/types';
import type { HandSegment } from '@wsoptv/types';  // 통합 타입 사용 (#17)

// 시간 비교 허용 오차 (#15)
const TIME_EPSILON = 0.1;  // 100ms

/**
 * 타임라인 검증 결과 (#6)
 */
export interface TimelineValidation {
  valid: boolean;
  errors: TimelineError[];
  warnings: TimelineWarning[];
}

export interface TimelineError {
  type: 'overlap' | 'invalid_range';
  hands: [number, number];
  message: string;
}

export interface TimelineWarning {
  type: 'gap' | 'short_hand';
  position: number;
  message: string;
}

/**
 * 핸드 배열 검증 (#6)
 */
export function validateTimeline(hands: Hand[]): TimelineValidation {
  const sorted = [...hands].sort((a, b) => a.startSec - b.startSec);
  const errors: TimelineError[] = [];
  const warnings: TimelineWarning[] = [];

  for (let i = 0; i < sorted.length; i++) {
    const hand = sorted[i];

    // 유효 범위 검사
    if (hand.endSec <= hand.startSec) {
      errors.push({
        type: 'invalid_range',
        hands: [hand.id, hand.id],
        message: `핸드 #${hand.handNumber}: 종료 시간이 시작 시간보다 작거나 같음`
      });
    }

    // 너무 짧은 핸드 경고
    if (hand.endSec - hand.startSec < 10) {
      warnings.push({
        type: 'short_hand',
        position: hand.startSec,
        message: `핸드 #${hand.handNumber}: 10초 미만의 짧은 핸드`
      });
    }

    // 오버랩 검사
    if (i < sorted.length - 1) {
      const next = sorted[i + 1];
      if (hand.endSec > next.startSec + TIME_EPSILON) {
        errors.push({
          type: 'overlap',
          hands: [hand.id, next.id],
          message: `핸드 #${hand.handNumber}와 #${next.handNumber} 오버랩`
        });
      }

      // 갭 경고 (30초 이상)
      const gap = next.startSec - hand.endSec;
      if (gap > 30) {
        warnings.push({
          type: 'gap',
          position: hand.endSec,
          message: `핸드 #${hand.handNumber} 후 ${Math.round(gap)}초 갭`
        });
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * 핸드 배열로 타임라인 세그먼트 생성
 */
export function buildTimeline(hands: Hand[], duration: number): HandSegment[] {
  // 먼저 검증
  const validation = validateTimeline(hands);
  if (!validation.valid) {
    console.warn('Timeline validation errors:', validation.errors);
  }

  const sorted = [...hands].sort((a, b) => a.startSec - b.startSec);
  const segments: HandSegment[] = [];
  let lastEnd = 0;

  for (const hand of sorted) {
    // 핸드 전 비핸드 구간 (1초 이상 갭)
    if (hand.startSec > lastEnd + 1) {
      segments.push({
        type: 'shuffle',
        startSec: lastEnd,
        endSec: hand.startSec
      });
    }

    // 핸드 구간
    segments.push({
      type: 'hand',
      startSec: hand.startSec,
      endSec: hand.endSec,
      hand
    });

    lastEnd = Math.max(lastEnd, hand.endSec);  // 오버랩 대응
  }

  // 마지막 비핸드 구간
  if (duration > 0 && lastEnd < duration - 1) {
    segments.push({
      type: 'shuffle',
      startSec: lastEnd,
      endSec: duration
    });
  }

  return segments;
}

/**
 * 최적화된 타임라인 인덱스 (#21)
 * O(n) → O(1) amortized 탐색
 */
export class TimelineIndex {
  private segments: HandSegment[];
  private lastIndex: number = 0;

  constructor(segments: HandSegment[]) {
    this.segments = segments;
  }

  /**
   * 현재 시간의 세그먼트 찾기
   * Locality 활용: 이전 위치부터 순차 탐색
   */
  find(currentTime: number): HandSegment | null {
    if (this.segments.length === 0) return null;

    // 이전 위치 확인 (대부분의 경우 같은 세그먼트)
    const last = this.segments[this.lastIndex];
    if (last && this.isInRange(currentTime, last)) {
      return last;
    }

    // 다음 세그먼트 확인 (순방향 재생)
    if (this.lastIndex < this.segments.length - 1) {
      const next = this.segments[this.lastIndex + 1];
      if (this.isInRange(currentTime, next)) {
        this.lastIndex++;
        return next;
      }
    }

    // 이전 세그먼트 확인 (역방향 또는 seek)
    if (this.lastIndex > 0) {
      const prev = this.segments[this.lastIndex - 1];
      if (this.isInRange(currentTime, prev)) {
        this.lastIndex--;
        return prev;
      }
    }

    // 이진 탐색 (큰 점프의 경우)
    const index = this.binarySearch(currentTime);
    if (index >= 0) {
      this.lastIndex = index;
      return this.segments[index];
    }

    return null;
  }

  private isInRange(time: number, segment: HandSegment): boolean {
    return time >= segment.startSec - TIME_EPSILON &&
           time < segment.endSec + TIME_EPSILON;
  }

  private binarySearch(time: number): number {
    let left = 0;
    let right = this.segments.length - 1;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);
      const seg = this.segments[mid];

      if (this.isInRange(time, seg)) {
        return mid;
      } else if (time < seg.startSec) {
        right = mid - 1;
      } else {
        left = mid + 1;
      }
    }

    return -1;
  }
}

/**
 * 현재 시간의 세그먼트 찾기 (레거시 호환)
 * @deprecated TimelineIndex.find() 사용 권장
 */
export function findCurrentSegment(
  timeline: HandSegment[],
  currentTime: number
): HandSegment | null {
  return timeline.find(s =>
    currentTime >= s.startSec - TIME_EPSILON &&
    currentTime < s.endSec + TIME_EPSILON
  ) ?? null;
}

/**
 * 하이라이트 핸드 필터링
 */
export function filterHighlights(
  hands: Hand[],
  minGrade: 'S' | 'A' = 'A'
): Hand[] {
  const gradeOrder: Record<string, number> = { S: 0, A: 1, B: 2, C: 3 };
  const threshold = gradeOrder[minGrade];
  return hands.filter(h => gradeOrder[h.grade] <= threshold);
}

/**
 * 다음 핸드 찾기
 */
export function findNextHand(hands: Hand[], currentTime: number): Hand | null {
  return [...hands]
    .sort((a, b) => a.startSec - b.startSec)
    .find(h => h.startSec > currentTime + TIME_EPSILON) ?? null;
}

/**
 * 이전 핸드 찾기
 */
export function findPrevHand(hands: Hand[], currentTime: number): Hand | null {
  return [...hands]
    .sort((a, b) => b.startSec - a.startSec)
    .find(h => h.endSec < currentTime - TIME_EPSILON) ?? null;
}

/**
 * 핸드 등급별 통계
 */
export function getHandStats(hands: Hand[]): Record<string, number> {
  return hands.reduce((acc, h) => {
    acc[h.grade] = (acc[h.grade] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
}
```

---

## 5. @wsoptv/auth

인증 모듈 - httpOnly 쿠키 기반 (#1, #12, #24)

```typescript
// packages/auth/src/index.ts

import { writable, derived, type Readable } from 'svelte/store';
import type { User, UserStatus } from '@wsoptv/types';

// === Types ===

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isApproved: boolean;
  isAdmin: boolean;
  loading: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  passwordConfirm: string;
  displayName?: string;
}

export interface AuthResponse {
  user: User;
  expiresAt: string;
  // 토큰은 httpOnly 쿠키로 전달 (#1)
}

// === Store ===

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    isAuthenticated: false,
    isApproved: false,
    isAdmin: false,
    loading: true
  });

  return {
    subscribe,

    // 초기화 - httpOnly 쿠키 기반 (#1)
    async init(): Promise<void> {
      try {
        const res = await fetch('/api/v1/auth/me', {
          credentials: 'include'  // 쿠키 포함
        });

        if (res.ok) {
          const { data } = await res.json();
          set({
            user: data,
            isAuthenticated: true,
            isApproved: data.status === 'approved',
            isAdmin: data.role === 'admin',
            loading: false
          });
        } else {
          update(s => ({ ...s, loading: false }));
        }
      } catch {
        update(s => ({ ...s, loading: false }));
      }
    },

    async login(req: LoginRequest): Promise<AuthResponse> {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',  // 쿠키 수신
        body: JSON.stringify(req)
      });

      if (!res.ok) throw await res.json();

      const { data }: { data: AuthResponse } = await res.json();
      // 토큰은 Set-Cookie 헤더로 자동 설정됨 (#1)

      set({
        user: data.user,
        isAuthenticated: true,
        isApproved: data.user.status === 'approved',
        isAdmin: data.user.role === 'admin',
        loading: false
      });

      return data;
    },

    async register(req: RegisterRequest): Promise<User> {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req)
      });

      if (!res.ok) throw await res.json();

      const { data } = await res.json();
      return data.user;
    },

    // Refresh Token으로 Access Token 갱신 (#12)
    async refresh(): Promise<boolean> {
      try {
        const res = await fetch('/api/v1/auth/refresh', {
          method: 'POST',
          credentials: 'include'
        });
        return res.ok;
      } catch {
        return false;
      }
    },

    async logout(): Promise<void> {
      // 서버에서 토큰 Blacklist 처리 (#24)
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });

      set({
        user: null,
        isAuthenticated: false,
        isApproved: false,
        isAdmin: false,
        loading: false
      });
    }
  };
}

export const auth = createAuthStore();

// === Derived Stores ===

export const isAuthenticated: Readable<boolean> = derived(
  auth,
  $auth => $auth.isAuthenticated
);

export const isApproved: Readable<boolean> = derived(
  auth,
  $auth => $auth.isApproved
);

export const isAdmin: Readable<boolean> = derived(
  auth,
  $auth => $auth.isAdmin
);

export const currentUser: Readable<User | null> = derived(
  auth,
  $auth => $auth.user
);

// === RBAC 권한 체크 (#10) ===

export type Permission =
  | 'user:approve'
  | 'user:reject'
  | 'user:suspend'
  | 'content:manage'
  | 'system:config';

export const rolePermissions: Record<string, Permission[]> = {
  admin: ['user:approve', 'user:reject', 'user:suspend', 'content:manage', 'system:config'],
  user: []
};

export function hasPermission(user: User | null, permission: Permission): boolean {
  if (!user) return false;
  return rolePermissions[user.role]?.includes(permission) ?? false;
}
```

---

## 6. @wsoptv/search

검색 클라이언트.

```typescript
// packages/search/src/index.ts

import type { SearchFilters, SearchResult, Content } from '@wsoptv/types';
import { searchRequestSchema } from '@wsoptv/types';
import { defaultConfig } from '@wsoptv/config';

export interface SearchOptions {
  query: string;
  filters?: SearchFilters;
  page?: number;
  limit?: number;
  sort?: 'relevance' | 'date' | 'views';
}

export class SearchClient {
  private baseUrl: string;
  private abortController: AbortController | null = null;

  constructor(baseUrl = defaultConfig.production.api.baseUrl) {
    this.baseUrl = baseUrl;
  }

  async search(options: SearchOptions): Promise<SearchResult> {
    // 이전 요청 취소
    this.abortController?.abort();
    this.abortController = new AbortController();

    // Input validation (#3)
    const validated = searchRequestSchema.parse({
      q: options.query,
      catalogId: options.filters?.catalogId,
      playerId: options.filters?.playerId,
      handGrade: options.filters?.handGrade,
      year: options.filters?.year,
      page: options.page,
      limit: options.limit,
      sort: options.sort
    });

    const params = new URLSearchParams();
    params.set('q', validated.q);

    // 필터 우선순위대로 적용 (#25)
    if (validated.catalogId) params.set('catalogId', validated.catalogId);
    if (validated.playerId) params.set('playerId', String(validated.playerId));
    if (validated.handGrade) params.set('handGrade', validated.handGrade);
    if (validated.year) params.set('year', String(validated.year));

    params.set('page', String(validated.page));
    params.set('limit', String(validated.limit));
    params.set('sort', validated.sort);

    const res = await fetch(`${this.baseUrl}/search?${params}`, {
      signal: this.abortController.signal,
      credentials: 'include'
    });

    if (!res.ok) throw await res.json();

    const { data } = await res.json();
    return data;
  }

  async suggest(query: string, limit = 5): Promise<string[]> {
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    const res = await fetch(`${this.baseUrl}/search/suggest?${params}`, {
      credentials: 'include'
    });

    if (!res.ok) return [];

    const { data } = await res.json();
    return data.suggestions;
  }

  cancel(): void {
    this.abortController?.abort();
    this.abortController = null;
  }
}

export const searchClient = new SearchClient();
```

---

## 7. @wsoptv/streaming (Backend)

HLS 스트리밍 서비스 - 중복 실행 방지 (#8), 캐시 (#29)

```python
# packages/streaming/src/service.py

from pathlib import Path
from enum import Enum
from typing import Optional
import asyncio
import aioredis
import aiofiles

class Quality(Enum):
    P360 = ("360p", 640, 360, "500k", "64k")
    P480 = ("480p", 854, 480, "1M", "96k")
    P720 = ("720p", 1280, 720, "2.5M", "128k")
    P1080 = ("1080p", 1920, 1080, "5M", "128k")

    @property
    def name(self) -> str: return self.value[0]
    @property
    def width(self) -> int: return self.value[1]
    @property
    def height(self) -> int: return self.value[2]
    @property
    def video_bitrate(self) -> str: return self.value[3]
    @property
    def audio_bitrate(self) -> str: return self.value[4]  # (#32)


class TranscodeStatus(Enum):
    """트랜스코딩 상태 (#16)"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HLSService:
    def __init__(
        self,
        nas_path: str,
        hls_path: str,
        redis: aioredis.Redis,
        config: dict
    ):
        self.nas_path = Path(nas_path)
        self.hls_path = Path(hls_path)
        self.redis = redis
        self.config = config

    async def get_stream_url(self, file_id: str, nas_file: str, user_id: int) -> str:
        """HLS 스트림 URL 반환 (권한 검증 포함 #4)"""

        # 권한 검증 (#4)
        if not await self._check_access(user_id, file_id):
            raise StreamAccessDeniedError(file_id)

        manifest = self.hls_path / file_id / "master.m3u8"

        if manifest.exists():
            return f"/hls/{file_id}/master.m3u8"

        # 이미 트랜스코딩 중인지 확인 (#8)
        status = await self.get_transcode_status(file_id)
        if status == TranscodeStatus.PROCESSING:
            raise StreamNotReadyError(file_id)

        # 분산 락으로 중복 실행 방지 (#8)
        lock_key = f"transcode:lock:{file_id}"
        if await self.redis.setnx(lock_key, "processing"):
            await self.redis.expire(lock_key, 3600)
            asyncio.create_task(self._transcode_with_status(file_id, nas_file))

        raise StreamNotReadyError(file_id)

    async def get_transcode_status(self, file_id: str) -> TranscodeStatus:
        """트랜스코딩 상태 조회 (#16)"""
        status = await self.redis.get(f"transcode:status:{file_id}")
        if status:
            return TranscodeStatus(status.decode())

        manifest = self.hls_path / file_id / "master.m3u8"
        if manifest.exists():
            return TranscodeStatus.COMPLETED

        return TranscodeStatus.PENDING

    async def _check_access(self, user_id: int, file_id: str) -> bool:
        """콘텐츠 접근 권한 확인 (#4)"""
        # TODO: 실제 구현에서는 DB 조회로 권한 확인
        # - 사용자 승인 상태
        # - 콘텐츠 공개 여부
        return True

    async def _transcode_with_status(self, file_id: str, source: str) -> None:
        """상태 추적 포함 트랜스코딩 (#16)"""
        status_key = f"transcode:status:{file_id}"
        lock_key = f"transcode:lock:{file_id}"

        try:
            await self.redis.set(status_key, TranscodeStatus.PROCESSING.value)
            await self._transcode(file_id, source)
            await self.redis.set(status_key, TranscodeStatus.COMPLETED.value)

            # manifest 캐시 TTL 설정 (#29)
            await self.redis.expire(
                status_key,
                self.config.get('cache', {}).get('manifest_ttl', 3600)
            )
        except Exception as e:
            await self.redis.set(status_key, TranscodeStatus.FAILED.value)
            # 에러 정보 저장
            await self.redis.set(f"transcode:error:{file_id}", str(e), ex=3600)
            raise
        finally:
            await self.redis.delete(lock_key)

    async def _transcode(self, file_id: str, source: str) -> None:
        """FFmpeg HLS 멀티비트레이트 트랜스코딩"""
        output_dir = self.hls_path / file_id
        output_dir.mkdir(parents=True, exist_ok=True)

        input_path = self.nas_path / source

        # 하드웨어 가속 설정 (#20)
        hw_accel = self.config.get('ffmpeg', {}).get('hw_accel', 'none')
        preset = self.config.get('ffmpeg', {}).get('preset', 'medium')

        hw_args = self._get_hw_accel_args(hw_accel)

        filter_complex = self._build_filter_complex()
        maps_and_codecs = self._build_maps_and_codecs(hw_accel)

        cmd = [
            "ffmpeg", "-y",
            *hw_args,
            "-i", str(input_path),
            "-filter_complex", filter_complex,
            *maps_and_codecs,
            "-preset", preset,
            "-f", "hls",
            "-hls_time", "6",
            "-hls_list_size", "0",
            "-hls_segment_filename", str(output_dir / "stream_%v_%03d.ts"),
            "-master_pl_name", "master.m3u8",
            "-var_stream_map", "v:0,a:0 v:1,a:1 v:2,a:2",
            str(output_dir / "stream_%v.m3u8")
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise TranscodeError(f"FFmpeg failed: {stderr.decode()}")

    def _get_hw_accel_args(self, hw_accel: str) -> list[str]:
        """하드웨어 가속 인자 (#20)"""
        if hw_accel == "cuda":
            return ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        elif hw_accel == "vaapi":
            return ["-hwaccel", "vaapi", "-hwaccel_output_format", "vaapi"]
        elif hw_accel == "qsv":
            return ["-hwaccel", "qsv", "-hwaccel_output_format", "qsv"]
        return []

    def _build_filter_complex(self) -> str:
        return (
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=1280:720[v720];"
            "[v2]scale=854:480[v480];"
            "[v3]scale=640:360[v360]"
        )

    def _build_maps_and_codecs(self, hw_accel: str) -> list[str]:
        """오디오 비트레이트 포함 (#32)"""
        encoder = "h264_nvenc" if hw_accel == "cuda" else "libx264"

        return [
            "-map", "[v720]", "-c:v:0", encoder, "-b:v:0", "2.5M",
            "-map", "[v480]", "-c:v:1", encoder, "-b:v:1", "1M",
            "-map", "[v360]", "-c:v:2", encoder, "-b:v:2", "500K",
            "-map", "0:a", "-c:a:0", "aac", "-b:a:0", "128k",
            "-map", "0:a", "-c:a:1", "aac", "-b:a:1", "96k",
            "-map", "0:a", "-c:a:2", "aac", "-b:a:2", "64k"
        ]


class StreamNotReadyError(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Stream not ready: {file_id}")


class StreamAccessDeniedError(Exception):
    """접근 권한 없음 (#4)"""
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Access denied: {file_id}")


class TranscodeError(Exception):
    pass
```

---

## 8. @wsoptv/db (Backend)

데이터베이스 레이어 - N+1 해결 (#9), Race Condition 방지 (#7)

```python
# packages/db/src/models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, ARRAY, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True)
    series_id = Column(Integer, ForeignKey("series.id"))
    file_id = Column(String(200), ForeignKey("files.id"))
    episode_num = Column(Integer)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    duration_sec = Column(Float)
    thumbnail_url = Column(Text)
    view_count = Column(Integer, default=0)

    series = relationship("Series", back_populates="contents")
    hands = relationship("Hand", back_populates="content", lazy="selectin")  # Eager loading (#9)
    players = relationship("Player", secondary="content_players", lazy="selectin")


class Hand(Base):
    __tablename__ = "hands"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    file_id = Column(String(200))
    hand_number = Column(Integer)
    start_sec = Column(Float, nullable=False)
    end_sec = Column(Float, nullable=False)
    players = Column(ARRAY(Text))
    winner = Column(String(100))
    pot_size_bb = Column(Float)
    hand_grade = Column(String(1))
    is_all_in = Column(Boolean, default=False)
    is_showdown = Column(Boolean, default=False)
    tags = Column(ARRAY(Text))
    highlight_score = Column(Float, default=0.0)

    content = relationship("Content", back_populates="hands")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    role = Column(String(20), default="user")
    status = Column(String(20), default="pending")


class WatchProgress(Base):
    """시청 진행률 - Optimistic Locking (#7)"""
    __tablename__ = "watch_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    progress_sec = Column(Float, nullable=False)
    duration_sec = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)
    version = Column(Integer, default=1)  # Optimistic Locking 버전
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

```python
# packages/db/src/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from typing import Optional, List

class ContentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Content]:
        """Eager Loading으로 N+1 방지 (#9)"""
        stmt = (
            select(Content)
            .options(
                selectinload(Content.hands),
                selectinload(Content.players),
                joinedload(Content.series)
            )
            .where(Content.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_series(
        self,
        series_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Content]:
        stmt = (
            select(Content)
            .options(selectinload(Content.hands))
            .where(Content.series_id == series_id)
            .order_by(Content.episode_num)
            .limit(limit).offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_view(self, id: int) -> None:
        content = await self.get_by_id(id)
        if content:
            content.view_count += 1
            await self.session.commit()


class WatchProgressRepository:
    """진행률 저장소 - Optimistic Locking (#7)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        user_id: int,
        content_id: int,
        progress_sec: float,
        duration_sec: float,
        expected_version: Optional[int] = None
    ) -> WatchProgress:
        """
        진행률 저장 (Race Condition 방지)
        expected_version이 일치할 때만 업데이트
        """
        existing = await self.session.execute(
            select(WatchProgress).where(
                WatchProgress.user_id == user_id,
                WatchProgress.content_id == content_id
            )
        )
        progress = existing.scalar_one_or_none()

        if progress:
            # Optimistic Locking 검증
            if expected_version is not None and progress.version != expected_version:
                raise OptimisticLockError(
                    f"Version mismatch: expected {expected_version}, got {progress.version}"
                )

            progress.progress_sec = progress_sec
            progress.duration_sec = duration_sec
            progress.completed = (progress_sec / duration_sec) >= 0.9
            progress.version += 1
        else:
            progress = WatchProgress(
                user_id=user_id,
                content_id=content_id,
                progress_sec=progress_sec,
                duration_sec=duration_sec,
                completed=(progress_sec / duration_sec) >= 0.9,
                version=1
            )
            self.session.add(progress)

        await self.session.commit()
        return progress


class HandRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_content(self, content_id: int) -> List[Hand]:
        stmt = (
            select(Hand)
            .where(Hand.content_id == content_id)
            .order_by(Hand.start_sec)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_highlights(
        self,
        content_id: int,
        min_grade: str = 'A'
    ) -> List[Hand]:
        grades = {'S': 1, 'A': 2, 'B': 3, 'C': 4}
        threshold = grades.get(min_grade, 2)
        valid_grades = [g for g, v in grades.items() if v <= threshold]

        stmt = (
            select(Hand)
            .where(Hand.content_id == content_id)
            .where(Hand.hand_grade.in_(valid_grades))
            .order_by(Hand.start_sec)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class OptimisticLockError(Exception):
    """버전 불일치 에러 (#7)"""
    pass
```

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 모듈 설계 |
| 2.0.0 | 2025-12-09 | 보안/성능/로직 이슈 32건 수정 (#1-#32) |
