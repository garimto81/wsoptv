<script lang="ts">
  /**
   * VideoPlayer Component
   *
   * HLS 비디오 플레이어 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { onMount, onDestroy } from 'svelte';
  import Hls from 'hls.js';
  import { Spinner } from '$shared/ui';
  import { playerStore } from '../stores/playerStore';
  import PlayerControls from './PlayerControls.svelte';
  import Timeline from './Timeline.svelte';
  import type { TimelineSegment } from '../types';

  interface Props {
    src: string;
    segments?: TimelineSegment[];
    autoplay?: boolean;
    poster?: string;
    onTimeUpdate?: (time: number) => void;
    onEnded?: () => void;
  }

  let {
    src,
    segments = [],
    autoplay = false,
    poster,
    onTimeUpdate,
    onEnded
  }: Props = $props();

  let videoRef: HTMLVideoElement | null = null;
  let containerRef: HTMLDivElement | null = null;
  let hls: Hls | null = null;
  let showControls = $state(true);
  let controlsTimeout: ReturnType<typeof setTimeout> | null = null;

  // HLS 초기화
  onMount(() => {
    if (!videoRef || !src) return;

    playerStore.setSegments(segments);

    if (Hls.isSupported()) {
      hls = new Hls(playerStore.hlsConfig);
      hls.loadSource(src);
      hls.attachMedia(videoRef);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        playerStore.setLoading(false);
        if (autoplay) {
          videoRef?.play().catch(() => {});
        }
      });

      hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) {
          playerStore.setError({
            code: 'PLAYER_NETWORK_ERROR',
            message: '동영상을 불러올 수 없습니다',
            recoverable: data.details !== 'manifestLoadError'
          });
        }
      });
    } else if (videoRef.canPlayType('application/vnd.apple.mpegurl')) {
      // Safari native HLS
      videoRef.src = src;
      if (autoplay) {
        videoRef.play().catch(() => {});
      }
    }

    playerStore.setLoading(true);
  });

  onDestroy(() => {
    if (hls) {
      hls.destroy();
      hls = null;
    }
    if (controlsTimeout) {
      clearTimeout(controlsTimeout);
    }
    playerStore.reset();
  });

  // 비디오 이벤트 핸들러
  function handleTimeUpdate() {
    if (!videoRef) return;
    playerStore.setCurrentTime(videoRef.currentTime);
    onTimeUpdate?.(videoRef.currentTime);
  }

  function handleDurationChange() {
    if (!videoRef) return;
    playerStore.setDuration(videoRef.duration);
  }

  function handleProgress() {
    if (!videoRef) return;
    const buffered = videoRef.buffered;
    if (buffered.length > 0) {
      playerStore.setBuffered(buffered.end(buffered.length - 1));
    }
  }

  function handlePlay() {
    playerStore.play();
  }

  function handlePause() {
    playerStore.pause();
  }

  function handleEnded() {
    playerStore.pause();
    onEnded?.();
  }

  function handleWaiting() {
    playerStore.setLoading(true);
  }

  function handleCanPlay() {
    playerStore.setLoading(false);
  }

  function handleError() {
    playerStore.setError({
      code: 'PLAYER_DECODE_ERROR',
      message: '동영상 재생 중 오류가 발생했습니다',
      recoverable: true
    });
  }

  // 컨트롤 표시/숨김
  function handleMouseMove() {
    showControls = true;

    if (controlsTimeout) {
      clearTimeout(controlsTimeout);
    }

    controlsTimeout = setTimeout(() => {
      if (playerStore.isPlaying) {
        showControls = false;
      }
    }, 3000);
  }

  // 클릭으로 재생/일시정지
  function handleVideoClick() {
    if (!videoRef) return;

    if (playerStore.isPaused) {
      videoRef.play().catch(() => {});
    } else {
      videoRef.pause();
    }
  }

  // 키보드 단축키
  function handleKeydown(e: KeyboardEvent) {
    if (!videoRef) return;

    switch (e.key) {
      case ' ':
      case 'k':
        e.preventDefault();
        handleVideoClick();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        videoRef.currentTime = Math.max(0, videoRef.currentTime - 10);
        break;
      case 'ArrowRight':
        e.preventDefault();
        videoRef.currentTime = Math.min(videoRef.duration, videoRef.currentTime + 10);
        break;
      case 'ArrowUp':
        e.preventDefault();
        playerStore.setVolume(playerStore.volume + 0.1);
        videoRef.volume = playerStore.volume;
        break;
      case 'ArrowDown':
        e.preventDefault();
        playerStore.setVolume(playerStore.volume - 0.1);
        videoRef.volume = playerStore.volume;
        break;
      case 'm':
        playerStore.toggleMute();
        videoRef.muted = playerStore.isMuted;
        break;
      case 'f':
        handleFullscreen();
        break;
      case 'n':
        // 다음 핸드
        playerStore.skipToNextHand();
        if (videoRef) videoRef.currentTime = playerStore.currentTime;
        break;
      case 'p':
        // 이전 핸드
        playerStore.skipToPrevHand();
        if (videoRef) videoRef.currentTime = playerStore.currentTime;
        break;
    }
  }

  function handleFullscreen() {
    if (!containerRef) return;

    if (!document.fullscreenElement) {
      containerRef.requestFullscreen().catch(() => {});
      playerStore.toggleFullscreen();
    } else {
      document.exitFullscreen();
      playerStore.toggleFullscreen();
    }
  }

  // Seek 핸들러
  function handleSeek(time: number) {
    if (!videoRef) return;
    videoRef.currentTime = time;
    playerStore.setCurrentTime(time);
  }
</script>

<div
  bind:this={containerRef}
  class="video-player"
  class:fullscreen={playerStore.isFullscreen}
  class:show-controls={showControls || playerStore.isPaused}
  onmousemove={handleMouseMove}
  onmouseleave={() => (showControls = false)}
  role="application"
  aria-label="비디오 플레이어"
  tabindex="0"
  onkeydown={handleKeydown}
>
  <video
    bind:this={videoRef}
    class="video"
    {poster}
    playsinline
    onclick={handleVideoClick}
    ontimeupdate={handleTimeUpdate}
    ondurationchange={handleDurationChange}
    onprogress={handleProgress}
    onplay={handlePlay}
    onpause={handlePause}
    onended={handleEnded}
    onwaiting={handleWaiting}
    oncanplay={handleCanPlay}
    onerror={handleError}
  >
    <track kind="captions" />
  </video>

  {#if playerStore.isLoading}
    <div class="loading-overlay">
      <Spinner size="lg" label="버퍼링 중..." />
    </div>
  {/if}

  {#if playerStore.error}
    <div class="error-overlay">
      <p>{playerStore.error.message}</p>
      {#if playerStore.error.recoverable}
        <button onclick={() => window.location.reload()}>다시 시도</button>
      {/if}
    </div>
  {/if}

  <div class="controls-container">
    {#if segments.length > 0}
      <Timeline
        {segments}
        currentTime={playerStore.currentTime}
        duration={playerStore.duration}
        onSeek={handleSeek}
      />
    {/if}

    <PlayerControls
      {videoRef}
      onFullscreen={handleFullscreen}
      onSeek={handleSeek}
    />
  </div>
</div>

<style>
  .video-player {
    position: relative;
    width: 100%;
    background: #000;
    border-radius: var(--radius-lg, 12px);
    overflow: hidden;
    aspect-ratio: 16 / 9;
  }

  .video-player:focus {
    outline: 2px solid var(--color-primary, #3b82f6);
    outline-offset: 2px;
  }

  .video-player.fullscreen {
    border-radius: 0;
  }

  .video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    cursor: pointer;
  }

  .loading-overlay,
  .error-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.7);
    color: white;
  }

  .error-overlay button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: var(--color-primary, #3b82f6);
    color: white;
    border: none;
    border-radius: var(--radius-md, 8px);
    cursor: pointer;
  }

  .controls-container {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: var(--spacing-md, 1rem);
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
    opacity: 0;
    transition: opacity 0.3s;
  }

  .video-player.show-controls .controls-container {
    opacity: 1;
  }
</style>
