<script lang="ts">
	import type { RowItem } from '$lib/types/row';

	interface Props {
		item: RowItem;
	}

	let { item }: Props = $props();

	function formatDuration(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (hours > 0) {
			return `${hours}:${minutes.toString().padStart(2, '0')}:00`;
		}
		return `${minutes}:00`;
	}
</script>

<a href="/watch/{item.id}" class="content-card">
	<div class="thumbnail">
		{#if item.thumbnailUrl}
			<img src={item.thumbnailUrl} alt={item.title} loading="lazy" />
		{:else}
			<div class="thumb-placeholder">
				<span class="placeholder-icon">🎬</span>
			</div>
		{/if}

		<span class="duration">{formatDuration(item.durationSec)}</span>

		{#if item.progress && item.progress > 0}
			<div class="progress-bar">
				<div class="progress-fill" style="width: {item.progress}%"></div>
			</div>
		{/if}
	</div>

	<div class="info">
		<h3 class="title">{item.title}</h3>
		<div class="meta">
			{#if item.libraryName}
				<span class="library">{item.libraryName}</span>
			{/if}
			{#if item.year}
				<span class="year">{item.year}</span>
			{/if}
		</div>
	</div>
</a>

<style>
	.content-card {
		display: block;
		flex: 0 0 auto;
		width: 280px;
		background: var(--color-surface);
		border-radius: var(--radius-md);
		overflow: hidden;
		transition: transform 0.2s ease, box-shadow 0.2s ease;
		text-decoration: none;
		scroll-snap-align: start;
	}

	.content-card:hover {
		transform: scale(1.05);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
		z-index: 10;
	}

	.thumbnail {
		position: relative;
		aspect-ratio: 16 / 9;
		overflow: hidden;
		background: var(--color-surface-hover);
	}

	.thumbnail img {
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
		background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-hover) 100%);
	}

	.placeholder-icon {
		font-size: 2rem;
		opacity: 0.5;
	}

	.duration {
		position: absolute;
		bottom: 8px;
		right: 8px;
		padding: 0.125rem 0.5rem;
		background: rgba(0, 0, 0, 0.85);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		font-weight: 500;
		color: white;
	}

	.progress-bar {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 4px;
		background: rgba(255, 255, 255, 0.3);
	}

	.progress-fill {
		height: 100%;
		background: var(--color-primary);
		transition: width 0.3s ease;
	}

	.info {
		padding: var(--spacing-sm);
	}

	.title {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text);
		margin-bottom: var(--spacing-xs);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		line-height: 1.3;
	}

	.meta {
		display: flex;
		gap: var(--spacing-sm);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.library {
		color: var(--color-primary);
	}

	@media (max-width: 768px) {
		.content-card {
			width: 200px;
		}

		.content-card:hover {
			transform: none;
			box-shadow: none;
		}
	}
</style>
