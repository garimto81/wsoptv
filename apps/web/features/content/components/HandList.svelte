<script lang="ts">
  /**
   * HandList Component
   *
   * 핸드 목록 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { formatDuration } from '$shared/utils';
  import { getGradeLabel, getGradeColor } from '../hooks/useContent';
  import type { Hand, HandGrade } from '../types';

  interface Props {
    hands: Hand[];
    currentTime?: number;
    selectedGrades?: HandGrade[];
    onHandClick?: (hand: Hand) => void;
    onGradeFilterChange?: (grades: HandGrade[]) => void;
  }

  let {
    hands,
    currentTime = 0,
    selectedGrades = [],
    onHandClick,
    onGradeFilterChange
  }: Props = $props();

  const allGrades: HandGrade[] = ['S', 'A', 'B', 'C'];

  // 필터링된 핸드
  const filteredHands = $derived(
    selectedGrades.length === 0
      ? hands
      : hands.filter((hand) => selectedGrades.includes(hand.grade))
  );

  // 현재 재생 중인 핸드
  const currentHand = $derived(
    hands.find((hand) => currentTime >= hand.startSec && currentTime <= hand.endSec)
  );

  function toggleGrade(grade: HandGrade) {
    const newGrades = selectedGrades.includes(grade)
      ? selectedGrades.filter((g) => g !== grade)
      : [...selectedGrades, grade];
    onGradeFilterChange?.(newGrades);
  }

  function handleHandClick(hand: Hand) {
    onHandClick?.(hand);
  }
</script>

<div class="hand-list">
  <!-- Grade Filters -->
  <div class="grade-filters">
    {#each allGrades as grade}
      <button
        class="grade-filter"
        class:selected={selectedGrades.includes(grade)}
        style="--grade-color: {getGradeColor(grade)}"
        onclick={() => toggleGrade(grade)}
      >
        <span class="grade-badge">{grade}</span>
        <span class="grade-label">{getGradeLabel(grade)}</span>
      </button>
    {/each}
  </div>

  <!-- Hand Items -->
  <div class="hand-items">
    {#each filteredHands as hand (hand.id)}
      <button
        class="hand-item"
        class:current={currentHand?.id === hand.id}
        onclick={() => handleHandClick(hand)}
      >
        <div class="hand-header">
          <span
            class="hand-grade"
            style="background: {getGradeColor(hand.grade)}"
          >
            {hand.grade}
          </span>
          <span class="hand-number">#{hand.handNumber}</span>
          <span class="hand-time">
            {formatDuration(hand.startSec)}
          </span>
        </div>

        {#if hand.players.length > 0}
          <div class="hand-players">
            {hand.players.slice(0, 3).join(' vs ')}
            {#if hand.players.length > 3}
              <span class="more">+{hand.players.length - 3}</span>
            {/if}
          </div>
        {/if}

        {#if hand.potSize}
          <div class="hand-pot">
            💰 {hand.potSize.toLocaleString()} BB
          </div>
        {/if}

        {#if hand.description}
          <p class="hand-description">{hand.description}</p>
        {/if}
      </button>
    {/each}

    {#if filteredHands.length === 0}
      <div class="empty">
        선택한 등급의 핸드가 없습니다.
      </div>
    {/if}
  </div>
</div>

<style>
  .hand-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md, 1rem);
  }

  .grade-filters {
    display: flex;
    gap: var(--spacing-sm, 0.5rem);
    flex-wrap: wrap;
  }

  .grade-filter {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: 1px solid var(--color-border, #e2e8f0);
    border-radius: var(--radius-full, 9999px);
    background: transparent;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }

  .grade-filter:hover {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .grade-filter.selected {
    background: var(--grade-color);
    border-color: var(--grade-color);
    color: white;
  }

  .grade-badge {
    font-weight: 600;
  }

  .hand-items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
    max-height: 400px;
    overflow-y: auto;
  }

  .hand-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border: 1px solid var(--color-border, #e2e8f0);
    border-radius: var(--radius-md, 8px);
    background: transparent;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
  }

  .hand-item:hover {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .hand-item.current {
    border-color: var(--color-primary, #3b82f6);
    background: rgba(59, 130, 246, 0.1);
  }

  .hand-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
  }

  .hand-grade {
    padding: 2px 6px;
    border-radius: 4px;
    color: white;
    font-size: 11px;
    font-weight: 600;
  }

  .hand-number {
    font-weight: 600;
  }

  .hand-time {
    margin-left: auto;
    font-size: 12px;
    color: var(--color-text-muted, #64748b);
  }

  .hand-players {
    font-size: 13px;
    color: var(--color-text-muted, #64748b);
  }

  .hand-players .more {
    color: var(--color-primary, #3b82f6);
  }

  .hand-pot {
    font-size: 13px;
    color: var(--color-warning, #f59e0b);
  }

  .hand-description {
    font-size: 12px;
    color: var(--color-text-muted, #64748b);
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .empty {
    text-align: center;
    padding: var(--spacing-lg, 1.5rem);
    color: var(--color-text-muted, #64748b);
    font-size: 14px;
  }
</style>
