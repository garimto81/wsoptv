<script lang="ts">
	import { page } from '$app/stores';
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores';
	import { Spinner } from '$lib/components/ui';
	import { VideoPlayer, HandTimeline } from '$lib/components/player';

	interface Hand {
		id: number;
		handNumber: number | null;
		startSec: number;
		endSec: number;
		winner: string | null;
		potSizeBb: number | null;
		isAllIn: boolean;
		isShowdown: boolean;
		grade: 'S' | 'A' | 'B' | 'C';
	}

	interface Content {
		id: number;
		seriesId: number;
		title: string;
		description: string | null;
		durationSec: number;
		thumbnailUrl: string | null;
		viewCount: number;
		hands: Hand[];
		series?: {
			id: number;
			title: string;
			catalogId: string;
		};
	}

	interface WatchProgress {
		contentId: number;
		progressSec: number;
		durationSec: number;
		completed: boolean;
		version: number;
	}

	let content = $state<Content | null>(null);
	let progress = $state<WatchProgress | null>(null);
	let isLoading = $state(true);
	let error = $state('');
	let currentTime = $state(0);
	let videoPlayer: VideoPlayer;
	let progressSaveInterval: ReturnType<typeof setInterval>;

	const contentId = $derived($page.params.id);
	const streamUrl = $derived(`/api/v1/stream/${contentId}/manifest.m3u8`);

	onMount(async () => {
		try {
			// Load content and progress in parallel
			const [contentData, progressData] = await Promise.all([
				api.get<Content>(`/contents/${contentId}`),
				authStore.isAuthenticated
					? api.get<WatchProgress | null>(`/users/watch-progress/${contentId}`)
					: Promise.resolve(null)
			]);

			content = contentData;
			progress = progressData;

			// Start progress save interval (every 10 seconds)
			if (authStore.isAuthenticated) {
				progressSaveInterval = setInterval(saveProgress, 10000);
			}
		} catch (err: any) {
			error = err.message || 'Failed to load content';
		} finally {
			isLoading = false;
		}
	});

	onDestroy(() => {
		if (progressSaveInterval) {
			clearInterval(progressSaveInterval);
		}
		// Save progress on unmount
		saveProgress();
	});

	async function saveProgress() {
		if (!authStore.isAuthenticated || !content || currentTime === 0) return;

		try {
			progress = await api.post<WatchProgress>('/users/watch-progress', {
				contentId: content.id,
				progressSec: Math.floor(currentTime),
				durationSec: content.durationSec,
				version: progress?.version
			});
		} catch {
			// Silently fail
		}
	}

	function handleTimeUpdate(time: number) {
		currentTime = time;
	}

	function handleSeek(time: number) {
		videoPlayer?.seekToTime(time);
	}

	function handleEnded() {
		saveProgress();
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
		<div class="error container">{error}</div>
	{:else if content}
		<div class="player-section">
			<VideoPlayer
				bind:this={videoPlayer}
				src={streamUrl}
				poster={content.thumbnailUrl || undefined}
				startTime={progress?.progressSec || 0}
				onTimeUpdate={handleTimeUpdate}
				onEnded={handleEnded}
			/>
		</div>

		<div class="content-section container">
			<div class="main-content">
				<header class="content-header">
					{#if content.series}
						<div class="breadcrumb">
							<a href="/catalog/{content.series.catalogId}">{content.series.catalogId.toUpperCase()}</a>
							<span>/</span>
							<a href="/series/{content.series.id}">{content.series.title}</a>
						</div>
					{/if}
					<h1>{content.title}</h1>
					{#if content.description}
						<p class="description">{content.description}</p>
					{/if}
					<div class="meta">
						<span>{content.viewCount.toLocaleString()} views</span>
					</div>
				</header>
			</div>

			<aside class="sidebar">
				{#if content.hands.length > 0}
					<HandTimeline
						hands={content.hands}
						{currentTime}
						duration={content.durationSec}
						onSeek={handleSeek}
					/>
				{:else}
					<div class="no-hands">
						<p>No hand information available</p>
					</div>
				{/if}
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

	.error {
		padding: var(--spacing-xl);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
		margin: var(--spacing-xl) auto;
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
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.sidebar {
		position: sticky;
		top: 80px;
		align-self: start;
	}

	.no-hands {
		padding: var(--spacing-lg);
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		text-align: center;
		color: var(--color-text-muted);
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
