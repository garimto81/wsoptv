<script lang="ts">
  /**
   * SearchResults Component
   *
   * 검색 결과 목록 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Card, Spinner } from '$shared/ui';
  import { formatDuration } from '$shared/utils';
  import type { SearchHit } from '../types';

  interface Props {
    hits: SearchHit[];
    totalHits: number;
    isLoading?: boolean;
    query?: string;
    onHitClick?: (hit: SearchHit) => void;
  }

  let {
    hits,
    totalHits,
    isLoading = false,
    query = '',
    onHitClick
  }: Props = $props();

  function handleHitClick(hit: SearchHit) {
    onHitClick?.(hit);
  }
</script>

<div class="search-results">
  {#if isLoading}
    <div class="loading">
      <Spinner size="lg" label="검색 중..." />
    </div>
  {:else if hits.length === 0}
    <div class="empty">
      {#if query}
        <p>"{query}"에 대한 검색 결과가 없습니다.</p>
        <p class="hint">다른 검색어를 시도해보세요.</p>
      {:else}
        <p>검색어를 입력하세요.</p>
      {/if}
    </div>
  {:else}
    <div class="results-header">
      <span class="total-count">
        {totalHits.toLocaleString()}개의 결과
      </span>
    </div>

    <ul class="results-list">
      {#each hits as hit (hit.id)}
        <li>
          <Card variant="bordered" padding="md" clickable onclick={() => handleHitClick(hit)}>
            <article class="result-item">
              <div class="result-thumbnail">
                {#if hit.thumbnailUrl}
                  <img src={hit.thumbnailUrl} alt={hit.title} loading="lazy" />
                {:else}
                  <div class="thumbnail-placeholder">🎬</div>
                {/if}
                <span class="duration">{formatDuration(hit.durationSec)}</span>
              </div>

              <div class="result-content">
                <h3 class="result-title">{hit.title}</h3>

                <div class="result-meta">
                  <span class="catalog">{hit.catalogName}</span>
                  {#if hit.episode}
                    <span class="episode">EP.{hit.episode}</span>
                  {/if}
                  {#if hit.season}
                    <span class="season">시즌 {hit.season}</span>
                  {/if}
                </div>

                {#if hit.handCount > 0}
                  <div class="hand-badge">
                    🃏 {hit.handCount}개 핸드
                  </div>
                {/if}

                {#if hit.highlights.length > 0}
                  <div class="highlights">
                    {#each hit.highlights as highlight}
                      <p class="highlight-text">
                        {@html highlight.snippet}
                      </p>
                    {/each}
                  </div>
                {/if}
              </div>
            </article>
          </Card>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .search-results {
    width: 100%;
  }

  .loading,
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl, 2rem);
    text-align: center;
    color: var(--color-text-muted, #64748b);
  }

  .hint {
    font-size: 14px;
    margin-top: var(--spacing-sm, 0.5rem);
  }

  .results-header {
    margin-bottom: var(--spacing-md, 1rem);
  }

  .total-count {
    font-size: 14px;
    color: var(--color-text-muted, #64748b);
  }

  .results-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md, 1rem);
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .result-item {
    display: flex;
    gap: var(--spacing-md, 1rem);
  }

  .result-thumbnail {
    position: relative;
    width: 160px;
    aspect-ratio: 16 / 9;
    flex-shrink: 0;
    border-radius: var(--radius-sm, 4px);
    overflow: hidden;
    background: var(--color-bg-hover, #f1f5f9);
  }

  .result-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumbnail-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
  }

  .duration {
    position: absolute;
    bottom: 4px;
    right: 4px;
    padding: 2px 4px;
    background: rgba(0, 0, 0, 0.75);
    color: white;
    font-size: 11px;
    border-radius: 2px;
  }

  .result-content {
    flex: 1;
    min-width: 0;
  }

  .result-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .result-meta {
    display: flex;
    gap: var(--spacing-sm, 0.5rem);
    font-size: 13px;
    color: var(--color-text-muted, #64748b);
    margin-bottom: var(--spacing-sm, 0.5rem);
  }

  .catalog {
    color: var(--color-primary, #3b82f6);
  }

  .hand-badge {
    font-size: 13px;
    color: var(--color-warning, #f59e0b);
    margin-bottom: var(--spacing-sm, 0.5rem);
  }

  .highlights {
    margin-top: var(--spacing-sm, 0.5rem);
  }

  .highlight-text {
    font-size: 13px;
    color: var(--color-text-muted, #64748b);
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .highlight-text :global(mark) {
    background: rgba(59, 130, 246, 0.2);
    color: var(--color-primary, #3b82f6);
    border-radius: 2px;
  }

  @media (max-width: 640px) {
    .result-item {
      flex-direction: column;
    }

    .result-thumbnail {
      width: 100%;
    }
  }
</style>
