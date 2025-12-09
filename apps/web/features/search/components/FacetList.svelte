<script lang="ts">
  /**
   * FacetList Component
   *
   * 검색 패싯 필터 목록 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import type { Facet, FacetValue } from '../types';

  interface Props {
    facets: Facet[];
    onFilterChange?: (field: string, value: string, selected: boolean) => void;
  }

  let { facets, onFilterChange }: Props = $props();

  function handleValueClick(facet: Facet, value: FacetValue) {
    onFilterChange?.(facet.field, value.value, !value.selected);
  }
</script>

<div class="facet-list">
  {#each facets as facet (facet.field)}
    <div class="facet-group">
      <h4 class="facet-label">{facet.label}</h4>

      <ul class="facet-values">
        {#each facet.values as value (value.value)}
          <li>
            <button
              class="facet-value"
              class:selected={value.selected}
              onclick={() => handleValueClick(facet, value)}
            >
              <span class="value-label">{value.label}</span>
              <span class="value-count">{value.count}</span>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  {/each}

  {#if facets.length === 0}
    <p class="empty">필터가 없습니다.</p>
  {/if}
</div>

<style>
  .facet-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg, 1.5rem);
  }

  .facet-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
  }

  .facet-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text-muted, #64748b);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0;
  }

  .facet-values {
    display: flex;
    flex-direction: column;
    gap: 2px;
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .facet-value {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    cursor: pointer;
    font-size: 14px;
    text-align: left;
    transition: background 0.2s;
  }

  .facet-value:hover {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .facet-value.selected {
    background: rgba(59, 130, 246, 0.1);
    color: var(--color-primary, #3b82f6);
  }

  .value-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .value-count {
    font-size: 12px;
    color: var(--color-text-muted, #64748b);
    background: var(--color-bg-card, #f8fafc);
    padding: 2px 6px;
    border-radius: var(--radius-full, 9999px);
  }

  .facet-value.selected .value-count {
    background: var(--color-primary, #3b82f6);
    color: white;
  }

  .empty {
    font-size: 14px;
    color: var(--color-text-muted, #64748b);
    text-align: center;
    padding: var(--spacing-md, 1rem);
  }
</style>
