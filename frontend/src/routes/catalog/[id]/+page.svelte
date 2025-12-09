<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner } from '$lib/components/ui';

	interface Series {
		id: number;
		catalogId: string;
		title: string;
		year: number;
		seasonNum: number | null;
		description: string | null;
		thumbnailUrl: string | null;
		contentCount?: number;
	}

	interface Catalog {
		id: string;
		name: string;
		displayTitle: string;
		description: string | null;
		series: Series[];
	}

	let catalog = $state<Catalog | null>(null);
	let isLoading = $state(true);
	let error = $state('');

	const catalogId = $derived($page.params.id);

	onMount(async () => {
		try {
			catalog = await api.get<Catalog>(`/catalogs/${catalogId}`);
		} catch (err: any) {
			error = err.message || '카탈로그를 불러오는데 실패했습니다';
		} finally {
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>{catalog?.displayTitle || '카탈로그'} - WSOPTV</title>
</svelte:head>

<div class="catalog-page container">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if catalog}
		<header class="catalog-header">
			<h1>{catalog.displayTitle}</h1>
			{#if catalog.description}
				<p>{catalog.description}</p>
			{/if}
		</header>

		<section class="series-section">
			<h2>시리즈</h2>

			{#if catalog.series.length === 0}
				<p class="empty">아직 등록된 시리즈가 없습니다.</p>
			{:else}
				<div class="series-grid">
					{#each catalog.series as series}
						<a href="/series/{series.id}" class="series-card">
							<Card variant="clickable" padding="none">
								<div class="series-image">
									{#if series.thumbnailUrl}
										<img src={series.thumbnailUrl} alt={series.title} />
									{:else}
										<div class="series-placeholder">
											<span>{series.year}</span>
										</div>
									{/if}
								</div>
								<div class="series-info">
									<h3>{series.title}</h3>
									<div class="series-meta">
										<span class="year">{series.year}</span>
										{#if series.seasonNum}
											<span class="season">시즌 {series.seasonNum}</span>
										{/if}
										{#if series.contentCount}
											<span class="count">{series.contentCount}개 에피소드</span>
										{/if}
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
	.catalog-page {
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

	.catalog-header {
		margin-bottom: var(--spacing-xl);
	}

	.catalog-header h1 {
		font-size: 2.5rem;
		font-weight: 700;
		margin-bottom: var(--spacing-sm);
	}

	.catalog-header p {
		color: var(--color-text-muted);
		font-size: 1.125rem;
	}

	.series-section h2 {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: var(--spacing-lg);
	}

	.empty {
		color: var(--color-text-muted);
		text-align: center;
		padding: var(--spacing-xl);
	}

	.series-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: var(--spacing-lg);
	}

	.series-card {
		text-decoration: none;
	}

	.series-image {
		aspect-ratio: 16 / 9;
		overflow: hidden;
	}

	.series-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.series-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-hover) 100%);
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text-muted);
	}

	.series-info {
		padding: var(--spacing-md);
	}

	.series-info h3 {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: var(--spacing-xs);
	}

	.series-meta {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-sm);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.series-meta span {
		padding: 0.125rem 0.5rem;
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
	}

	@media (max-width: 768px) {
		.catalog-header h1 {
			font-size: 1.75rem;
		}

		.series-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
