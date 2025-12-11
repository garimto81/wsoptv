<script lang="ts">
	import type { RowItem } from '$lib/types/row';
	import { ContentCard } from '$lib/components/home';

	interface Props {
		items: RowItem[];
	}

	let { items }: Props = $props();
</script>

{#if items.length === 0}
	<div class="empty-grid">
		<span class="empty-icon">🔍</span>
		<p>No content found</p>
		<p class="hint">Try adjusting your filters</p>
	</div>
{:else}
	<div class="content-grid">
		{#each items as item (item.id)}
			<ContentCard {item} />
		{/each}
	</div>
{/if}

<style>
	.content-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: var(--spacing-lg);
	}

	.empty-grid {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-muted);
	}

	.empty-icon {
		font-size: 3rem;
		display: block;
		margin-bottom: var(--spacing-md);
		opacity: 0.5;
	}

	.empty-grid p {
		margin-bottom: var(--spacing-xs);
	}

	.hint {
		font-size: 0.875rem;
		opacity: 0.7;
	}

	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
			gap: var(--spacing-md);
		}

		/* Override ContentCard hover on mobile */
		:global(.content-grid .content-card) {
			width: 100%;
		}
	}
</style>
