<script lang="ts">
  /**
   * Timeline Component
   *
   * 핸드 타임라인 시각화 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { getSegmentColor, timeToPosition } from '../hooks/usePlayer';
  import type { TimelineSegment, HandGrade } from '../types';

  interface Props {
    segments: TimelineSegment[];
    currentTime: number;
    duration: number;
    onSeek?: (time: number) => void;
  }

  let { segments, currentTime, duration, onSeek }: Props = $props();

  let hoveredSegment = $state<TimelineSegment | null>(null);
  let tooltipPosition = $state({ x: 0, y: 0 });

  function handleSegmentClick(segment: TimelineSegment) {
    onSeek?.(segment.startSec);
  }

  function handleMouseEnter(segment: TimelineSegment, e: MouseEvent) {
    hoveredSegment = segment;
    const target = e.currentTarget as HTMLElement;
    const rect = target.getBoundingClientRect();
    tooltipPosition = {
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    };
  }

  function handleMouseLeave() {
    hoveredSegment = null;
  }

  function getSegmentWidth(segment: TimelineSegment): number {
    return ((segment.endSec - segment.startSec) / duration) * 100;
  }

  function getSegmentLeft(segment: TimelineSegment): number {
    return (segment.startSec / duration) * 100;
  }

  function isCurrentSegment(segment: TimelineSegment): boolean {
    return currentTime >= segment.startSec && currentTime < segment.endSec;
  }
</script>

<div class="timeline">
  <div class="timeline-track">
    {#each segments as segment (segment.startSec)}
      <button
        class="timeline-segment"
        class:current={isCurrentSegment(segment)}
        class:hand={segment.type === 'hand'}
        style="
          left: {getSegmentLeft(segment)}%;
          width: {getSegmentWidth(segment)}%;
          background-color: {getSegmentColor(segment.type, segment.hand?.grade as HandGrade | undefined)};
        "
        onclick={() => handleSegmentClick(segment)}
        onmouseenter={(e) => handleMouseEnter(segment, e)}
        onmouseleave={handleMouseLeave}
        aria-label="{segment.type === 'hand' ? `핸드 #${segment.hand?.handNumber}` : segment.type}"
      ></button>
    {/each}

    <!-- Current Time Indicator -->
    <div
      class="current-indicator"
      style="left: {timeToPosition(currentTime, duration)}%"
    ></div>
  </div>

  <!-- Tooltip -->
  {#if hoveredSegment}
    <div
      class="tooltip"
      style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px"
    >
      {#if hoveredSegment.type === 'hand' && hoveredSegment.hand}
        <div class="tooltip-content">
          <span class="hand-badge" style="background: {getSegmentColor('hand', hoveredSegment.hand.grade)}">
            {hoveredSegment.hand.grade}
          </span>
          <span class="hand-number">핸드 #{hoveredSegment.hand.handNumber}</span>
          {#if hoveredSegment.hand.players.length > 0}
            <span class="hand-players">{hoveredSegment.hand.players.join(' vs ')}</span>
          {/if}
        </div>
      {:else}
        <span class="segment-type">{hoveredSegment.type}</span>
      {/if}
    </div>
  {/if}
</div>

<style>
  .timeline {
    position: relative;
    width: 100%;
    padding: 8px 0;
  }

  .timeline-track {
    position: relative;
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: visible;
  }

  .timeline-segment {
    position: absolute;
    top: 0;
    height: 100%;
    min-width: 2px;
    border: none;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity 0.2s, transform 0.2s;
    border-radius: 2px;
  }

  .timeline-segment:hover {
    opacity: 1;
    transform: scaleY(1.5);
    z-index: 10;
  }

  .timeline-segment.current {
    opacity: 1;
    transform: scaleY(1.3);
  }

  .timeline-segment.hand {
    border-radius: 4px;
  }

  .current-indicator {
    position: absolute;
    top: -4px;
    width: 2px;
    height: calc(100% + 8px);
    background: white;
    transform: translateX(-50%);
    pointer-events: none;
    z-index: 20;
  }

  .tooltip {
    position: fixed;
    transform: translate(-50%, -100%);
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
  }

  .tooltip::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: rgba(0, 0, 0, 0.9);
  }

  .tooltip-content {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .hand-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 10px;
  }

  .hand-number {
    font-weight: 500;
  }

  .hand-players {
    color: rgba(255, 255, 255, 0.7);
    font-size: 11px;
  }

  .segment-type {
    text-transform: capitalize;
  }
</style>
