<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner } from '$lib/components/ui';

	interface Content {
		id: number;
		title: string;
		thumbnailUrl: string | null;
		durationSec: number;
		viewCount: number;
		series?: {
			id: number;
			title: string;
			catalogId: string;
		};
	}

	interface ContentResponse {
		items: Content[];
		total: number;
		page: number;
		hasNext: boolean;
	}

	let contents = $state<Content[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let page = $state(1);
	let hasNext = $state(false);
	let total = $state(0);
	let sortBy = $state<'recent' | 'popular'>('recent');

	onMount(async () => {
		await loadContents();
	});

	async function loadContents(loadMore = false) {
		if (loadMore) {
			isLoadingMore = true;
		} else {
			isLoading = true;
			page = 1;
		}
		error = '';

		try {
			const params = new URLSearchParams();
			params.set('page', page.toString());
			params.set('limit', '24');
			params.set('sort', sortBy);

			const response = await api.get<ContentResponse>(`/contents?${params}`);

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

	function changeSort(newSort: typeof sortBy) {
		sortBy = newSort;
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

	function formatViewCount(count: number): string {
		if (count >= 1000000) {
			return `${(count / 1000000).toFixed(1)}M`;
		}
		if (count >= 1000) {
			return `${(count / 1000).toFixed(1)}K`;
		}
		return count.toString();
	}
</script>

<svelte:head>
	<title>Browse - WSOPTV</title>
</svelte:head>

<div class="browse-page container">
	<header class="page-header">
		<div class="header-content">
			<h1>Browse</h1>
			<p class="subtitle">{total.toLocaleString()} contents</p>
		</div>

		<div class="sort-options">
			<button
				class="sort-btn"
				class:active={sortBy === 'recent'}
				onclick={() => changeSort('recent')}
			>
				Recent
			</button>
			<button
				class="sort-btn"
				class:active={sortBy === 'popular'}
				onclick={() => changeSort('popular')}
			>
				Popular
			</button>
		</div>
	</header>

	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else}
		<div class="content-grid">
			{#each contents as content}
				<a href="/watch/{content.id}" class="content-card">
					<Card variant="clickable" padding="none">
						<div class="content-thumbnail">
							{#if content.thumbnailUrl}
								<img src={content.thumbnailUrl} alt={content.title} />
							{:else}
								<div class="thumb-placeholder"></div>
							{/if}
							<span class="duration">{formatDuration(content.durationSec)}</span>
						</div>
						<div class="content-info">
							<h3>{content.title}</h3>
							{#if content.series}
								<a href="/catalog/{content.series.catalogId}" class="series-link">
									{content.series.catalogId.toUpperCase()}
								</a>
							{/if}
							<div class="meta">
								<span>{formatViewCount(content.viewCount)} views</span>
							</div>
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
	.browse-page {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
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

	.sort-options {
		display: flex;
		gap: var(--spacing-sm);
	}

	.sort-btn {
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s ease;
	}

	.sort-btn:hover {
		background: var(--color-surface-hover);
	}

	.sort-btn.active {
		background: var(--color-primary);
		border-color: var(--color-primary);
		color: white;
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

	.series-link {
		display: inline-block;
		font-size: 0.75rem;
		color: var(--color-primary);
		text-decoration: none;
		margin-bottom: var(--spacing-xs);
	}

	.series-link:hover {
		text-decoration: underline;
	}

	.meta {
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
			gap: var(--spacing-md);
		}

		.content-grid {
			grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
		}
	}
</style>
