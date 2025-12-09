<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	interface Props extends HTMLButtonAttributes {
		variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
		size?: 'sm' | 'md' | 'lg';
		loading?: boolean;
		children: Snippet;
	}

	let {
		variant = 'primary',
		size = 'md',
		loading = false,
		disabled = false,
		children,
		...restProps
	}: Props = $props();
</script>

<button
	class="button {variant} {size}"
	disabled={disabled || loading}
	{...restProps}
>
	{#if loading}
		<span class="spinner"></span>
	{/if}
	{@render children()}
</button>

<style>
	.button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		font-weight: 500;
		border-radius: var(--radius-md);
		border: none;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Variants */
	.primary {
		background: var(--color-primary);
		color: white;
	}

	.primary:hover:not(:disabled) {
		background: var(--color-primary-hover);
	}

	.secondary {
		background: var(--color-surface);
		color: var(--color-text);
		border: 1px solid var(--color-border);
	}

	.secondary:hover:not(:disabled) {
		background: var(--color-surface-hover);
	}

	.ghost {
		background: transparent;
		color: var(--color-text);
	}

	.ghost:hover:not(:disabled) {
		background: var(--color-surface-hover);
	}

	.danger {
		background: var(--color-error);
		color: white;
	}

	.danger:hover:not(:disabled) {
		opacity: 0.9;
	}

	/* Sizes */
	.sm {
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
	}

	.md {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
	}

	.lg {
		padding: 1rem 2rem;
		font-size: 1.125rem;
	}

	/* Spinner */
	.spinner {
		width: 1em;
		height: 1em;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
