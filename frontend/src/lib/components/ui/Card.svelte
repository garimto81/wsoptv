<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';

	interface Props extends HTMLAttributes<HTMLDivElement> {
		variant?: 'default' | 'hover' | 'clickable';
		padding?: 'none' | 'sm' | 'md' | 'lg';
		children: Snippet;
	}

	let {
		variant = 'default',
		padding = 'md',
		children,
		...restProps
	}: Props = $props();
</script>

<div class="card {variant} padding-{padding}" {...restProps}>
	{@render children()}
</div>

<style>
	.card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.hover:hover {
		border-color: var(--color-text-muted);
	}

	.clickable {
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.clickable:hover {
		border-color: var(--color-primary);
		transform: translateY(-2px);
	}

	.padding-none {
		padding: 0;
	}

	.padding-sm {
		padding: var(--spacing-sm);
	}

	.padding-md {
		padding: var(--spacing-md);
	}

	.padding-lg {
		padding: var(--spacing-lg);
	}
</style>
