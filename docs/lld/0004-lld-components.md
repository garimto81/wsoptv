# LLD: Components (Svelte 컴포넌트 상세)

**Version**: 2.0.0 | **Master**: [0001-lld-wsoptv-platform.md](./0001-lld-wsoptv-platform.md)

---

## 1. VideoPlayer

HLS 비디오 재생 + 핸드 감지.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| src | string | (필수) | HLS URL |
| hands | Hand[] | [] | 핸드 목록 |
| autoplay | boolean | true | 자동 재생 |
| startTime | number | 0 | 시작 시간 (초) |
| config | PlayerConfig | {} | 플레이어 설정 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| timeupdate | number | 재생 시간 변경 |
| handenter | Hand | 핸드 구간 진입 |
| handexit | Hand | 핸드 구간 이탈 |
| nonhandsegment | HandSegment | 비핸드 구간 진입 |
| statechange | PlayerState | 플레이어 상태 변경 |
| error | PlayerError | 에러 발생 |

### Methods

| Method | Params | Return | 설명 |
|--------|--------|--------|------|
| play | - | void | 재생 |
| pause | - | void | 일시정지 |
| seek | time: number | void | 특정 시간으로 이동 |
| seekToHand | handId: number | void | 특정 핸드로 이동 |
| skipToNextHand | - | void | 다음 핸드로 이동 |
| skipToPrevHand | - | void | 이전 핸드로 이동 |
| setQuality | quality: string | void | 화질 변경 |
| getState | - | PlayerState | 현재 상태 반환 |

### 구현

```svelte
<!-- packages/player/src/VideoPlayer.svelte -->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { PlayerController } from './controller';
  import type { Hand, PlayerConfig, PlayerState, HandSegment, PlayerError } from './types';

  export let src: string;
  export let hands: Hand[] = [];
  export let autoplay = true;
  export let startTime = 0;
  export let config: Partial<PlayerConfig> = {};

  const dispatch = createEventDispatcher<{
    timeupdate: number;
    handenter: Hand;
    handexit: Hand;
    nonhandsegment: HandSegment;
    statechange: PlayerState;
    error: PlayerError;
  }>();

  let videoEl: HTMLVideoElement;
  let controller: PlayerController;
  let state: PlayerState;

  onMount(async () => {
    controller = new PlayerController(videoEl, config, {
      onTimeUpdate: (time) => dispatch('timeupdate', time),
      onHandEnter: (hand) => dispatch('handenter', hand),
      onHandExit: (hand) => dispatch('handexit', hand),
      onNonHandSegment: (seg) => dispatch('nonhandsegment', seg),
      onStateChange: (s) => {
        state = s;
        dispatch('statechange', s);
      },
      onError: (e) => dispatch('error', e)
    });

    await controller.loadSource(src, hands);

    if (startTime > 0) controller.seek(startTime);
    if (autoplay) controller.play();
  });

  onDestroy(() => controller?.destroy());

  // Public methods
  export const play = () => controller?.play();
  export const pause = () => controller?.pause();
  export const seek = (time: number) => controller?.seek(time);
  export const seekToHand = (id: number) => controller?.seekToHand(id);
  export const skipToNextHand = () => controller?.skipToNextHand();
  export const skipToPrevHand = () => controller?.skipToPrevHand();
  export const setQuality = (q: string) => controller?.setQuality(q);
  export const getState = () => controller?.getState();
</script>

<div class="video-player" class:playing={state?.status === 'playing'}>
  <video
    bind:this={videoEl}
    playsinline
    crossorigin="anonymous"
  >
    <track kind="metadata" />
  </video>

  <slot name="overlay" {state} />
  <slot name="controls" {state} />
</div>

<style>
  .video-player {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    background: var(--wsop-black);
  }

  video {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
</style>
```

---

## 2. SkipButtons

Netflix 스타일 스킵 버튼 오버레이.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| visible | boolean | false | 표시 여부 |
| autoHideMs | number | 5000 | 자동 숨김 시간 |
| hasHighlights | boolean | true | 하이라이트 버튼 표시 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| skiptohand | - | "핸드 모아보기" 클릭 |
| highlightsonly | - | "하이라이트만 보기" 클릭 |
| dismiss | - | 버튼 숨김 |

