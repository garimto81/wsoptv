/**
 * Search API Client
 *
 * MeiliSearch 통합 검색 API
 */

import { api } from './client';

// =============================================================================
// Types
// =============================================================================

export interface SearchResult {
	id: number;
	type: 'content' | 'player' | 'hand';
	title: string;
	description?: string;
	thumbnailUrl?: string;
	highlights?: Record<string, string[]>;
	score?: number;
}

export interface SearchResponse {
	items: SearchResult[];
	total: number;
	query: string;
	processingTimeMs: number;
	facets?: Record<string, Record<string, number>>;
}

export interface AutocompleteResult {
	value: string;
	type: 'content' | 'player' | 'suggestion';
	id?: number;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Search contents, players, and hands
 */
export async function search(
	query: string,
	options?: {
		type?: 'content' | 'player' | 'hand' | 'all';
		page?: number;
		limit?: number;
		filters?: Record<string, string | number>;
	}
): Promise<SearchResponse> {
	const params = new URLSearchParams();
	params.set('q', query);
	if (options?.type && options.type !== 'all') params.set('type', options.type);
	if (options?.page) params.set('page', options.page.toString());
	if (options?.limit) params.set('limit', options.limit.toString());

	// Add filters
	if (options?.filters) {
		Object.entries(options.filters).forEach(([key, value]) => {
			params.set(`filter_${key}`, value.toString());
		});
	}

	return api.get<SearchResponse>(`/search?${params}`);
}

/**
 * Get autocomplete suggestions
 */
export async function autocomplete(
	query: string,
	limit: number = 5
): Promise<AutocompleteResult[]> {
	const params = new URLSearchParams();
	params.set('q', query);
	params.set('limit', limit.toString());

	return api.get<AutocompleteResult[]>(`/search/autocomplete?${params}`);
}

/**
 * Get popular searches
 */
export async function getPopularSearches(limit: number = 10): Promise<string[]> {
	return api.get<string[]>(`/search/popular?limit=${limit}`);
}

/**
 * Get search facets (filters)
 */
export async function getFacets(): Promise<Record<string, string[]>> {
	return api.get<Record<string, string[]>>('/search/facets');
}

// Export as namespace
export const searchApi = {
	search,
	autocomplete,
	getPopularSearches,
	getFacets
};

export default searchApi;
