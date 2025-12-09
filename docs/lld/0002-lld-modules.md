# LLD: Modules (패키지 상세 설계)

**Version**: 1.0.0 | **Master**: [0001-lld-wsoptv-platform.md](./0001-lld-wsoptv-platform.md)

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
}
```

### 1.3 API Types

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

export interface SearchFilters {
  catalogId?: string;
  seriesId?: number;
  playerId?: number;
  handGrade?: HandGrade;
  year?: number;
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
  skipButtonDelay: number;  // ms
  skipButtonDuration: number;  // ms
}

export type VideoQuality = '360p' | '480p' | '720p' | '1080p' | 'auto';

export interface SearchConfig {
  debounceMs: number;
  minQueryLength: number;
  defaultLimit: number;
  maxLimit: number;
}

export interface AuthConfig {
  tokenKey: string;
  tokenExpiry: number;  // days
  refreshThreshold: number;  // hours
}

// 기본값
export const defaultConfig: AppConfig = {
  api: {
    baseUrl: '/api/v1',
    timeout: 30000,
    retryCount: 3
  },
  player: {
    autoplay: true,
    defaultQuality: 'auto',
    defaultPlaybackRate: 1,
    skipButtonDelay: 500,
    skipButtonDuration: 5000
  },
  search: {
    debounceMs: 300,
    minQueryLength: 2,
    defaultLimit: 20,
    maxLimit: 100
  },
  auth: {
    tokenKey: 'wsoptv_token',
    tokenExpiry: 7,
    refreshThreshold: 24
  }
};
```

---

## 3. @wsoptv/player

비디오 플레이어 핵심 로직.

### 3.1 Types

```typescript
// packages/player/src/types.ts

import type { Hand, HandGrade } from '@wsoptv/types';

export interface PlayerConfig {
  autoplay: boolean;
  quality: VideoQuality;
  playbackRate: number;
  volume: number;
  muted: boolean;
  skipConfig: SkipConfig;
}

export interface SkipConfig {
  enabled: boolean;
  skipShuffle: boolean;      // 셔플 구간 자동 스킵
  minHandGrade: HandGrade | null;  // null = 전체
  autoNextHand: boolean;     // 핸드 종료 시 다음 핸드로
  showSkipButtons: boolean;  // Netflix 스타일 버튼
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
  onError?: (error: PlayerError) => void;
}

export interface HandSegment {
  type: 'hand' | 'shuffle' | 'break';
  startSec: number;
  endSec: number;
  hand?: Hand;
}
```

### 3.2 Player Controller

