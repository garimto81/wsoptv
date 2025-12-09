<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores';
	import { Card, Spinner, Button } from '$lib/components/ui';

	interface HistoryItem {
		contentId: number;
		title: string;
		thumbnailUrl: string | null;
		durationSec: number;
		progressSec: number;
		progressPercent: number;
		completed: boolean;
		lastWatched: string;
	}

	interface HistoryResponse {
		items: HistoryItem[];
		total: number;
		page: number;
		limit: number;
		hasNext: boolean;
	}

	let items = $state<HistoryItem[]>([]);
	let total = $state(0);
	let page = $state(1);
	let hasNext = $state(false);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let filter = $state<'all' | 'completed' | 'in-progress'>('all');

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadHistory();
	});

	async function loadHistory(loadMore = false) {
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
			params.set('limit', '20');

			if (filter === 'completed') {
				params.set('completed', 'true');
			} else if (filter === 'in-progress') {
				params.set('completed', 'false');
			}

			const response = await api.get<HistoryResponse>(`/users/history?${params}`);

			if (loadMore) {
				items = [...items, ...response.items];
			} else {
				items = response.items;
			}
			total = response.total;
			hasNext = response.hasNext;
		} catch (err: any) {
			error = err.message || 'Failed to load watch history';
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	function loadMore() {
		page++;
		loadHistory(true);
	}

	function setFilter(newFilter: typeof filter) {
		filter = newFilter;
		loadHistory();
	}

	async function removeItem(contentId: number) {
		try {
			await api.delete(`/users/history/${contentId}`);
			items = items.filter((item) => item.contentId !== contentId);
			total--;
		} catch {
			// Silently fail
		}
	}

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) {
			return `${hours}h ${minutes}m`;
		}
		return `${minutes}m`;
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (days === 0) return 'Today';
		if (days === 1) return 'Yesterday';
		if (days < 7) return `${days} days ago`;
		return date.toLocaleDateString('en-US');
	}
</script>

<svelte:head>
	<title>Watch History - WSOPTV</title>
</svelte:head>

<div class="history-page container">
	<header class="page-header">
		<h1>Watch History</h1>
		<p class="subtitle">{total} items</p>
	</header>

	<div class="filter-tabs">
		<button
			class="filter-tab"
			class:active={filter === 'all'}
			onclick={() => setFilter('all')}
		>
			All
		</button>
		<button
			class="filter-tab"
			class:active={filter === 'in-progress'}
			onclick={() => setFilter('in-progress')}
		>
			In Progress
		</button>
		<button
			class="filter-tab"
			class:active={filter === 'completed'}
			onclick={() => setFilter('completed')}
		>
			Completed
		</button>
	</div>

	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if items.length === 0}
		<div class="empty">
			<p>No watch history found</p>
			<a href="/">
				<Button variant="primary">Browse Content</Button>
			</a>
		</div>
	{:else}
		<div class="history-list">
			{#each items as item}
				<div class="history-item">
					<Card variant="hover" padding="none">
						<div class="item-layout">
							<a href="/watch/{item.contentId}" class="item-thumbnail">
								{#if item.thumbnailUrl}
									<img src={item.thumbnailUrl} alt={item.title} />
								{:else}
									<div class="thumb-placeholder"></div>
								{/if}
								<div class="progress-bar">
									<div class="progress-fill" style="width: {item.progressPercent}%"></div>
								</div>
								{#if item.completed}
									<span class="completed-badge">Done</span>
								{/if}
							</a>

							<div class="item-info">
								<a href="/watch/{item.contentId}" class="item-title">
									{item.title}
								</a>
								<div class="item-meta">
									<span>
										{formatDuration(item.progressSec)} / {formatDuration(item.durationSec)}
									</span>
									<span class="separator">·</span>
									<span>{formatDate(item.lastWatched)}</span>
								</div>
							</div>

							<div class="item-actions">
								<a href="/watch/{item.contentId}">
									<Button variant="primary" size="sm">
										{item.completed ? 'Watch Again' : 'Continue'}
									</Button>
								</a>
								<button
									class="remove-btn"
									onclick={() => removeItem(item.contentId)}
									aria-label="Remove from history"
								>
									✕
								</button>
							</div>
						</div>
					</Card>
				</div>
			{/each}
		</div>

		{#if hasNext}
			<div class="load-more">
				<Button variant="secondary" loading={isLoadingMore} onclick={loadMore}>
					Load More
				</Button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.history-page {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.page-header {
		margin-bottom: var(--spacing-lg);
	}

	.page-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.subtitle {
		color: var(--color-text-muted);
	}

	.filter-tabs {
		display: flex;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-xl);
	}

	.filter-tab {
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s ease;
	}

	.filter-tab:hover {
		background: var(--color-surface-hover);
	}

	.filter-tab.active {
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

	.empty {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-muted);
	}

	.empty p {
		margin-bottom: var(--spacing-md);
	}

	.history-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.item-layout {
		display: grid;
		grid-template-columns: 200px 1fr auto;
		gap: var(--spacing-md);
		align-items: center;
		padding: var(--spacing-sm);
	}

	.item-thumbnail {
		position: relative;
		aspect-ratio: 16 / 9;
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.item-thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumb-placeholder {
		width: 100%;
		height: 100%;
		background: var(--color-surface-hover);
	}

	.progress-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: rgba(255, 255, 255, 0.3);
	}

	.progress-fill {
		height: 100%;
		background: var(--color-primary);
	}

	.completed-badge {
		position: absolute;
		top: 8px;
		right: 8px;
		padding: 0.125rem 0.375rem;
		background: var(--color-success);
		color: black;
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 600;
	}

	.item-info {
		min-width: 0;
	}

	.item-title {
		display: block;
		font-size: 1rem;
		font-weight: 500;
		color: var(--color-text);
		text-decoration: none;
		margin-bottom: var(--spacing-xs);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.item-title:hover {
		color: var(--color-primary);
	}

	.item-meta {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.separator {
		margin: 0 var(--spacing-xs);
	}

	.item-actions {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.remove-btn {
		background: none;
		border: none;
		color: var(--color-text-muted);
		padding: var(--spacing-xs);
		cursor: pointer;
		border-radius: var(--radius-sm);
	}

	.remove-btn:hover {
		background: var(--color-surface-hover);
		color: var(--color-error);
	}

	.load-more {
		display: flex;
		justify-content: center;
		margin-top: var(--spacing-xl);
	}

	@media (max-width: 768px) {
		.item-layout {
			grid-template-columns: 120px 1fr;
		}

		.item-actions {
			grid-column: 1 / -1;
			justify-content: center;
			margin-top: var(--spacing-sm);
		}
	}
</style>
