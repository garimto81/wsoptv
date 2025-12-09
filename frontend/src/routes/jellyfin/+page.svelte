<script lang="ts">
	import { onMount } from 'svelte';
	import { jellyfinApi, type JellyfinContent, type JellyfinLibrary } from '$lib/api/jellyfin';
	import { Card, Spinner } from '$lib/components/ui';

	let contents = $state<JellyfinContent[]>([]);
	let libraries = $state<JellyfinLibrary[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let page = $state(1);
	let hasNext = $state(false);
	let total = $state(0);
	let selectedLibrary = $state<string | undefined>(undefined);
	let searchQuery = $state('');

	onMount(async () => {
		await Promise.all([loadLibraries(), loadContents()]);
	});

	async function loadLibraries() {
		try {
			libraries = await jellyfinApi.getLibraries();
		} catch (err: any) {
			console.error('Failed to load libraries:', err);
		}
	}

	async function loadContents(loadMore = false) {
		if (loadMore) {
			isLoadingMore = true;
		} else {
			isLoading = true;
			page = 1;
		}
		error = '';

		try {
			const response = await jellyfinApi.getContents({
				library: selectedLibrary,
				q: searchQuery || undefined,
				page: loadMore ? page : 1,
				limit: 24
			});

			if (loadMore) {
				contents = [...contents, ...response.items];
			} else {
				contents = response.items;
			}
			total = response.total;
			hasNext = response.hasNext;
		} catch (err: any) {
			error = err.message || 'Failed to load contents';
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	function loadMore() {
		page++;
		loadContents(true);
	}

	function handleLibraryChange(libraryId: string | undefined) {
		selectedLibrary = libraryId;
		loadContents();
	}

	function handleSearch() {
		loadContents();
	}

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) {
			return `${hours}:${minutes.toString().padStart(2, '0')}:00`;
		}
		return `${minutes}:00`;
	}
</script>

<svelte:head>
	<title>Jellyfin Library - WSOPTV</title>
</svelte:head>

<div class="jellyfin-page container">
	<header class="page-header">
		<div class="header-content">
			<h1>Jellyfin Library</h1>
			<p class="subtitle">{total.toLocaleString()} items</p>
		</div>

		<div class="filters">
			<div class="search-box">
				<input
					type="text"
					placeholder="Search..."
					bind:value={searchQuery}
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
				/>
				<button onclick={handleSearch}>Search</button>
			</div>

			<select onchange={(e) => handleLibraryChange(e.currentTarget.value || undefined)}>
				<option value="">All Libraries</option>
				{#each libraries as library}
					<option value={library.id}>{library.name}</option>
				{/each}
			</select>
		</div>
	</header>

	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if contents.length === 0}
		<div class="empty">
			<p>No contents found.</p>
		</div>
	{:else}
		<div class="content-grid">
			{#each contents as content}
				<a href="/jellyfin/watch/{content.jellyfinId}" class="content-card">
					<Card variant="clickable" padding="none">
						<div class="content-thumbnail">
							{#if content.thumbnailUrl}
								<img src={content.thumbnailUrl} alt={content.title} />
							{:else}
								<div class="thumb-placeholder"></div>
							{/if}
							<span class="duration">{formatDuration(content.durationSec)}</span>
							{#if content.supportsHls}
								<span class="badge hls">HLS</span>
							{/if}
						</div>
						<div class="content-info">
							<h3>{content.title}</h3>
							{#if content.libraryName}
								<span class="library-name">{content.libraryName}</span>
							{/if}
							{#if content.year}
								<span class="year">{content.year}</span>
							{/if}
						</div>
					</Card>
				</a>
			{/each}
		</div>

		{#if hasNext}
			<div class="load-more">
				<button
					class="load-more-btn"
					onclick={loadMore}
					disabled={isLoadingMore}
				>
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
	.jellyfin-page {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: var(--spacing-xl);
		flex-wrap: wrap;
		gap: var(--spacing-md);
	}

	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.subtitle {
		color: var(--color-text-muted);
	}

	.filters {
		display: flex;
		gap: var(--spacing-md);
		align-items: center;
		flex-wrap: wrap;
	}

	.search-box {
		display: flex;
		gap: var(--spacing-xs);
	}

	.search-box input {
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		font-size: 0.875rem;
		min-width: 200px;
	}

	.search-box button {
		padding: 0.5rem 1rem;
		background: var(--color-primary);
		border: none;
		border-radius: var(--radius-md);
		color: white;
		cursor: pointer;
		font-size: 0.875rem;
	}

	.filters select {
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		font-size: 0.875rem;
		cursor: pointer;
	}

	.loading {
		display: flex;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.error {
		padding: var(--spacing-md);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
	}

	.empty {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-muted);
	}

	.content-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--spacing-lg);
	}

	.content-card {
		text-decoration: none;
	}

	.content-thumbnail {
		position: relative;
		aspect-ratio: 16 / 9;
		overflow: hidden;
	}

	.content-thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumb-placeholder {
		width: 100%;
		height: 100%;
		background: var(--color-surface-hover);
	}

	.duration {
		position: absolute;
		bottom: 8px;
		right: 8px;
		padding: 0.125rem 0.375rem;
		background: rgba(0, 0, 0, 0.8);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
	}

	.badge {
		position: absolute;
		top: 8px;
		left: 8px;
		padding: 0.125rem 0.5rem;
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.badge.hls {
		background: var(--color-primary);
		color: white;
	}

	.content-info {
		padding: var(--spacing-sm);
	}

	.content-info h3 {
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: var(--spacing-xs);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.library-name {
		display: inline-block;
		font-size: 0.75rem;
		color: var(--color-primary);
		margin-right: var(--spacing-sm);
	}

	.year {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.load-more {
		display: flex;
		justify-content: center;
		margin-top: var(--spacing-xl);
	}

	.load-more-btn {
		padding: 0.75rem 2rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s ease;
	}

	.load-more-btn:hover:not(:disabled) {
		background: var(--color-surface-hover);
	}

	.load-more-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.filters {
			width: 100%;
		}

		.search-box {
			flex: 1;
		}

		.search-box input {
			flex: 1;
			min-width: 0;
		}

		.content-grid {
			grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
		}
	}
</style>
