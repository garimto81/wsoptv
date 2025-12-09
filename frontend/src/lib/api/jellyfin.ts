/**
 * Jellyfin API Client
 *
 * Jellyfin 통합 API와 통신
 */

import { api } from './client';

// =============================================================================
// Types
// =============================================================================

export interface JellyfinServerInfo {
	serverName: string;
	version: string;
	id: string;
}

export interface JellyfinLibrary {
	id: string;
	name: string;
	collectionType?: string;
}

export interface JellyfinContent {
	jellyfinId: string;
	title: string;
	description?: string;
	durationSec: number;
	thumbnailUrl?: string;
	streamUrl?: string;
	libraryName?: string;
	path?: string;
	year?: number;
	dateCreated?: string;
	mediaType: string;
	supportsDirectPlay: boolean;
	supportsHls: boolean;
}

export interface JellyfinContentList {
	items: JellyfinContent[];
	total: number;
	page: number;
	limit: number;
	hasNext: boolean;
}

export interface JellyfinStreamInfo {
	itemId: string;
	hlsUrl: string;
	directUrl: string;
	thumbnailUrl: string;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Get Jellyfin server info
 */
export async function getServerInfo(): Promise<JellyfinServerInfo> {
	return api.get<JellyfinServerInfo>('/jellyfin/server');
}

/**
 * Get all Jellyfin libraries
 */
export async function getLibraries(): Promise<JellyfinLibrary[]> {
	return api.get<JellyfinLibrary[]>('/jellyfin/libraries');
}

/**
 * Get Jellyfin contents with optional filters
 */
export async function getContents(options?: {
	library?: string;
	q?: string;
	page?: number;
	limit?: number;
}): Promise<JellyfinContentList> {
	const params = new URLSearchParams();

	if (options?.library) params.set('library', options.library);
	if (options?.q) params.set('q', options.q);
	if (options?.page) params.set('page', options.page.toString());
	if (options?.limit) params.set('limit', options.limit.toString());

	const query = params.toString();
	return api.get<JellyfinContentList>(`/jellyfin/contents${query ? `?${query}` : ''}`);
}

/**
 * Get single Jellyfin content
 */
export async function getContent(itemId: string): Promise<JellyfinContent> {
	return api.get<JellyfinContent>(`/jellyfin/contents/${itemId}`);
}

/**
 * Get stream URLs for a Jellyfin item
 */
export async function getStreamInfo(itemId: string): Promise<JellyfinStreamInfo> {
	return api.get<JellyfinStreamInfo>(`/jellyfin/stream/${itemId}`);
}

/**
 * Search Jellyfin contents
 */
export async function searchContents(
	query: string,
	limit: number = 20
): Promise<JellyfinContentList> {
	const params = new URLSearchParams();
	params.set('q', query);
	params.set('limit', limit.toString());
	return api.get<JellyfinContentList>(`/jellyfin/search?${params}`);
}

/**
 * Get thumbnail URL for a Jellyfin item
 */
export function getThumbnailUrl(
	itemId: string,
	options?: { width?: number; height?: number }
): string {
	const params = new URLSearchParams();
	if (options?.width) params.set('width', options.width.toString());
	if (options?.height) params.set('height', options.height.toString());
	const query = params.toString();
	return `/api/v1/jellyfin/thumbnail/${itemId}${query ? `?${query}` : ''}`;
}

// Export all as namespace
export const jellyfinApi = {
	getServerInfo,
	getLibraries,
	getContents,
	getContent,
	getStreamInfo,
	searchContents,
	getThumbnailUrl
};

export default jellyfinApi;
