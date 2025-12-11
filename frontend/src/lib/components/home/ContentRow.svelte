<script lang="ts">
	import type { RowData } from '$lib/types/row';
	import ContentCard from './ContentCard.svelte';

	interface Props {
		row: RowData;
	}

	let { row }: Props = $props();

	let scrollContainer = $state<HTMLDivElement | null>(null);
	let canScrollLeft = $state(false);
	let canScrollRight = $state(true);

	function updateScrollButtons() {
		if (!scrollContainer) return;
		canScrollLeft = scrollContainer.scrollLeft > 0;
		canScrollRight =
			scrollContainer.scrollLeft < scrollContainer.scrollWidth - scrollContainer.clientWidth - 10;
	}

	function scrollBy(direction: 'left' | 'right') {
		if (!scrollContainer) return;
		const scrollAmount = scrollContainer.clientWidth * 0.8;
		scrollContainer.scrollBy({
			left: direction === 'left' ? -scrollAmount : scrollAmount,
			behavior: 'smooth'
		});
	}

	$effect(() => {
		if (scrollContainer) {
			updateScrollButtons();
		}
	});
</script>

<section class="content-row">
	<header class="row-header">
		<h2 class="row-title">{row.title}</h2>
		<a href={row.viewAllUrl} class="view-all">View All ({row.totalCount})</a>
	</header>

	<div class="row-container">
		{#if canScrollLeft}
			<button class="scroll-btn scroll-left" onclick={() => scrollBy('left')} aria-label="Scroll left">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<polyline points="15 18 9 12 15 6"></polyline>
				</svg>
			</button>
		{/if}

		<div
			class="items-container"
			bind:this={scrollContainer}
			onscroll={updateScrollButtons}
		>
			{#each row.items as item (item.id)}
				<ContentCard {item} />
			{/each}
		</div>

		{#if canScrollRight}
			<button class="scroll-btn scroll-right" onclick={() => scrollBy('right')} aria-label="Scroll right">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<polyline points="9 18 15 12 9 6"></polyline>
				</svg>
			</button>
		{/if}
	</div>
</section>

<style>
	.content-row {
		margin-bottom: var(--spacing-xl);
	}

	.row-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-md);
		padding: 0 var(--spacing-md);
	}

	.row-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.view-all {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		text-decoration: none;
		transition: color 0.2s ease;
	}

	.view-all:hover {
		color: var(--color-primary);
	}

	.row-container {
		position: relative;
	}

	.items-container {
		display: flex;
		gap: var(--spacing-md);
		overflow-x: auto;
		scroll-snap-type: x mandatory;
		scroll-behavior: smooth;
		padding: var(--spacing-sm) var(--spacing-md);
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.items-container::-webkit-scrollbar {
		display: none;
	}

	.scroll-btn {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		z-index: 20;
		width: 48px;
		height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(0, 0, 0, 0.8);
		border: none;
		border-radius: 50%;
		color: white;
		cursor: pointer;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.row-container:hover .scroll-btn {
		opacity: 1;
	}

	.scroll-btn:hover {
		background: rgba(0, 0, 0, 0.95);
	}

	.scroll-left {
		left: 8px;
	}

	.scroll-right {
		right: 8px;
	}

	@media (max-width: 768px) {
		.scroll-btn {
			display: none;
		}

		.row-header {
			padding: 0 var(--spacing-sm);
		}

		.items-container {
			padding: var(--spacing-sm);
		}
	}
</style>
