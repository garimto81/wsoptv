<script lang="ts">
	import { onMount } from 'svelte';
	import { jellyfinApi, type JellyfinContent, type JellyfinLibrary, type ApiError } from '$lib/api';
	import { authStore } from '$lib/stores';
	import { Card, Spinner } from '$lib/components/ui';

	let libraries = $state<JellyfinLibrary[]>([]);
	let contents = $state<JellyfinContent[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let requiresAuth = $state(false);
	let page = $state(1);
	let hasNext = $state(false);
	let total = $state(0);
	let selectedLibrary = $state<string | null>(null);
	let searchQuery = $state('');

	onMount(async () => {
		// Wait for auth store to initialize
		if (authStore.isLoading) {
			await new Promise<void>((resolve) => {
				const checkAuth = setInterval(() => {
					if (!authStore.isLoading) {
						clearInterval(checkAuth);
						resolve();
					}
				}, 50);
			});
		}

		// Check authentication before loading data
		if (!authStore.isAuthenticated) {
			requiresAuth = true;
			isLoading = false;
			return;
		}

		await Promise.all([loadLibraries(), loadContents()]);
	});

	async function loadLibraries() {
		try {
			libraries = await jellyfinApi.getLibraries();
		} catch (err: unknown) {
			const apiErr = err as ApiError;
			// 401 is handled by API client redirect
			if (apiErr.status !== 401) {
				console.error('Failed to load libraries:', err);
			}
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
				library: selectedLibrary || undefined,
				q: searchQuery || undefined,
				page,
				limit: 24
			});

			if (loadMore) {
				contents = [...contents, ...response.items];
			} else {
				contents = response.items;
			}
			total = response.total;
			hasNext = response.hasNext;
		} catch (err: unknown) {
			const apiErr = err as ApiError;
			// 401 is handled by API client redirect
			if (apiErr.status !== 401) {
				error = apiErr.message || 'Failed to load contents';
			}
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	function loadMore() {
		page++;
		loadContents(true);
	}

	function selectLibrary(libraryName: string | null) {
		selectedLibrary = libraryName;
		loadContents();
	}

	function handleSearch() {
		loadContents();
	}

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		const secs = seconds % 60;
		if (hours > 0) {
			return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
		}
		return `${minutes}:${secs.toString().padStart(2, '0')}`;
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

		<div class="search-box">
			<input
				type="text"
				placeholder="Search contents..."
				bind:value={searchQuery}
				onkeydown={(e) => e.key === 'Enter' && handleSearch()}
			/>
			<button class="search-btn" onclick={handleSearch}>Search</button>
		</div>
	</header>

	<div class="library-tabs">
		<button
			class="tab-btn"
			class:active={selectedLibrary === null}
			onclick={() => selectLibrary(null)}
		>
			All
		</button>
		{#each libraries as library}
			<button
				class="tab-btn"
				class:active={selectedLibrary === library.name}
				onclick={() => selectLibrary(library.name)}
			>
				{library.name}
			</button>
		{/each}
	</div>

	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if requiresAuth}
		<div class="auth-required">
			<div class="auth-message">
				<h2>Login Required</h2>
				<p>You need to sign in to access the Jellyfin library.</p>
				<a href="/login?redirect=/jellyfin" class="login-btn">Sign In</a>
			</div>
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else}
		<div class="content-grid">
			{#each contents as content}
				<a href="/jellyfin/watch/{content.jellyfinId}" class="content-card">
					<Card variant="clickable" padding="none">
						<div class="content-thumbnail">
							{#if content.thumbnailUrl}
								<img src={content.thumbnailUrl} alt={content.title} loading="lazy" />
							{:else}
								<div class="thumb-placeholder">
									<span class="placeholder-icon">🎬</span>
								</div>
							{/if}
							<span class="duration">{formatDuration(content.durationSec)}</span>
							{#if content.supportsHls}
								<span class="hls-badge">HLS</span>
							{/if}
						</div>
						<div class="content-info">
							<h3>{content.title}</h3>
							{#if content.libraryName}
								<span class="library-tag">{content.libraryName}</span>
							{/if}
							{#if content.year}
								<span class="year">{content.year}</span>
							{/if}
							{#if content.description}
								<p class="description">{content.description}</p>
							{/if}
						</div>
					</Card>
				</a>
			{/each}
		</div>

		{#if contents.length === 0}
			<div class="empty-state">
				<p>No contents found</p>
			</div>
		{/if}

		{#if hasNext}
			<div class="load-more">
				<button class="load-more-btn" onclick={loadMore} disabled={isLoadingMore}>
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
		align-items: flex-end;
		margin-bottom: var(--spacing-lg);
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

	.search-box {
		display: flex;
		gap: var(--spacing-sm);
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

	.search-box input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.search-btn {
		padding: 0.5rem 1rem;
		background: var(--color-primary);
		border: none;
		border-radius: var(--radius-md);
		color: white;
		cursor: pointer;
		font-size: 0.875rem;
		transition: opacity 0.2s ease;
	}

	.search-btn:hover {
		opacity: 0.9;
	}

	.library-tabs {
		display: flex;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-xl);
		flex-wrap: wrap;
	}

	.tab-btn {
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text-muted);
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s ease;
	}

	.tab-btn:hover {
		background: var(--color-surface-hover);
	}

	.tab-btn.active {
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

	.auth-required {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 300px;
	}

	.auth-message {
		text-align: center;
		padding: var(--spacing-xl);
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		max-width: 400px;
	}

	.auth-message h2 {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: var(--spacing-sm);
	}

	.auth-message p {
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-lg);
	}

	.login-btn {
		display: inline-block;
		padding: 0.75rem 2rem;
		background: var(--color-primary);
		color: white;
		text-decoration: none;
		border-radius: var(--radius-md);
		font-weight: 500;
		transition: opacity 0.2s ease;
	}

	.login-btn:hover {
		opacity: 0.9;
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
		background: var(--color-surface-hover);
	}

	.content-thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumb-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-surface-hover);
	}

	.placeholder-icon {
		font-size: 2rem;
		opacity: 0.5;
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

	.hls-badge {
		position: absolute;
		top: 8px;
		right: 8px;
		padding: 0.125rem 0.375rem;
		background: var(--color-primary);
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 600;
		text-transform: uppercase;
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

	.library-tag {
		display: inline-block;
		font-size: 0.625rem;
		padding: 0.125rem 0.375rem;
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
		color: var(--color-text-muted);
		margin-right: var(--spacing-xs);
		text-transform: uppercase;
	}

	.year {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.description {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		margin-top: var(--spacing-xs);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.empty-state {
		text-align: center;
		padding: var(--spacing-xl);
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

		.search-box {
			width: 100%;
		}

		.search-box input {
			flex: 1;
		}

		.content-grid {
			grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
		}
	}
</style>