### 구현

```svelte
<!-- packages/player/src/SkipButtons.svelte -->
<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  export let visible = false;
  export let autoHideMs = 5000;
  export let hasHighlights = true;

  const dispatch = createEventDispatcher<{
    skiptohand: void;
    highlightsonly: void;
    dismiss: void;
  }>();

  let hideTimer: ReturnType<typeof setTimeout>;

  $: if (visible) {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      visible = false;
      dispatch('dismiss');
    }, autoHideMs);
  }

  function handleSkipToHand() {
    dispatch('skiptohand');
    visible = false;
  }

  function handleHighlightsOnly() {
    dispatch('highlightsonly');
    visible = false;
  }

  onMount(() => () => clearTimeout(hideTimer));
</script>

{#if visible}
  <div
    class="skip-buttons"
    transition:fly={{ y: 20, duration: 300 }}
  >
    <button
      class="skip-btn primary"
      on:click={handleSkipToHand}
    >
      <span class="icon">⏭</span>
      <span class="label">핸드 모아보기</span>
      <span class="sublabel">(셔플 스킵)</span>
    </button>

    {#if hasHighlights}
      <button
        class="skip-btn highlight"
        on:click={handleHighlightsOnly}
      >
        <span class="icon">⭐</span>
        <span class="label">하이라이트 핸드만 보기</span>
        <span class="sublabel">(S, A 등급만)</span>
      </button>
    {/if}
  </div>
{/if}

<style>
  .skip-buttons {
    position: absolute;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 12px;
    z-index: 10;
  }

  .skip-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 28px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
  }

  .skip-btn.primary {
    background: rgba(255, 255, 255, 0.95);
    color: var(--wsop-black);
  }

  .skip-btn.highlight {
    background: var(--wsop-gold);
    color: var(--wsop-black);
  }

  .skip-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }

  .icon {
    font-size: 24px;
    margin-bottom: 4px;
  }

  .label {
    font-weight: 600;
    font-size: 14px;
  }

  .sublabel {
    font-size: 11px;
    opacity: 0.7;
    margin-top: 2px;
  }
</style>
```

---

## 3. HandTimeline

프로그레스 바 위 핸드 마커 표시.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| hands | Hand[] | [] | 핸드 목록 |
| duration | number | 0 | 전체 재생시간 |
| currentTime | number | 0 | 현재 재생시간 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| markerclick | Hand | 마커 클릭 |
| markerhover | Hand | null | 마커 호버 |

### 구현

```svelte
<!-- packages/player/src/HandTimeline.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Hand } from '@wsoptv/types';

  export let hands: Hand[] = [];
  export let duration = 0;
  export let currentTime = 0;

  const dispatch = createEventDispatcher<{
    markerclick: Hand;
    markerhover: Hand | null;
  }>();

  const gradeColors: Record<string, string> = {
    S: 'var(--wsop-gold)',
    A: 'var(--wsop-red)',
    B: 'var(--wsop-bronze)',
    C: 'var(--wsop-black-light)'
  };

  function getPosition(time: number): string {
    return `${(time / duration) * 100}%`;
  }

  function getWidth(hand: Hand): string {
    return `${((hand.endSec - hand.startSec) / duration) * 100}%`;
  }

  function isActive(hand: Hand): boolean {
    return currentTime >= hand.startSec && currentTime < hand.endSec;
  }
</script>

<div class="timeline">
  {#each hands as hand (hand.id)}
    <button
      class="marker"
      class:active={isActive(hand)}
      style="
        left: {getPosition(hand.startSec)};
        width: {getWidth(hand)};
        background: {gradeColors[hand.grade]};
      "
      on:click={() => dispatch('markerclick', hand)}
      on:mouseenter={() => dispatch('markerhover', hand)}
      on:mouseleave={() => dispatch('markerhover', null)}
      title="Hand #{hand.handNumber} ({hand.grade})"
    />
  {/each}

  <div
    class="progress"
    style="width: {getPosition(currentTime)}"
  />
</div>

<style>
  .timeline {
    position: relative;
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    overflow: hidden;
  }

  .marker {
    position: absolute;
    top: 0;
    height: 100%;
    min-width: 4px;
    opacity: 0.8;
    border: none;
    padding: 0;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .marker:hover,
  .marker.active {
    opacity: 1;
    z-index: 1;
  }

  .progress {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background: var(--wsop-gold);
    pointer-events: none;
    z-index: 2;
  }
</style>
```

