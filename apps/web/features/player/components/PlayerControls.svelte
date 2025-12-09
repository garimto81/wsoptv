<script lang="ts">
  /**
   * PlayerControls Component
   *
   * 플레이어 컨트롤 바 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { formatDuration } from '$shared/utils';
  import { playerStore } from '../stores/playerStore';
  import { getQualityLabel } from '../hooks/usePlayer';
  import type { QualityLevel } from '../types';

  interface Props {
    videoRef: HTMLVideoElement | null;
    onFullscreen?: () => void;
    onSeek?: (time: number) => void;
  }

  let { videoRef, onFullscreen, onSeek }: Props = $props();

  let showQualityMenu = $state(false);
  const qualityOptions: QualityLevel[] = ['auto', '1080p', '720p', '480p', '360p'];

  function handlePlayPause() {
    if (!videoRef) return;

    if (playerStore.isPaused) {
      videoRef.play().catch(() => {});
    } else {
      videoRef.pause();
    }
  }

  function handleSeekBarClick(e: MouseEvent) {
    const target = e.currentTarget as HTMLDivElement;
    const rect = target.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const time = percent * playerStore.duration;
    onSeek?.(time);
  }

  function handleVolumeChange(e: Event) {
    const target = e.target as HTMLInputElement;
    const volume = parseFloat(target.value);
    playerStore.setVolume(volume);
    if (videoRef) {
      videoRef.volume = volume;
    }
  }

  function handleMuteToggle() {
    playerStore.toggleMute();
    if (videoRef) {
      videoRef.muted = playerStore.isMuted;
    }
  }

  function handleQualitySelect(quality: QualityLevel) {
    playerStore.setQuality(quality);
    showQualityMenu = false;
    // 실제 품질 변경은 HLS에서 처리
  }

  function handleSkipPrev() {
    playerStore.skipToPrevHand();
    if (videoRef) {
      videoRef.currentTime = playerStore.currentTime;
    }
  }

  function handleSkipNext() {
    playerStore.skipToNextHand();
    if (videoRef) {
      videoRef.currentTime = playerStore.currentTime;
    }
  }
</script>

<div class="player-controls">
  <!-- Progress Bar -->
  <div
    class="progress-bar"
    onclick={handleSeekBarClick}
    role="slider"
    aria-label="재생 위치"
    aria-valuenow={playerStore.currentTime}
    aria-valuemin={0}
    aria-valuemax={playerStore.duration}
    tabindex="0"
  >
    <div class="buffered" style="width: {(playerStore.buffered / playerStore.duration) * 100}%"></div>
    <div class="progress" style="width: {(playerStore.currentTime / playerStore.duration) * 100}%"></div>
    <div
      class="thumb"
      style="left: {(playerStore.currentTime / playerStore.duration) * 100}%"
    ></div>
  </div>

  <div class="controls-row">
    <!-- Left Controls -->
    <div class="controls-left">
      <button
        class="control-btn"
        onclick={handlePlayPause}
        aria-label={playerStore.isPaused ? '재생' : '일시정지'}
      >
        {playerStore.isPaused ? '▶️' : '⏸️'}
      </button>

      <button
        class="control-btn"
        onclick={handleSkipPrev}
        aria-label="이전 핸드"
        title="이전 핸드 (P)"
      >
        ⏮️
      </button>

      <button
        class="control-btn"
        onclick={handleSkipNext}
        aria-label="다음 핸드"
        title="다음 핸드 (N)"
      >
        ⏭️
      </button>

      <div class="volume-control">
        <button
          class="control-btn"
          onclick={handleMuteToggle}
          aria-label={playerStore.isMuted ? '음소거 해제' : '음소거'}
        >
          {playerStore.isMuted || playerStore.volume === 0 ? '🔇' : playerStore.volume < 0.5 ? '🔉' : '🔊'}
        </button>
        <input
          type="range"
          class="volume-slider"
          min="0"
          max="1"
          step="0.1"
          value={playerStore.isMuted ? 0 : playerStore.volume}
          oninput={handleVolumeChange}
          aria-label="볼륨"
        />
      </div>

      <span class="time">
        {formatDuration(playerStore.currentTime)} / {formatDuration(playerStore.duration)}
      </span>
    </div>

    <!-- Right Controls -->
    <div class="controls-right">
      {#if playerStore.currentHand}
        <span class="current-hand">
          🃏 #{playerStore.currentHand.handNumber}
        </span>
      {/if}

      <div class="quality-control">
        <button
          class="control-btn quality-btn"
          onclick={() => (showQualityMenu = !showQualityMenu)}
          aria-label="화질 선택"
          aria-expanded={showQualityMenu}
        >
          ⚙️ {getQualityLabel(playerStore.quality)}
        </button>

        {#if showQualityMenu}
          <div class="quality-menu">
            {#each qualityOptions as option}
              <button
                class="quality-option"
                class:selected={playerStore.quality === option}
                onclick={() => handleQualitySelect(option)}
              >
                {getQualityLabel(option)}
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <button
        class="control-btn"
        onclick={onFullscreen}
        aria-label={playerStore.isFullscreen ? '전체화면 종료' : '전체화면'}
      >
        {playerStore.isFullscreen ? '⛶' : '⛶'}
      </button>
    </div>
  </div>
</div>

<style>
  .player-controls {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
  }

  .progress-bar {
    position: relative;
    height: 4px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
    cursor: pointer;
    transition: height 0.2s;
  }

  .progress-bar:hover {
    height: 8px;
  }

  .buffered {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 2px;
  }

  .progress {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background: var(--color-primary, #3b82f6);
    border-radius: 2px;
  }

  .thumb {
    position: absolute;
    top: 50%;
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    opacity: 0;
    transition: opacity 0.2s;
  }

  .progress-bar:hover .thumb {
    opacity: 1;
  }

  .controls-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md, 1rem);
  }

  .controls-left,
  .controls-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
  }

  .control-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    height: 32px;
    padding: 0 8px;
    background: transparent;
    border: none;
    color: white;
    font-size: 16px;
    cursor: pointer;
    border-radius: var(--radius-sm, 4px);
    transition: background 0.2s;
  }

  .control-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .volume-control {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .volume-slider {
    width: 60px;
    height: 4px;
    -webkit-appearance: none;
    appearance: none;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
    cursor: pointer;
  }

  .volume-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
  }

  .time {
    font-size: 13px;
    color: white;
    font-variant-numeric: tabular-nums;
  }

  .current-hand {
    font-size: 13px;
    color: var(--color-warning, #f59e0b);
    background: rgba(245, 158, 11, 0.2);
    padding: 4px 8px;
    border-radius: var(--radius-sm, 4px);
  }

  .quality-control {
    position: relative;
  }

  .quality-btn {
    font-size: 12px;
    gap: 4px;
  }

  .quality-menu {
    position: absolute;
    bottom: 100%;
    right: 0;
    margin-bottom: 8px;
    background: rgba(0, 0, 0, 0.9);
    border-radius: var(--radius-md, 8px);
    overflow: hidden;
    min-width: 120px;
  }

  .quality-option {
    display: block;
    width: 100%;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: white;
    font-size: 13px;
    text-align: left;
    cursor: pointer;
    transition: background 0.2s;
  }

  .quality-option:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .quality-option.selected {
    background: var(--color-primary, #3b82f6);
  }
</style>
