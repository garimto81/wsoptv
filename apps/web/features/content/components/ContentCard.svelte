<script lang="ts">
  /**
   * ContentCard Component
   *
   * 콘텐츠 카드 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Card } from '$shared/ui';
  import { formatDuration } from '$shared/utils';
  import { getGradeColor } from '../hooks/useContent';
  import type { Content } from '../types';

  interface Props {
    content: Content;
    onclick?: (content: Content) => void;
  }

  let { content, onclick }: Props = $props();

  function handleClick() {
    onclick?.(content);
  }
</script>

<Card variant="bordered" padding="none" clickable onclick={handleClick}>
  <article class="content-card">
    <div class="thumbnail">
      {#if content.thumbnailUrl}
        <img src={content.thumbnailUrl} alt={content.title} loading="lazy" />
      {:else}
        <div class="thumbnail-placeholder">
          <span>🎬</span>
        </div>
      {/if}
      <span class="duration">{formatDuration(content.durationSec)}</span>
    </div>

    <div class="info">
      <h3 class="title">{content.title}</h3>
      <p class="meta">
        <span class="catalog">{content.catalogName}</span>
        {#if content.episode}
          <span class="episode">EP.{content.episode}</span>
        {/if}
      </p>

      {#if content.handCount > 0}
        <div class="hand-info">
          <span class="hand-count" style="color: {getGradeColor('A')}">
            🃏 {content.handCount}개 핸드
          </span>
        </div>
      {/if}
    </div>
  </article>
</Card>

<style>
  .content-card {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .thumbnail {
    position: relative;
    aspect-ratio: 16 / 9;
    background: var(--color-bg-hover, #f1f5f9);
    overflow: hidden;
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.2s;
  }

  .content-card:hover .thumbnail img {
    transform: scale(1.05);
  }

  .thumbnail-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
  }

  .duration {
    position: absolute;
    bottom: 8px;
    right: 8px;
    padding: 2px 6px;
    background: rgba(0, 0, 0, 0.75);
    color: white;
    font-size: 12px;
    font-weight: 500;
    border-radius: 4px;
  }

  .info {
    padding: var(--spacing-md, 1rem);
  }

  .title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .meta {
    display: flex;
    gap: 8px;
    font-size: 13px;
    color: var(--color-text-muted, #64748b);
    margin-bottom: 8px;
  }

  .catalog {
    color: var(--color-primary, #3b82f6);
  }

  .hand-info {
    display: flex;
    align-items: center;
  }

  .hand-count {
    font-size: 13px;
    font-weight: 500;
  }
</style>
