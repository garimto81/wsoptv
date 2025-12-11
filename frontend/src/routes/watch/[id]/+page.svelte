<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import { jellyfinApi, type JellyfinContent, type JellyfinStreamInfo } from '$lib/api/jellyfin';
	import { Spinner } from '$lib/components/ui';
	import { VideoPlayer } from '$lib/components/player';
	import { authStore } from '$lib/stores';

	let content = $state<JellyfinContent | null>(null);
	let streamInfo = $state<JellyfinStreamInfo | null>(null);
	let isLoading = $state(true);
	let error = $state('');
	let currentTime = $state(0);
	let videoPlayer: VideoPlayer;

	const itemId = $derived($page.params.id);

	onMount(async () => {
		// Auth is already initialized by +layout.ts -> +layout.svelte
		// Redirect to login if not authenticated
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}

		if (!itemId) {
			error = 'Invalid content ID';
			isLoading = false;
			return;
		}

		try {
			// Load content and stream info in parallel
			const [contentData, streamData] = await Promise.all([
				jellyfinApi.getContent(itemId),
				jellyfinApi.getStreamInfo(itemId)
			]);

			content = contentData;
			streamInfo = streamData;
		} catch (err: any) {
			console.error('Failed to load content:', err);
			error = err.message || 'Failed to load content';
		} finally {
			isLoading = false;
		}
	});

	function handleTimeUpdate(time: number) {
		currentTime = time;
	}

	function handleSeek(time: number) {
		videoPlayer?.seekToTime(time);
	}

	function handleEnded() {
		// Could implement watch history here in the future
	}

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) {
			return `${hours}h ${minutes}m`;
		}
		return `${minutes}m`;
	}
</script>

<svelte:head>
	<title>{content?.title || 'Now Playing'} - WSOPTV</title>
</svelte:head>

<div class="watch-page">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error-container">
			<div class="error">{error}</div>
			<a href="/" class="back-link">Back to Library</a>
		</div>
	{:else if content && streamInfo}
		<div class="player-section">
			<VideoPlayer
				bind:this={videoPlayer}
				src={streamInfo.hlsUrl}
				poster={content.thumbnailUrl || streamInfo.thumbnailUrl}
				onTimeUpdate={handleTimeUpdate}
				onEnded={handleEnded}
			/>
		</div>

		<div class="content-section container">
			<div class="main-content">
				<header class="content-header">
					{#if content.libraryName}
						<div class="breadcrumb">
							<a href="/">{content.libraryName}</a>
						</div>
					{/if}
					<h1>{content.title}</h1>
					{#if content.description}
						<p class="description">{content.description}</p>
					{/if}
					<div class="meta">
						{#if content.year}
							<span>{content.year}</span>
						{/if}
						{#if content.durationSec}
							<span>{formatDuration(content.durationSec)}</span>
						{/if}
						{#if content.mediaType}
							<span>{content.mediaType}</span>
						{/if}
					</div>
				</header>
			</div>

			<aside class="sidebar">
				<div class="stream-info">
					<h3>Stream Info</h3>
					<div class="info-row">
						<span class="label">Format:</span>
						<span class="value">{content.supportsHls ? 'HLS' : 'Direct'}</span>
					</div>
					<div class="info-row">
						<span class="label">Duration:</span>
						<span class="value">{formatDuration(content.durationSec)}</span>
					</div>
					{#if content.path}
						<div class="info-row">
							<span class="label">Path:</span>
							<span class="value path">{content.path}</span>
						</div>
					{/if}
				</div>

				<div class="actions">
					<a href="/" class="btn-secondary">Back to Library</a>
				</div>
			</aside>
		</div>
	{/if}
</div>

<style>
	.watch-page {
		min-height: calc(100vh - 64px);
		background: var(--color-bg);
	}

	.loading {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 50vh;
	}

	.error-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		gap: var(--spacing-lg);
	}

	.error {
		padding: var(--spacing-md);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
	}

	.back-link {
		color: var(--color-primary);
		text-decoration: none;
	}

	.back-link:hover {
		text-decoration: underline;
	}

	.player-section {
		background: black;
		max-width: 1600px;
		margin: 0 auto;
	}

	.content-section {
		display: grid;
		grid-template-columns: 1fr 350px;
		gap: var(--spacing-xl);
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.content-header {
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

	.content-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: var(--spacing-sm);
	}

	.description {
		color: var(--color-text-muted);
		line-height: 1.6;
		margin-bottom: var(--spacing-sm);
	}

	.meta {
		display: flex;
		gap: var(--spacing-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.meta span:not(:last-child)::after {
		content: '|';
		margin-left: var(--spacing-md);
		color: var(--color-border);
	}

	.sidebar {
		position: sticky;
		top: 80px;
		align-self: start;
	}

	.stream-info {
		padding: var(--spacing-lg);
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		margin-bottom: var(--spacing-lg);
	}

	.stream-info h3 {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: var(--spacing-md);
	}

	.info-row {
		display: flex;
		justify-content: space-between;
		padding: var(--spacing-sm) 0;
		border-bottom: 1px solid var(--color-border);
	}

	.info-row:last-child {
		border-bottom: none;
	}

	.label {
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	.value {
		font-size: 0.875rem;
		text-align: right;
	}

	.value.path {
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.actions {
		display: flex;
		gap: var(--spacing-md);
	}

	.btn-secondary {
		padding: 0.75rem 1.5rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		text-decoration: none;
		font-size: 0.875rem;
		transition: all 0.2s ease;
		text-align: center;
		flex: 1;
	}

	.btn-secondary:hover {
		background: var(--color-surface-hover);
	}

	@media (max-width: 1024px) {
		.content-section {
			grid-template-columns: 1fr;
		}

		.sidebar {
			position: static;
		}
	}
</style>
