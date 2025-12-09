<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { jellyfinApi, type JellyfinContent, type JellyfinStreamInfo } from '$lib/api/jellyfin';
	import { Spinner } from '$lib/components/ui';
	import Hls from 'hls.js';

	interface Props {
		data: { itemId: string };
	}

	let { data }: Props = $props();

	let content = $state<JellyfinContent | null>(null);
	let streamInfo = $state<JellyfinStreamInfo | null>(null);
	let isLoading = $state(true);
	let error = $state('');
	let videoElement = $state<HTMLVideoElement | null>(null);
	let hls: Hls | null = null;

	onMount(async () => {
		await loadContent();
	});

	onDestroy(() => {
		if (hls) {
			hls.destroy();
		}
	});

	async function loadContent() {
		isLoading = true;
		error = '';

		try {
			const [contentData, streamData] = await Promise.all([
				jellyfinApi.getContent(data.itemId),
				jellyfinApi.getStreamInfo(data.itemId)
			]);

			content = contentData;
			streamInfo = streamData;

			// 비디오 초기화
			initializePlayer();
		} catch (err: any) {
			error = err.message || 'Failed to load content';
		} finally {
			isLoading = false;
		}
	}

	function initializePlayer() {
		if (!videoElement || !streamInfo) return;

		const videoSrc = streamInfo.hlsUrl || streamInfo.directUrl;

		if (Hls.isSupported() && streamInfo.hlsUrl) {
			hls = new Hls({
				maxBufferLength: 30,
				maxMaxBufferLength: 60
			});
			hls.loadSource(streamInfo.hlsUrl);
			hls.attachMedia(videoElement);
			hls.on(Hls.Events.MANIFEST_PARSED, () => {
				// Ready to play
			});
			hls.on(Hls.Events.ERROR, (_, data) => {
				if (data.fatal) {
					console.error('HLS Error:', data);
					// Fallback to direct URL
					if (streamInfo?.directUrl) {
						videoElement!.src = streamInfo.directUrl;
					}
				}
			});
		} else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
			// Native HLS support (Safari)
			videoElement.src = videoSrc;
		} else {
			// Fallback to direct URL
			videoElement.src = streamInfo.directUrl;
		}
	}

	// 비디오 엘리먼트가 마운트되면 플레이어 초기화
	$effect(() => {
		if (videoElement && streamInfo && !hls) {
			initializePlayer();
		}
	});
</script>

<svelte:head>
	<title>{content?.title || 'Loading...'} - Jellyfin - WSOPTV</title>
</svelte:head>

<div class="watch-page">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error-container">
			<div class="error">{error}</div>
			<a href="/jellyfin" class="back-link">Back to Library</a>
		</div>
	{:else if content && streamInfo}
		<div class="player-container">
			<video
				bind:this={videoElement}
				controls
				autoplay
				playsinline
				poster={content.thumbnailUrl || streamInfo.thumbnailUrl}
			>
				<track kind="captions" />
			</video>
		</div>

		<div class="content-details container">
			<h1>{content.title}</h1>

			<div class="meta">
				{#if content.year}
					<span class="year">{content.year}</span>
				{/if}
				{#if content.durationSec}
					<span class="duration">{Math.floor(content.durationSec / 60)} min</span>
				{/if}
				{#if content.libraryName}
					<span class="library">{content.libraryName}</span>
				{/if}
			</div>

			{#if content.description}
				<p class="description">{content.description}</p>
			{/if}

			<div class="actions">
				<a href="/jellyfin" class="btn-secondary">Back to Library</a>
			</div>
		</div>
	{/if}
</div>

<style>
	.watch-page {
		min-height: 100vh;
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

	.player-container {
		width: 100%;
		max-width: 1400px;
		margin: 0 auto;
		aspect-ratio: 16 / 9;
		background: black;
	}

	video {
		width: 100%;
		height: 100%;
		outline: none;
	}

	.content-details {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.content-details h1 {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: var(--spacing-md);
	}

	.meta {
		display: flex;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-lg);
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	.meta span {
		display: flex;
		align-items: center;
	}

	.meta span::after {
		content: '|';
		margin-left: var(--spacing-md);
		color: var(--color-border);
	}

	.meta span:last-child::after {
		display: none;
	}

	.description {
		color: var(--color-text-secondary);
		line-height: 1.6;
		margin-bottom: var(--spacing-lg);
		max-width: 800px;
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
	}

	.btn-secondary:hover {
		background: var(--color-surface-hover);
	}

	@media (max-width: 768px) {
		.content-details h1 {
			font-size: 1.25rem;
		}

		.meta {
			flex-wrap: wrap;
			gap: var(--spacing-sm);
		}
	}
</style>
