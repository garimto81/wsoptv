<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner, Button } from '$lib/components/ui';

	interface SearchResult {
		id: number;
		type: 'content' | 'player' | 'hand';
		title: string;
		description: string | null;
		thumbnailUrl: string | null;
		catalogId?: string;
		year?: number;
		grade?: string;
	}

	interface SearchResponse {
		results: SearchResult[];
		total: number;
		facets: {
			catalogs: { value: string; count: number }[];
			years: { value: number; count: number }[];
			grades: { value: string; count: number }[];
		};
	}

	let results = $state<SearchResult[]>([]);
	let total = $state(0);
	let facets = $state<SearchResponse['facets'] | null>(null);
	let isLoading = $state(false);
	let error = $state('');

	// Filters
	let query = $state('');
	let selectedCatalogs = $state<string[]>([]);
	let selectedYears = $state<number[]>([]);
	let selectedGrades = $state<string[]>([]);

	const urlQuery = $derived($page.url.searchParams.get('q') || '');

	onMount(() => {
		query = urlQuery;
		if (query) {
			search();
		}
	});

	async function search() {
		if (!query.trim()) return;

		isLoading = true;
		error = '';

		try {
			const params = new URLSearchParams();
			params.set('q', query);
			if (selectedCatalogs.length) params.set('catalogs', selectedCatalogs.join(','));
			if (selectedYears.length) params.set('years', selectedYears.join(','));
			if (selectedGrades.length) params.set('grades', selectedGrades.join(','));

			const response = await api.get<SearchResponse>(`/search?${params}`);
			results = response.results;
			total = response.total;
			facets = response.facets;

			// Update URL
			goto(`/search?q=${encodeURIComponent(query)}`, { replaceState: true });
		} catch (err: any) {
			error = err.message || '검색에 실패했습니다';
		} finally {
			isLoading = false;
		}
	}

	function handleSubmit(e: Event) {
		e.preventDefault();
		search();
	}

	function toggleFilter(type: 'catalog' | 'year' | 'grade', value: string | number) {
		if (type === 'catalog') {
			const v = value as string;
			if (selectedCatalogs.includes(v)) {
				selectedCatalogs = selectedCatalogs.filter((c) => c !== v);
			} else {
				selectedCatalogs = [...selectedCatalogs, v];
			}
		} else if (type === 'year') {
			const v = value as number;
			if (selectedYears.includes(v)) {
				selectedYears = selectedYears.filter((y) => y !== v);
			} else {
				selectedYears = [...selectedYears, v];
			}
		} else if (type === 'grade') {
			const v = value as string;
			if (selectedGrades.includes(v)) {
				selectedGrades = selectedGrades.filter((g) => g !== v);
			} else {
				selectedGrades = [...selectedGrades, v];
			}
		}
		search();
	}

	function clearFilters() {
		selectedCatalogs = [];
		selectedYears = [];
		selectedGrades = [];
		search();
	}

	function getResultUrl(result: SearchResult): string {
		if (result.type === 'content') return `/watch/${result.id}`;
		if (result.type === 'player') return `/player/${result.id}`;
		return `/watch/${result.id}`;
	}

	const gradeColors: Record<string, string> = {
		S: '#f5c518',
		A: '#46d369',
		B: '#4db8ff',
		C: '#888'
	};
</script>

<svelte:head>
	<title>{query ? `"${query}" 검색 결과` : '검색'} - WSOPTV</title>
</svelte:head>

