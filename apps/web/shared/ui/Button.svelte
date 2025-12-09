<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    loading?: boolean;
    type?: 'button' | 'submit' | 'reset';
    onclick?: (e: MouseEvent) => void;
    children: Snippet;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    type = 'button',
    onclick,
    children
  }: Props = $props();

  const isDisabled = $derived(disabled || loading);
</script>

<button
  {type}
  class="btn btn-{variant} btn-{size}"
  class:loading
  disabled={isDisabled}
  aria-busy={loading}
  {onclick}
>
  {#if loading}
    <span class="spinner" aria-hidden="true"></span>
  {/if}
  {@render children()}
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    font-weight: 500;
    border-radius: var(--radius-md, 8px);
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Sizes */
  .btn-sm {
    height: 32px;
    padding: 0 12px;
    font-size: 14px;
  }

  .btn-md {
    height: 40px;
    padding: 0 16px;
    font-size: 15px;
  }

  .btn-lg {
    height: 48px;
    padding: 0 24px;
    font-size: 16px;
  }

  /* Variants */
  .btn-primary {
    background: var(--color-primary, #3b82f6);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--color-primary-dark, #2563eb);
  }

  .btn-secondary {
    background: var(--color-bg-card, #f8fafc);
    color: var(--color-text, #1e293b);
    border: 1px solid var(--color-border, #e2e8f0);
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .btn-ghost {
    background: transparent;
    color: var(--color-text, #1e293b);
  }

  .btn-ghost:hover:not(:disabled) {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .btn-danger {
    background: var(--color-error, #ef4444);
    color: white;
  }

  .btn-danger:hover:not(:disabled) {
    background: #dc2626;
  }

  /* Loading */
  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
