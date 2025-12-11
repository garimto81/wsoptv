<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { homeApi } from '$lib/api/home';
	import type { RowData } from '$lib/types/row';
	import { ContentRow, RowSkeleton } from '$lib/components/home';
	import { authStore } from '$lib/stores';

	let rows = $state<RowData[]>([]);
	let isLoading = $state(true);
	let error = $state('');
	let cached = $state(false);

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}

		await loadHomeRows();
	});

	async function loadHomeRows() {
		isLoading = true;
		error = '';

		try {
			const response = await homeApi.fetchHomeRows(20);
			rows = response.rows;
			cached = response.cached;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'Failed to load content';
			console.error('Home API error:', err);
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>WSOPTV - Poker VOD Streaming</title>
</svelte:head>

<div class="home-page">
	<section class="hero">
		<div class="hero-content">
			<h1>WSOPTV</h1>
			<p>The world's best poker broadcasts in one place</p>
		</div>
	</section>

	<section class="rows-section">
		{#if isLoading}
			<RowSkeleton count={6} />
			<RowSkeleton count={6} />
			<RowSkeleton count={6} />
		{:else if error}
			<div class="error-container">
				<div class="error">
					<span class="error-icon">⚠️</span>
					<p>{error}</p>
					<button onclick={loadHomeRows}>Try Again</button>
				</div>
			</div>
		{:else if rows.length === 0}
			<div class="empty">
				<span class="empty-icon">📺</span>
				<p>No content available</p>
				<p class="empty-hint">Check your Jellyfin server connection</p>
			</div>
		{:else}
			{#each rows as row (row.id)}
				<ContentRow {row} />
			{/each}
		{/if}
	</section>

	{#if cached && !isLoading}
		<div class="cache-indicator" title="Data loaded from cache">
			<span>⚡ Cached</span>
		</div>
	{/if}
</div>

<style>
	.home-page {
		min-height: 100vh;
		padding-bottom: var(--spacing-xl);
	}

	.hero {
		position: relative;
		padding: var(--spacing-xl) var(--spacing-md);
		margin-bottom: var(--spacing-xl);
		background: linear-gradient(
			180deg,
			rgba(229, 9, 20, 0.15) 0%,
			rgba(229, 9, 20, 0.05) 50%,
			transparent 100%
		);
	}

	.hero-content {
		max-width: 1400px;
		margin: 0 auto;
		text-align: center;
	}

	.hero h1 {
		font-size: 3.5rem;
		font-weight: 700;
		color: var(--color-primary);
		margin-bottom: var(--spacing-sm);
		letter-spacing: -0.02em;
	}

	.hero p {
		font-size: 1.25rem;
		color: var(--color-text-muted);
	}

	.rows-section {
		max-width: 1600px;
		margin: 0 auto;
	}

	.error-container {
		display: flex;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.error {
		text-align: center;
		padding: var(--spacing-xl);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-lg);
		max-width: 400px;
	}

	.error-icon {
		font-size: 2rem;
		display: block;
		margin-bottom: var(--spacing-md);
	}

	.error p {
		color: var(--color-error);
		margin-bottom: var(--spacing-md);
	}

	.error button {
		padding: 0.75rem 1.5rem;
		background: var(--color-primary);
		border: none;
		border-radius: var(--radius-md);
		color: white;
		cursor: pointer;
		font-size: 0.875rem;
		transition: background 0.2s ease;
	}

	.error button:hover {
		background: var(--color-primary-hover);
	}

	.empty {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-muted);
	}

	.empty-icon {
		font-size: 3rem;
		display: block;
		margin-bottom: var(--spacing-md);
		opacity: 0.5;
	}

	.empty p {
		font-size: 1.125rem;
		margin-bottom: var(--spacing-xs);
	}

	.empty-hint {
		font-size: 0.875rem;
		opacity: 0.7;
	}

	.cache-indicator {
		position: fixed;
		bottom: 16px;
		right: 16px;
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 0.75rem;
		color: var(--color-text-muted);
		opacity: 0.6;
		transition: opacity 0.2s ease;
	}

	.cache-indicator:hover {
		opacity: 1;
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 2.5rem;
		}

		.hero p {
			font-size: 1rem;
		}

		.cache-indicator {
			display: none;
		}
	}
</style>
