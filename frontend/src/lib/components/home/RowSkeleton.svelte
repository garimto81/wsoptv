<script lang="ts">
	interface Props {
		count?: number;
	}

	let { count = 6 }: Props = $props();
</script>

<section class="skeleton-row">
	<div class="skeleton-header">
		<div class="skeleton-title"></div>
		<div class="skeleton-link"></div>
	</div>

	<div class="skeleton-items">
		{#each Array(count) as _item, i}
			<div class="skeleton-card" style="animation-delay: {i * 0.1}s">
				<div class="skeleton-thumbnail"></div>
				<div class="skeleton-info">
					<div class="skeleton-text title"></div>
					<div class="skeleton-text meta"></div>
				</div>
			</div>
		{/each}
	</div>
</section>

<style>
	.skeleton-row {
		margin-bottom: var(--spacing-xl);
	}

	.skeleton-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-md);
		padding: 0 var(--spacing-md);
	}

	.skeleton-title {
		width: 200px;
		height: 24px;
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
		animation: pulse 1.5s ease-in-out infinite;
	}

	.skeleton-link {
		width: 80px;
		height: 16px;
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
		animation: pulse 1.5s ease-in-out infinite;
	}

	.skeleton-items {
		display: flex;
		gap: var(--spacing-md);
		overflow: hidden;
		padding: var(--spacing-sm) var(--spacing-md);
	}

	.skeleton-card {
		flex: 0 0 auto;
		width: 280px;
		background: var(--color-surface);
		border-radius: var(--radius-md);
		overflow: hidden;
		animation: pulse 1.5s ease-in-out infinite;
	}

	.skeleton-thumbnail {
		aspect-ratio: 16 / 9;
		background: var(--color-surface-hover);
	}

	.skeleton-info {
		padding: var(--spacing-sm);
	}

	.skeleton-text {
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
	}

	.skeleton-text.title {
		width: 80%;
		height: 16px;
		margin-bottom: var(--spacing-xs);
	}

	.skeleton-text.meta {
		width: 50%;
		height: 12px;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	@media (max-width: 768px) {
		.skeleton-card {
			width: 200px;
		}
	}
</style>
