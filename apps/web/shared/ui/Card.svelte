<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'default' | 'bordered' | 'elevated';
    padding?: 'none' | 'sm' | 'md' | 'lg';
    clickable?: boolean;
    onclick?: () => void;
    children: Snippet;
  }

  let {
    variant = 'default',
    padding = 'md',
    clickable = false,
    onclick,
    children
  }: Props = $props();
</script>

{#if clickable}
  <button
    class="card card-{variant} padding-{padding}"
    class:clickable
    type="button"
    {onclick}
  >
    {@render children()}
  </button>
{:else}
  <div class="card card-{variant} padding-{padding}">
    {@render children()}
  </div>
{/if}

<style>
  .card {
    border-radius: var(--radius-lg, 12px);
    background: var(--color-bg-card, #f8fafc);
    width: 100%;
    text-align: left;
  }

  /* Variants */
  .card-default {
    border: none;
  }

  .card-bordered {
    border: 1px solid var(--color-border, #e2e8f0);
  }

  .card-elevated {
    box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
  }

  /* Padding */
  .padding-none {
    padding: 0;
  }

  .padding-sm {
    padding: var(--spacing-sm, 0.5rem);
  }

  .padding-md {
    padding: var(--spacing-md, 1rem);
  }

  .padding-lg {
    padding: var(--spacing-lg, 1.5rem);
  }

  /* Clickable */
  .clickable {
    cursor: pointer;
    border: none;
    font: inherit;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .clickable:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg, 0 10px 15px rgba(0, 0, 0, 0.1));
  }

  .clickable:focus {
    outline: 2px solid var(--color-primary, #3b82f6);
    outline-offset: 2px;
  }
</style>