---

## 4. HandList

사이드바 핸드 목록.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| hands | Hand[] | [] | 핸드 목록 |
| currentHandId | number | null | 현재 핸드 ID |
| filterGrade | string | null | 등급 필터 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| select | Hand | 핸드 선택 |

### 구현

```svelte
<!-- packages/player/src/HandList.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Hand } from '@wsoptv/types';

  export let hands: Hand[] = [];
  export let currentHandId: number | null = null;
  export let filterGrade: string | null = null;

  const dispatch = createEventDispatcher<{ select: Hand }>();

  $: filteredHands = filterGrade
    ? hands.filter(h => h.grade === filterGrade)
    : hands;

  function formatTime(sec: number): string {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }
</script>

<div class="hand-list">
  <div class="header">
    <span>핸드 목록 ({filteredHands.length})</span>
    <select bind:value={filterGrade}>
      <option value={null}>전체</option>
      <option value="S">S등급</option>
      <option value="A">A등급</option>
      <option value="B">B등급</option>
      <option value="C">C등급</option>
    </select>
  </div>

  <ul class="list">
    {#each filteredHands as hand (hand.id)}
      <li
        class="item"
        class:active={hand.id === currentHandId}
        on:click={() => dispatch('select', hand)}
      >
        <span class="badge grade-{hand.grade.toLowerCase()}">{hand.grade}</span>
        <div class="info">
          <span class="time">{formatTime(hand.startSec)}</span>
          <span class="players">{hand.players.slice(0, 2).join(' vs ')}</span>
        </div>
        <div class="tags">
          {#if hand.isAllIn}<span class="tag">All-in</span>{/if}
          {#if hand.isShowdown}<span class="tag">Showdown</span>{/if}
        </div>
      </li>
    {/each}
  </ul>
</div>

<style>
  .hand-list {
    background: var(--wsop-black-light);
    border-radius: 8px;
    overflow: hidden;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    color: var(--wsop-cream);
  }

  .list {
    list-style: none;
    margin: 0;
    padding: 0;
    max-height: 400px;
    overflow-y: auto;
  }

  .item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.2s;
    color: var(--wsop-cream);
  }

  .item:hover,
  .item.active {
    background: rgba(212, 175, 55, 0.1);
  }

  .item.active {
    border-left: 3px solid var(--wsop-gold);
  }

  .badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 12px;
  }

  .badge.grade-s { background: var(--wsop-gold); color: var(--wsop-black); }
  .badge.grade-a { background: var(--wsop-red); color: white; }
  .badge.grade-b { background: var(--wsop-bronze); color: white; }
  .badge.grade-c { background: var(--wsop-black); color: var(--wsop-cream); }

  .time {
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    opacity: 0.7;
  }

  .players {
    font-size: 14px;
  }

  .tag {
    font-size: 10px;
    padding: 2px 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
  }
</style>
```

---

## 5. SearchBar

자동완성 검색.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| placeholder | string | "검색..." | 플레이스홀더 |
| debounceMs | number | 300 | 디바운스 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| search | string | 검색 실행 |
| suggest | string[] | 제안 목록 |

### 구현

