<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { homeApi } from '$lib/api/home';
	import { jellyfinApi, type JellyfinLibrary } from '$lib/api/jellyfin';
	import type { RowItem } from '$lib/types/row';
	import { FilterBar, ContentGrid } from '$lib/components/browse';
	import { Spinner } from '$lib/components/ui';
	import { authStore } from '$lib/stores';

	let items = $state<RowItem[]>([]);
	let libraries = $state<JellyfinLibrary[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');

	let selectedLibrary = $state<string | undefined>(undefined);
	let sortBy = $state('DateCreated');
	let sortOrder = $state('Descending');
	let currentPage = $state(1);
	let hasNext = $state(false);
	let total = $state(0);

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}

		// Parse URL params
		const urlParams = $page.url.searchParams;
		selectedLibrary = urlParams.get('library') || undefined;
		sortBy = urlParams.get('sort') || 'DateCreated';
		sortOrder = urlParams.get('order') || 'Descending';

		await Promise.all([loadLibraries(), loadContents()]);
	});

	async function loadLibraries() {
		try {
			libraries = await jellyfinApi.getLibraries();
		} catch (err) {
			console.error('Failed to load libraries:', err);
		}
	}

	async function loadContents(loadMore = false) {
		if (loadMore) {
			isLoadingMore = true;
		} else {
			isLoading = true;
			currentPage = 1;
		}
		error = '';

		try {
			const response = await homeApi.fetchBrowseContents({
				library: selectedLibrary,
				sort: sortBy,
				order: sortOrder,
				page: loadMore ? currentPage : 1,
				limit: 24
			});

			if (loadMore) {
				items = [...items, ...response.items];
			} else {
				items = response.items;
			}
			total = response.total;
			hasNext = response.hasNext;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'Failed to load content';
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	function handleFilterChange() {
		// Update URL
		const params = new URLSearchParams();
		if (selectedLibrary) params.set('library', selectedLibrary);
		if (sortBy !== 'DateCreated') params.set('sort', sortBy);
		if (sortOrder !== 'Descending') params.set('order', sortOrder);

		const newUrl = params.toString() ? `/browse?${params}` : '/browse';
		history.replaceState({}, '', newUrl);

		loadContents();
	}

	function loadMore() {
		currentPage++;
		loadContents(true);
	}
</script>

<svelte:head>
	<title>Browse - WSOPTV</title>
</svelte:head>

<div class="browse-page container">
	<header class="page-header">
		<h1>Browse</h1>
		<p class="subtitle">{total.toLocaleString()} items</p>
	</header>

	<FilterBar
		{libraries}
		bind:selectedLibrary
		bind:sortBy
		bind:sortOrder
		onFilterChange={handleFilterChange}
	/>

	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">
			<span class="error-icon">⚠️</span>
			<p>{error}</p>
			<button onclick={() => loadContents()}>Try Again</button>
		</div>
	{:else}
		<ContentGrid {items} />

		{#if hasNext}
			<div class="load-more">
				<button onclick={loadMore} disabled={isLoadingMore}>
					{#if isLoadingMore}
						<Spinner size="sm" />
					{:else}
						Load More
					{/if}
				</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.browse-page {
		padding: var(--spacing-xl) var(--spacing-md);
		max-width: 1600px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: var(--spacing-xl);
	}

	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.subtitle {
		color: var(--color-text-muted);
	}

	.loading {
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
		margin: 0 auto;
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
	}

	.load-more {
		display: flex;
		justify-content: center;
		margin-top: var(--spacing-xl);
	}

	.load-more button {
		padding: 0.75rem 2rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s ease;
	}

	.load-more button:hover:not(:disabled) {
		background: var(--color-surface-hover);
		border-color: var(--color-primary);
	}

	.load-more button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
