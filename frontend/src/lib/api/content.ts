/**
 * Content API Client
 *
 * 콘텐츠, 카탈로그, 시리즈, 핸드 API
 */

import { api } from './client';

// =============================================================================
// Types
// =============================================================================

export interface Catalog {
	id: number;
	name: string;
	slug: string;
	description?: string;
	thumbnailUrl?: string;
	seriesCount?: number;
}

export interface Series {
	id: number;
	title: string;
	catalogId: number;
	year?: number;
	description?: string;
	thumbnailUrl?: string;
	contentCount?: number;
}

export interface Content {
	id: number;
	title: string;
	description?: string;
	seriesId?: number;
	durationSec: number;
	thumbnailUrl?: string;
	viewCount: number;
	createdAt: string;
	series?: {
		id: number;
		title: string;
		catalogId: string;
	};
}

export interface ContentDetail extends Content {
	files: ContentFile[];
	hands: Hand[];
}

export interface ContentFile {
	id: number;
	contentId: number;
	path: string;
	format: string;
	resolution?: string;
	sizeMb?: number;
}

export interface Hand {
	id: number;
	contentId: number;
	handNumber: number;
	timestampSec: number;
	players: HandPlayer[];
	potSize?: number;
	winner?: string;
	description?: string;
}

export interface HandPlayer {
	id: number;
	handId: number;
	playerId: number;
	playerName: string;
	position?: string;
	cards?: string;
	action?: string;
}

export interface ContentListResponse {
	items: Content[];
	total: number;
	page: number;
	hasNext: boolean;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Get all catalogs
 */
export async function getCatalogs(): Promise<Catalog[]> {
	return api.get<Catalog[]>('/catalogs');
}

/**
 * Get catalog by ID
 */
export async function getCatalog(id: number): Promise<Catalog> {
	return api.get<Catalog>(`/catalogs/${id}`);
}

/**
 * Get series by catalog ID
 */
export async function getSeriesByCatalog(catalogId: number): Promise<Series[]> {
	return api.get<Series[]>(`/catalogs/${catalogId}/series`);
}

/**
 * Get series by ID
 */
export async function getSeries(id: number): Promise<Series> {
	return api.get<Series>(`/series/${id}`);
}

/**
 * Get contents with filters
 */
export async function getContents(options?: {
	seriesId?: number;
	catalogId?: number;
	page?: number;
	limit?: number;
	sort?: 'recent' | 'popular';
}): Promise<ContentListResponse> {
	const params = new URLSearchParams();
	if (options?.seriesId) params.set('series_id', options.seriesId.toString());
	if (options?.catalogId) params.set('catalog_id', options.catalogId.toString());
	if (options?.page) params.set('page', options.page.toString());
	if (options?.limit) params.set('limit', options.limit.toString());
	if (options?.sort) params.set('sort', options.sort);

	const query = params.toString();
	return api.get<ContentListResponse>(`/contents${query ? `?${query}` : ''}`);
}

/**
 * Get content by ID with details
 */
export async function getContent(id: number): Promise<ContentDetail> {
	return api.get<ContentDetail>(`/contents/${id}`);
}

/**
 * Get hands for a content
 */
export async function getHands(contentId: number): Promise<Hand[]> {
	return api.get<Hand[]>(`/contents/${contentId}/hands`);
}

// Export as namespace
export const contentApi = {
	getCatalogs,
	getCatalog,
	getSeriesByCatalog,
	getSeries,
	getContents,
	getContent,
	getHands
};

export default contentApi;
