<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner } from '$lib/components/ui';

	interface Catalog {
		id: string;
		name: string;
		displayTitle: string;
		description: string | null;
		thumbnailUrl: string | null;
	}

	let catalogs = $state<Catalog[]>([]);
	let isLoading = $state(true);
	let error = $state('');

	onMount(async () => {
		console.log('[v0.1.3] Starting catalog load...');
		try {
			// API 응답: { items: [...], total: N } 구조
			const response = await api.get<{ items: Catalog[]; total: number }>('/catalogs');
			catalogs = response.items || [];
			console.log('[v0.1.3] Catalogs loaded:', catalogs.length);
		} catch (err: any) {
			console.error('[v0.1.3] Catalog load error:', err);
			error = err.message || 'Failed to load catalogs';
		} finally {
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>WSOPTV - Poker VOD Streaming</title>
</svelte:head>

<div class="home">
	<section class="hero">
		<h1>WSOPTV</h1>
		<p>The world's best poker broadcasts in one place</p>
	</section>

	<section class="catalogs container">
		<h2>Catalogs</h2>

		{#if isLoading}
			<div class="loading">
				<Spinner size="lg" />
			</div>
		{:else if error}
			<div class="error">{error}</div>
		{:else}
			<div class="catalog-grid">
				{#each catalogs as catalog}
					<a href="/catalog/{catalog.id}" class="catalog-card">
						<Card variant="clickable" padding="none">
							<div class="catalog-image">
								{#if catalog.thumbnailUrl}
									<img src={catalog.thumbnailUrl} alt={catalog.displayTitle} />
								{:else}
									<div class="catalog-placeholder">
										<span>{catalog.name}</span>
									</div>
								{/if}
							</div>
							<div class="catalog-info">
								<h3>{catalog.displayTitle}</h3>
								{#if catalog.description}
									<p>{catalog.description}</p>
								{/if}
							</div>
						</Card>
					</a>
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	.home {
		padding-bottom: var(--spacing-xl);
	}

	.hero {
		text-align: center;
		padding: var(--spacing-xl) var(--spacing-md);
		background: linear-gradient(180deg, rgba(229, 9, 20, 0.1) 0%, transparent 100%);
	}

	.hero h1 {
		font-size: 3rem;
		font-weight: 700;
		color: var(--color-primary);
		margin-bottom: var(--spacing-sm);
	}

	.hero p {
		font-size: 1.25rem;
		color: var(--color-text-muted);
	}

	.catalogs {
		padding-top: var(--spacing-xl);
	}

	.catalogs h2 {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: var(--spacing-lg);
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

	.catalog-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--spacing-lg);
	}

	.catalog-card {
		text-decoration: none;
	}

	.catalog-image {
		aspect-ratio: 16 / 9;
		overflow: hidden;
	}

	.catalog-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.catalog-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-hover) 100%);
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-text-muted);
	}

	.catalog-info {
		padding: var(--spacing-md);
	}

	.catalog-info h3 {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: var(--spacing-xs);
	}

	.catalog-info p {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	@media (max-width: 768px) {
		.hero h1 {
			font-size: 2rem;
		}

		.catalog-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
