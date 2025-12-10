<script lang="ts">
	import type { JellyfinLibrary } from '$lib/api/jellyfin';

	interface Props {
		libraries: JellyfinLibrary[];
		selectedLibrary: string | undefined;
		sortBy: string;
		sortOrder: string;
		onFilterChange: () => void;
	}

	let { libraries, selectedLibrary = $bindable(), sortBy = $bindable(), sortOrder = $bindable(), onFilterChange }: Props = $props();

	const sortOptions = [
		{ value: 'DateCreated', label: 'Date Added' },
		{ value: 'SortName', label: 'Title' },
		{ value: 'PremiereDate', label: 'Release Date' },
		{ value: 'CommunityRating', label: 'Rating' }
	];

	function handleLibraryChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		selectedLibrary = target.value || undefined;
		onFilterChange();
	}

	function handleSortChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		sortBy = target.value;
		onFilterChange();
	}

	function handleOrderChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		sortOrder = target.value;
		onFilterChange();
	}
</script>

<div class="filter-bar">
	<div class="filter-group">
		<label for="library-select">Library</label>
		<select id="library-select" value={selectedLibrary || ''} onchange={handleLibraryChange}>
			<option value="">All Libraries</option>
			{#each libraries as library}
				<option value={library.id}>{library.name}</option>
			{/each}
		</select>
	</div>

	<div class="filter-group">
		<label for="sort-select">Sort By</label>
		<select id="sort-select" value={sortBy} onchange={handleSortChange}>
			{#each sortOptions as option}
				<option value={option.value}>{option.label}</option>
			{/each}
		</select>
	</div>

	<div class="filter-group">
		<label for="order-select">Order</label>
		<select id="order-select" value={sortOrder} onchange={handleOrderChange}>
			<option value="Descending">Newest First</option>
			<option value="Ascending">Oldest First</option>
		</select>
	</div>
</div>

<style>
	.filter-bar {
		display: flex;
		gap: var(--spacing-lg);
		padding: var(--spacing-md);
		background: var(--color-surface);
		border-radius: var(--radius-md);
		margin-bottom: var(--spacing-xl);
		flex-wrap: wrap;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.filter-group label {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.filter-group select {
		padding: 0.5rem 1rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		color: var(--color-text);
		font-size: 0.875rem;
		cursor: pointer;
		min-width: 150px;
	}

	.filter-group select:hover {
		border-color: var(--color-primary);
	}

	.filter-group select:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 2px rgba(229, 9, 20, 0.2);
	}

	@media (max-width: 768px) {
		.filter-bar {
			flex-direction: column;
		}

		.filter-group select {
			width: 100%;
		}
	}
</style>