```svelte
<!-- packages/search/src/SearchBar.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { searchClient } from './index';

  export let placeholder = '검색...';
  export let debounceMs = 300;

  const dispatch = createEventDispatcher<{
    search: string;
    suggest: string[];
  }>();

  let query = '';
  let suggestions: string[] = [];
  let showSuggestions = false;
  let debounceTimer: ReturnType<typeof setTimeout>;

  async function handleInput() {
    clearTimeout(debounceTimer);

    if (query.length < 2) {
      suggestions = [];
      return;
    }

    debounceTimer = setTimeout(async () => {
      suggestions = await searchClient.suggest(query);
      showSuggestions = suggestions.length > 0;
      dispatch('suggest', suggestions);
    }, debounceMs);
  }

  function handleSubmit() {
    if (query.trim()) {
      dispatch('search', query.trim());
      showSuggestions = false;
    }
  }

  function selectSuggestion(s: string) {
    query = s;
    showSuggestions = false;
    dispatch('search', s);
  }
</script>

<div class="search-bar">
  <form on:submit|preventDefault={handleSubmit}>
    <input
      type="text"
      bind:value={query}
      on:input={handleInput}
      on:focus={() => showSuggestions = suggestions.length > 0}
      on:blur={() => setTimeout(() => showSuggestions = false, 200)}
      {placeholder}
    />
    <button type="submit">
      <span class="icon">🔍</span>
    </button>
  </form>

  {#if showSuggestions}
    <ul class="suggestions">
      {#each suggestions as s}
        <li on:click={() => selectSuggestion(s)}>{s}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .search-bar {
    position: relative;
  }

  form {
    display: flex;
    gap: 8px;
  }

  input {
    flex: 1;
    padding: 12px 16px;
    background: var(--wsop-black-light);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 8px;
    color: var(--wsop-cream);
    font-size: 16px;
  }

  input:focus {
    outline: none;
    border-color: var(--wsop-gold);
  }

  button {
    padding: 12px 16px;
    background: var(--wsop-gold);
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--wsop-black-light);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 0 0 8px 8px;
    list-style: none;
    margin: 0;
    padding: 0;
    z-index: 100;
  }

  .suggestions li {
    padding: 12px 16px;
    cursor: pointer;
    color: var(--wsop-cream);
  }

  .suggestions li:hover {
    background: rgba(212, 175, 55, 0.1);
  }
</style>
```

---

## 6. ContentCard

콘텐츠 카드.

### Props

| Prop | Type | Default | 설명 |
|------|------|---------|------|
| content | Content | (필수) | 콘텐츠 데이터 |
| progress | WatchProgress | null | 시청 진행률 |
| showSeries | boolean | true | 시리즈명 표시 |

### Events

| Event | Payload | 설명 |
|-------|---------|------|
| click | Content | 카드 클릭 |

### 구현

```svelte
<!-- packages/ui/src/ContentCard.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Content, WatchProgress } from '@wsoptv/types';

  export let content: Content;
  export let progress: WatchProgress | null = null;
  export let showSeries = true;

  const dispatch = createEventDispatcher<{ click: Content }>();

  function formatDuration(sec: number): string {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return h > 0 ? `${h}시간 ${m}분` : `${m}분`;
  }

  $: progressPercent = progress
    ? Math.round((progress.progressSec / progress.durationSec) * 100)
    : 0;
</script>

<article
  class="content-card"
  on:click={() => dispatch('click', content)}
>
  <div class="thumbnail">
    {#if content.thumbnailUrl}
      <img src={content.thumbnailUrl} alt={content.title} />
    {:else}
      <div class="placeholder" />
    {/if}

    {#if progress && !progress.completed}
      <div class="progress-bar" style="width: {progressPercent}%" />
    {/if}

    <span class="duration">{formatDuration(content.durationSec)}</span>
  </div>

  <div class="info">
    <h3 class="title">{content.title}</h3>
    {#if showSeries && content.series}
      <span class="series">{content.series.title}</span>
    {/if}
    <div class="meta">
      <span class="views">{content.viewCount.toLocaleString()}회 시청</span>
    </div>
  </div>
</article>

<style>
  .content-card {
    background: var(--wsop-black-light);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .content-card:hover {
    border-color: var(--wsop-gold);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  }

  .thumbnail {
    position: relative;
    aspect-ratio: 16 / 9;
    background: var(--wsop-black);
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, var(--wsop-black) 0%, var(--wsop-black-light) 100%);
  }

  .progress-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 4px;
    background: var(--wsop-gold);
  }

  .duration {
    position: absolute;
    bottom: 8px;
    right: 8px;
    padding: 4px 8px;
    background: rgba(0, 0, 0, 0.8);
    border-radius: 4px;
    font-size: 12px;
    color: white;
  }

  .info {
    padding: 12px;
  }

  .title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--wsop-cream);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .series {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: var(--wsop-gold);
  }

  .meta {
    margin-top: 8px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }
</style>
```

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 컴포넌트 설계 |
| 2.0.0 | 2025-12-09 | 보안/로직 이슈 수정: httpOnly 쿠키, 통합 타입, 하이라이트 모드 (#1, #17, #26, #31) |