```typescript
// packages/player/src/controller.ts

import Hls from 'hls.js';
import type { Hand } from '@wsoptv/types';
import type { PlayerConfig, PlayerState, PlayerCallbacks, HandSegment } from './types';
import { buildTimeline, findCurrentSegment } from '@wsoptv/hands';

export class PlayerController {
  private video: HTMLVideoElement;
  private hls: Hls | null = null;
  private config: PlayerConfig;
  private callbacks: PlayerCallbacks;
  private hands: Hand[] = [];
  private timeline: HandSegment[] = [];
  private currentSegment: HandSegment | null = null;

  constructor(
    video: HTMLVideoElement,
    config: Partial<PlayerConfig>,
    callbacks: PlayerCallbacks
  ) {
    this.video = video;
    this.config = { ...defaultPlayerConfig, ...config };
    this.callbacks = callbacks;
    this.setupEventListeners();
  }

  async loadSource(src: string, hands: Hand[] = []): Promise<void> {
    this.hands = hands;
    this.timeline = buildTimeline(hands, 0);  // duration 은 로드 후 업데이트

    if (Hls.isSupported()) {
      this.hls = new Hls({
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        startLevel: -1  // Auto
      });
      this.hls.loadSource(src);
      this.hls.attachMedia(this.video);

      return new Promise((resolve, reject) => {
        this.hls!.on(Hls.Events.MANIFEST_PARSED, () => {
          this.timeline = buildTimeline(hands, this.video.duration);
          resolve();
        });
        this.hls!.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal) reject(new Error(data.details));
        });
      });
    } else if (this.video.canPlayType('application/vnd.apple.mpegurl')) {
      // Safari native HLS
      this.video.src = src;
      return new Promise(resolve => {
        this.video.addEventListener('loadedmetadata', () => {
          this.timeline = buildTimeline(hands, this.video.duration);
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

    const segment = findCurrentSegment(this.timeline, time);

    if (segment !== this.currentSegment) {
      // 이전 세그먼트 종료
      if (this.currentSegment?.type === 'hand' && this.currentSegment.hand) {
        this.callbacks.onHandExit?.(this.currentSegment.hand);
      }

      // 새 세그먼트 진입
      this.currentSegment = segment;

      if (segment?.type === 'hand' && segment.hand) {
        this.callbacks.onHandEnter?.(segment.hand);
      } else if (segment?.type === 'shuffle' || segment?.type === 'break') {
        this.callbacks.onNonHandSegment?.(segment);
      }
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
      playbackRate: this.video.playbackRate
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

export interface HandSegment {
  type: 'hand' | 'shuffle' | 'break';
  startSec: number;
  endSec: number;
  hand?: Hand;
}

/**
 * 핸드 배열로 타임라인 세그먼트 생성
 */
export function buildTimeline(hands: Hand[], duration: number): HandSegment[] {
  const sorted = [...hands].sort((a, b) => a.startSec - b.startSec);
  const segments: HandSegment[] = [];
  let lastEnd = 0;

  for (const hand of sorted) {
    // 핸드 전 비핸드 구간
    if (hand.startSec > lastEnd + 1) {  // 1초 이상 갭
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

    lastEnd = hand.endSec;
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
 * 현재 시간의 세그먼트 찾기
 */
export function findCurrentSegment(
  timeline: HandSegment[],
  currentTime: number
): HandSegment | null {
  return timeline.find(s =>
    currentTime >= s.startSec && currentTime < s.endSec
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
    .find(h => h.startSec > currentTime) ?? null;
}

/**
 * 이전 핸드 찾기
 */
export function findPrevHand(hands: Hand[], currentTime: number): Hand | null {
  return [...hands]
    .sort((a, b) => b.startSec - a.startSec)
    .find(h => h.endSec < currentTime) ?? null;
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

인증 모듈.

```typescript
// packages/auth/src/index.ts

import { writable, derived, type Readable } from 'svelte/store';
import type { User, UserStatus } from '@wsoptv/types';
import { defaultConfig } from '@wsoptv/config';

// === Types ===

export interface AuthState {
  user: User | null;
  token: string | null;
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
  token: string;
  expiresAt: string;
}

