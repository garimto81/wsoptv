<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { jellyfinApi, type JellyfinContent, type JellyfinStreamInfo, type ApiError } from '$lib/api';
	import { authStore } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';
	import { VideoPlayer } from '$lib/components/player';

	let content = $state<JellyfinContent | null>(null);
	let streamInfo = $state<JellyfinStreamInfo | null>(null);
	let isLoading = $state(true);
	let error = $state('');
	let requiresAuth = $state(false);
	let currentTime = $state(0);
	let videoPlayer: VideoPlayer;

	const itemId = $derived($page.params.id);

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

		const id = itemId;
		if (!id) {
			error = 'Invalid content ID';
			isLoading = false;
			return;
		}

		try {
			// Load content and stream info in parallel
			const [contentData, streamData] = await Promise.all([
				jellyfinApi.getContent(id),
				jellyfinApi.getStreamInfo(id)
			]);

			content = contentData;
			streamInfo = streamData;
		} catch (err: unknown) {
			const apiErr = err as ApiError;
			// 401 is handled by API client redirect
			if (apiErr.status !== 401) {
				error = apiErr.message || 'Failed to load content';
			}
		} finally {
			isLoading = false;
		}
	});

	function handleTimeUpdate(time: number) {
		currentTime = time;
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
	<title>{content?.title || 'Now Playing'} - WSOPTV</title>
</svelte:head>

<div class="watch-page">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if requiresAuth}
		<div class="auth-required container">
			<div class="auth-message">
				<h2>Login Required</h2>
				<p>You need to sign in to watch this content.</p>
				<a href="/login?redirect=/jellyfin" class="login-btn">Sign In</a>
			</div>
		</div>
	{:else if error}
		<div class="error container">{error}</div>
	{:else if content && streamInfo}
		<div class="player-section">
			<VideoPlayer
				bind:this={videoPlayer}
				src={streamInfo.hlsUrl}
				poster={streamInfo.thumbnailUrl || content.thumbnailUrl || undefined}
				onTimeUpdate={handleTimeUpdate}
			/>
		</div>

		<div class="content-section container">
			<div class="main-content">
				<header class="content-header">
					<div class="breadcrumb">
						<a href="/jellyfin">Jellyfin Library</a>
						{#if content.libraryName}
							<span>/</span>
							<span>{content.libraryName}</span>
						{/if}
					</div>
					<h1>{content.title}</h1>
					{#if content.description}
						<p class="description">{content.description}</p>
					{/if}
					<div class="meta">
						<span class="duration">{formatDuration(content.durationSec)}</span>
						{#if content.year}
							<span class="year">{content.year}</span>
						{/if}
						{#if content.mediaType}
							<span class="media-type">{content.mediaType}</span>
						{/if}
					</div>
				</header>

				<div class="stream-info">
					<h3>Stream Options</h3>
					<div class="stream-options">
						{#if content.supportsHls}
							<div class="stream-option active">
								<span class="option-icon">HLS</span>
								<span class="option-label">Adaptive Streaming (Current)</span>
							</div>
						{/if}
						{#if content.supportsDirectPlay}
							<a href={streamInfo.directUrl} target="_blank" rel="noopener" class="stream-option">
								<span class="option-icon">Direct</span>
								<span class="option-label">Direct Play (No transcoding)</span>
							</a>
						{/if}
					</div>
				</div>

				{#if content.path}
					<div class="file-info">
						<h3>File Information</h3>
						<p class="file-path">{content.path}</p>
					</div>
				{/if}
			</div>
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

	.error {
		padding: var(--spacing-xl);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
		margin: var(--spacing-xl) auto;
	}

	.auth-required {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 50vh;
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

	.player-section {
		background: black;
		max-width: 1600px;
		margin: 0 auto;
	}

	.content-section {
		padding: var(--spacing-xl) var(--spacing-md);
		max-width: 1200px;
		margin: 0 auto;
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
		flex-wrap: wrap;
		gap: var(--spacing-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.meta span {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
	}

	.media-type {
		padding: 0.125rem 0.5rem;
		background: var(--color-surface);
		border-radius: var(--radius-sm);
		text-transform: uppercase;
		font-size: 0.75rem;
	}

	.stream-info,
	.file-info {
		margin-top: var(--spacing-xl);
		padding: var(--spacing-lg);
		background: var(--color-surface);
		border-radius: var(--radius-lg);
	}

	.stream-info h3,
	.file-info h3 {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: var(--spacing-md);
	}

	.stream-options {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
	}

	.stream-option {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		padding: var(--spacing-md);
		background: var(--color-bg);
		border-radius: var(--radius-md);
		text-decoration: none;
		color: var(--color-text);
		transition: background 0.2s ease;
	}

	.stream-option:hover {
		background: var(--color-surface-hover);
	}

	.stream-option.active {
		border: 1px solid var(--color-primary);
	}

	.option-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 48px;
		height: 28px;
		background: var(--color-primary);
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 700;
		color: white;
		text-transform: uppercase;
	}

	.option-label {
		font-size: 0.875rem;
	}

	.file-path {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		font-family: monospace;
		word-break: break-all;
		padding: var(--spacing-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
	}

	@media (max-width: 768px) {
		.content-section {
			padding: var(--spacing-md);
		}
	}
</style>
