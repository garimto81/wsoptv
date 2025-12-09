<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner } from '$lib/components/ui';

	interface Content {
		id: number;
		seriesId: number;
		episodeNum: number | null;
		title: string;
		description: string | null;
		durationSec: number;
		thumbnailUrl: string | null;
		viewCount: number;
	}

	interface Series {
		id: number;
		catalogId: string;
		title: string;
		year: number;
		seasonNum: number | null;
		description: string | null;
		thumbnailUrl: string | null;
		contents: Content[];
	}

	let series = $state<Series | null>(null);
	let isLoading = $state(true);
	let error = $state('');

	const seriesId = $derived($page.params.id);

	onMount(async () => {
		try {
			series = await api.get<Series>(`/series/${seriesId}`);
		} catch (err: any) {
			error = err.message || 'Failed to load series';
		} finally {
			isLoading = false;
		}
	});

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) {
			return `${hours}h ${minutes}m`;
		}
		return `${minutes}m`;
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
	<title>{series?.title || 'Series'} - WSOPTV</title>
</svelte:head>

<div class="series-page container">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if series}
		<header class="series-header">
			<div class="breadcrumb">
				<a href="/catalog/{series.catalogId}">{series.catalogId.toUpperCase()}</a>
				<span>/</span>
				<span>{series.title}</span>
			</div>
			<h1>{series.title}</h1>
			<div class="series-meta">
				<span class="year">{series.year}</span>
				{#if series.seasonNum}
					<span class="season">Season {series.seasonNum}</span>
				{/if}
				<span class="count">{series.contents.length} episodes</span>
			</div>
			{#if series.description}
				<p class="description">{series.description}</p>
			{/if}
		</header>

		<section class="contents-section">
			<h2>Episodes</h2>

			{#if series.contents.length === 0}
				<p class="empty">No episodes available yet.</p>
			{:else}
				<div class="contents-list">
					{#each series.contents as content, index}
						<a href="/watch/{content.id}" class="content-item">
							<Card variant="clickable" padding="sm">
								<div class="content-layout">
									<div class="content-number">
										{content.episodeNum || index + 1}
									</div>
									<div class="content-thumbnail">
										{#if content.thumbnailUrl}
											<img src={content.thumbnailUrl} alt={content.title} />
										{:else}
											<div class="thumbnail-placeholder"></div>
										{/if}
										<span class="duration">{formatDuration(content.durationSec)}</span>
									</div>
									<div class="content-info">
										<h3>{content.title}</h3>
										{#if content.description}
											<p class="content-description">{content.description}</p>
										{/if}
										<div class="content-meta">
											<span class="views">{formatViewCount(content.viewCount)} views</span>
										</div>
									</div>
								</div>
							</Card>
						</a>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>

<style>
	.series-page {
		padding: var(--spacing-xl) var(--spacing-md);
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

	.series-header {
		margin-bottom: var(--spacing-xl);
	}

	.breadcrumb {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		font-size: 0.875rem;
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-sm);
	}

	.breadcrumb a {
		color: var(--color-primary);
		text-decoration: none;
	}

	.breadcrumb a:hover {
		text-decoration: underline;
	}

	.series-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-sm);
	}

	.series-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-md);
	}

	.series-meta span {
		padding: 0.25rem 0.75rem;
		background: var(--color-surface);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.description {
		color: var(--color-text-muted);
		line-height: 1.6;
	}

	.contents-section h2 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: var(--spacing-lg);
	}

	.empty {
		color: var(--color-text-muted);
		text-align: center;
		padding: var(--spacing-xl);
	}

	.contents-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.content-item {
		text-decoration: none;
	}

	.content-layout {
		display: grid;
		grid-template-columns: 40px 200px 1fr;
		gap: var(--spacing-md);
		align-items: center;
	}

	.content-number {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text-muted);
		text-align: center;
	}

	.content-thumbnail {
		position: relative;
		aspect-ratio: 16 / 9;
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.content-thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumbnail-placeholder {
		width: 100%;
		height: 100%;
		background: var(--color-surface-hover);
	}

	.duration {
		position: absolute;
		bottom: 4px;
		right: 4px;
		padding: 2px 6px;
		background: rgba(0, 0, 0, 0.8);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
	}

	.content-info {
		min-width: 0;
	}

	.content-info h3 {
		font-size: 1rem;
		font-weight: 500;
		margin-bottom: var(--spacing-xs);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.content-description {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		margin-bottom: var(--spacing-xs);
	}

	.content-meta {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	@media (max-width: 768px) {
		.content-layout {
			grid-template-columns: 40px 120px 1fr;
		}

		.series-header h1 {
			font-size: 1.5rem;
		}
	}

	@media (max-width: 480px) {
		.content-layout {
			grid-template-columns: 1fr;
			text-align: center;
		}

		.content-number {
			display: none;
		}

		.content-thumbnail {
			max-width: 100%;
		}
	}
</style>