// === Store ===

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isApproved: false,
    isAdmin: false,
    loading: true
  });

  const { tokenKey } = defaultConfig.auth;

  return {
    subscribe,

    async init(): Promise<void> {
      const token = localStorage.getItem(tokenKey);
      if (!token) {
        update(s => ({ ...s, loading: false }));
        return;
      }

      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.ok) {
          const { data } = await res.json();
          set({
            user: data,
            token,
            isAuthenticated: true,
            isApproved: data.status === 'approved',
            isAdmin: data.role === 'admin',
            loading: false
          });
        } else {
          localStorage.removeItem(tokenKey);
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
        body: JSON.stringify(req)
      });

      if (!res.ok) throw await res.json();

      const { data }: { data: AuthResponse } = await res.json();
      localStorage.setItem(tokenKey, data.token);

      set({
        user: data.user,
        token: data.token,
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

    logout(): void {
      localStorage.removeItem(tokenKey);
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isApproved: false,
        isAdmin: false,
        loading: false
      });
    },

    getToken(): string | null {
      let token: string | null = null;
      subscribe(s => { token = s.token; })();
      return token;
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
```

---

## 6. @wsoptv/search

검색 클라이언트.

```typescript
// packages/search/src/index.ts

import type { SearchFilters, SearchResult, Content } from '@wsoptv/types';
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

  constructor(baseUrl = defaultConfig.api.baseUrl) {
    this.baseUrl = baseUrl;
  }

  async search(options: SearchOptions): Promise<SearchResult> {
    // 이전 요청 취소
    this.abortController?.abort();
    this.abortController = new AbortController();

    const params = new URLSearchParams();
    params.set('q', options.query);
    if (options.filters?.catalogId) params.set('catalogId', options.filters.catalogId);
    if (options.filters?.playerId) params.set('playerId', String(options.filters.playerId));
    if (options.filters?.handGrade) params.set('handGrade', options.filters.handGrade);
    if (options.filters?.year) params.set('year', String(options.filters.year));
    params.set('page', String(options.page ?? 1));
    params.set('limit', String(options.limit ?? defaultConfig.search.defaultLimit));
    if (options.sort) params.set('sort', options.sort);

    const res = await fetch(`${this.baseUrl}/search?${params}`, {
      signal: this.abortController.signal
    });

    if (!res.ok) throw await res.json();

    const { data } = await res.json();
    return data;
  }

  async suggest(query: string, limit = 5): Promise<string[]> {
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    const res = await fetch(`${this.baseUrl}/search/suggest?${params}`);

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

HLS 스트리밍 서비스.

```python
# packages/streaming/src/service.py

from pathlib import Path
from enum import Enum
from typing import Optional
import asyncio
import hashlib
import aiofiles

class Quality(Enum):
    P360 = ("360p", 640, 360, "500k")
    P480 = ("480p", 854, 480, "1M")
    P720 = ("720p", 1280, 720, "2.5M")
    P1080 = ("1080p", 1920, 1080, "5M")

    @property
    def name(self) -> str: return self.value[0]
    @property
    def width(self) -> int: return self.value[1]
    @property
    def height(self) -> int: return self.value[2]
    @property
    def bitrate(self) -> str: return self.value[3]


class HLSService:
    def __init__(self, nas_path: str, hls_path: str, cache_ttl: int = 3600):
        self.nas_path = Path(nas_path)
        self.hls_path = Path(hls_path)
        self.cache_ttl = cache_ttl

    async def get_stream_url(self, file_id: str, nas_file: str) -> str:
        """HLS 스트림 URL 반환 (없으면 생성 트리거)"""
        manifest = self.hls_path / file_id / "master.m3u8"

        if manifest.exists():
            return f"/hls/{file_id}/master.m3u8"

        # 트랜스코딩 시작 (비동기)
        asyncio.create_task(self._transcode(file_id, nas_file))

        raise StreamNotReadyError(file_id)

    async def is_ready(self, file_id: str) -> bool:
        """스트림 준비 여부"""
        manifest = self.hls_path / file_id / "master.m3u8"
        return manifest.exists()

    async def _transcode(self, file_id: str, source: str) -> None:
        """FFmpeg HLS 멀티비트레이트 트랜스코딩"""
        output_dir = self.hls_path / file_id
        output_dir.mkdir(parents=True, exist_ok=True)

        input_path = self.nas_path / source

        # FFmpeg 명령 구성
        filter_complex = self._build_filter_complex()
        maps_and_codecs = self._build_maps_and_codecs()

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-filter_complex", filter_complex,
            *maps_and_codecs,
            "-f", "hls",
            "-hls_time", "6",
            "-hls_list_size", "0",
            "-hls_segment_filename", str(output_dir / "stream_%v_%03d.ts"),
            "-master_pl_name", "master.m3u8",
            "-var_stream_map", "v:0,a:0 v:1,a:0 v:2,a:0",
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

    def _build_filter_complex(self) -> str:
        return (
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=1280:720[v720];"
            "[v2]scale=854:480[v480];"
            "[v3]scale=640:360[v360]"
        )

    def _build_maps_and_codecs(self) -> list[str]:
        return [
            "-map", "[v720]", "-c:v:0", "libx264", "-b:v:0", "2.5M",
            "-map", "[v480]", "-c:v:1", "libx264", "-b:v:1", "1M",
            "-map", "[v360]", "-c:v:2", "libx264", "-b:v:2", "500K",
            "-map", "0:a", "-c:a", "aac", "-b:a", "128k"
        ]


class StreamNotReadyError(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Stream not ready: {file_id}")


class TranscodeError(Exception):
    pass
```

---

## 8. @wsoptv/db (Backend)

데이터베이스 레이어.

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
    hands = relationship("Hand", back_populates="content")


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
```

```python
# packages/db/src/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

class ContentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Content]:
        return await self.session.get(Content, id)

    async def list_by_series(
        self,
        series_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Content]:
        stmt = (
            select(Content)
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
```

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 모듈 설계 |
