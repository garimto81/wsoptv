<script lang="ts">
  /**
   * ContentList Component
   *
   * 콘텐츠 목록 그리드 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Spinner } from '$shared/ui';
  import ContentCard from './ContentCard.svelte';
  import type { Content } from '../types';

  interface Props {
    contents: Content[];
    isLoading?: boolean;
    hasMore?: boolean;
    onContentClick?: (content: Content) => void;
    onLoadMore?: () => void;
  }

  let {
    contents,
    isLoading = false,
    hasMore = false,
    onContentClick,
    onLoadMore
  }: Props = $props();

  // Intersection Observer for infinite scroll
  let loadMoreRef: HTMLDivElement | null = null;

  $effect(() => {
    if (!loadMoreRef || !hasMore || !onLoadMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoading) {
          onLoadMore();
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(loadMoreRef);

    return () => observer.disconnect();
  });
</script>

<div class="content-list">
  {#if contents.length === 0 && !isLoading}
    <div class="empty">
      <p>콘텐츠가 없습니다.</p>
    </div>
  {:else}
    <div class="grid">
      {#each contents as content (content.id)}
        <ContentCard {content} onclick={onContentClick} />
      {/each}
    </div>
  {/if}

  {#if isLoading}
    <div class="loading">
      <Spinner size="lg" label="콘텐츠 로딩 중..." />
    </div>
  {/if}

  {#if hasMore && !isLoading}
    <div class="load-more" bind:this={loadMoreRef}>
      <!-- Intersection observer target -->
    </div>
  {/if}
</div>

<style>
  .content-list {
    width: 100%;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-lg, 1.5rem);
  }

  .empty {
    text-align: center;
    padding: var(--spacing-xl, 2rem);
    color: var(--color-text-muted, #64748b);
  }

  .loading {
    display: flex;
    justify-content: center;
    padding: var(--spacing-xl, 2rem);
  }

  .load-more {
    height: 1px;
  }
</style>