<div class="search-page container">
	<header class="search-header">
		<h1>검색</h1>
		<form class="search-form" onsubmit={handleSubmit}>
			<input
				type="search"
				class="search-input"
				placeholder="콘텐츠, 플레이어, 핸드 검색..."
				bind:value={query}
			/>
			<Button type="submit" variant="primary">검색</Button>
		</form>
	</header>

	<div class="search-content">
		{#if facets && (facets.catalogs.length || facets.years.length || facets.grades.length)}
			<aside class="filters">
				<div class="filter-header">
					<h3>필터</h3>
					{#if selectedCatalogs.length || selectedYears.length || selectedGrades.length}
						<button class="clear-btn" onclick={clearFilters}>초기화</button>
					{/if}
				</div>

				{#if facets.catalogs.length}
					<div class="filter-group">
						<h4>카탈로그</h4>
						{#each facets.catalogs as cat}
							<label class="filter-item">
								<input
									type="checkbox"
									checked={selectedCatalogs.includes(cat.value)}
									onchange={() => toggleFilter('catalog', cat.value)}
								/>
								<span>{cat.value.toUpperCase()}</span>
								<span class="count">({cat.count})</span>
							</label>
						{/each}
					</div>
				{/if}

				{#if facets.years.length}
					<div class="filter-group">
						<h4>연도</h4>
						{#each facets.years as year}
							<label class="filter-item">
								<input
									type="checkbox"
									checked={selectedYears.includes(year.value)}
									onchange={() => toggleFilter('year', year.value)}
								/>
								<span>{year.value}</span>
								<span class="count">({year.count})</span>
							</label>
						{/each}
					</div>
				{/if}

				{#if facets.grades.length}
					<div class="filter-group">
						<h4>등급</h4>
						{#each facets.grades as grade}
							<label class="filter-item">
								<input
									type="checkbox"
									checked={selectedGrades.includes(grade.value)}
									onchange={() => toggleFilter('grade', grade.value)}
								/>
								<span class="grade-badge" style="color: {gradeColors[grade.value]}">{grade.value}</span>
								<span class="count">({grade.count})</span>
							</label>
						{/each}
					</div>
				{/if}
			</aside>
		{/if}

		<div class="results">
			{#if isLoading}
				<div class="loading">
					<Spinner size="lg" />
				</div>
			{:else if error}
				<div class="error">{error}</div>
			{:else if !query}
				<div class="empty">
					<p>검색어를 입력하세요</p>
				</div>
			{:else if results.length === 0}
				<div class="empty">
					<p>"{query}"에 대한 검색 결과가 없습니다</p>
				</div>
			{:else}
				<div class="results-header">
					<p>{total.toLocaleString()}개 결과</p>
				</div>

				<div class="results-grid">
					{#each results as result}
						<a href={getResultUrl(result)} class="result-card">
							<Card variant="clickable" padding="none">
								<div class="result-image">
									{#if result.thumbnailUrl}
										<img src={result.thumbnailUrl} alt={result.title} />
									{:else}
										<div class="result-placeholder">
											{result.type === 'player' ? '👤' : '🎬'}
										</div>
									{/if}
									{#if result.grade}
										<span class="grade" style="background: {gradeColors[result.grade]}">{result.grade}</span>
									{/if}
								</div>
								<div class="result-info">
									<span class="type-badge">{result.type}</span>
									<h3>{result.title}</h3>
									{#if result.description}
										<p class="description">{result.description}</p>
									{/if}
									<div class="meta">
										{#if result.catalogId}
											<span>{result.catalogId.toUpperCase()}</span>
										{/if}
										{#if result.year}
											<span>{result.year}</span>
										{/if}
									</div>
								</div>
							</Card>
						</a>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.search-page {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.search-header {
		margin-bottom: var(--spacing-xl);
	}

	.search-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-md);
	}

	.search-form {
		display: flex;
		gap: var(--spacing-sm);
		max-width: 600px;
	}

	.search-input {
		flex: 1;
		padding: 0.75rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		font-size: 1rem;
	}

	.search-input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.search-content {
		display: grid;
		grid-template-columns: 220px 1fr;
		gap: var(--spacing-xl);
	}

	.filters {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--spacing-md);
		align-self: start;
		position: sticky;
		top: 80px;
	}

	.filter-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-md);
	}

	.filter-header h3 {
		font-size: 1rem;
		font-weight: 600;
	}

	.clear-btn {
		background: none;
		border: none;
		color: var(--color-primary);
		font-size: 0.75rem;
		cursor: pointer;
	}

	.filter-group {
		margin-bottom: var(--spacing-md);
	}

	.filter-group h4 {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-sm);
	}

	.filter-item {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		padding: var(--spacing-xs) 0;
		cursor: pointer;
		font-size: 0.875rem;
	}

	.filter-item input {
		accent-color: var(--color-primary);
	}

	.filter-item .count {
		color: var(--color-text-muted);
		font-size: 0.75rem;
		margin-left: auto;
	}

	.grade-badge {
		font-weight: 700;
	}

	.results {
		min-height: 400px;
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

	.empty {
		text-align: center;
		padding: var(--spacing-xl);
		color: var(--color-text-muted);
	}

	.results-header {
		margin-bottom: var(--spacing-md);
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.results-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
		gap: var(--spacing-md);
	}

	.result-card {
		text-decoration: none;
	}

	.result-image {
		position: relative;
		aspect-ratio: 16 / 9;
		overflow: hidden;
	}

	.result-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.result-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-surface-hover);
		font-size: 2rem;
	}

	.grade {
		position: absolute;
		top: 8px;
		right: 8px;
		padding: 0.125rem 0.375rem;
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		font-weight: 700;
		color: black;
	}

	.result-info {
		padding: var(--spacing-sm);
	}

	.type-badge {
		display: inline-block;
		padding: 0.125rem 0.375rem;
		background: var(--color-surface-hover);
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		text-transform: uppercase;
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-xs);
	}

	.result-info h3 {
		font-size: 0.875rem;
		font-weight: 500;
		margin-bottom: var(--spacing-xs);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.result-info .description {
		font-size: 0.75rem;
		color: var(--color-text-muted);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		margin-bottom: var(--spacing-xs);
	}

	.meta {
		display: flex;
		gap: var(--spacing-sm);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	@media (max-width: 768px) {
		.search-content {
			grid-template-columns: 1fr;
		}

		.filters {
			position: static;
			order: -1;
		}
	}
</style>
