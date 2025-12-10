/**
 * Home API
 *
 * Netflix-style 동적 카탈로그 Row API 클라이언트
 */

import type { HomeRowsResponse, BrowseParams, BrowseResponse } from '$lib/types/row';

const API_BASE = '/api/v1';

class HomeApiError extends Error {
	constructor(
		message: string,
		public code: string,
		public status: number
	) {
		super(message);
		this.name = 'HomeApiError';
	}
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		const error = await response.json().catch(() => ({ message: 'Unknown error' }));
		throw new HomeApiError(
			error.detail?.message || error.message || 'Request failed',
			error.detail?.code || 'UNKNOWN',
			response.status
		);
	}
	return response.json();
}

/**
 * 홈페이지 Row 목록 조회
 */
export async function fetchHomeRows(limit: number = 20): Promise<HomeRowsResponse> {
	const response = await fetch(`${API_BASE}/home?limit=${limit}`, {
		credentials: 'include'
	});
	return handleResponse<HomeRowsResponse>(response);
}

/**
 * 특정 라이브러리 Row 조회
 */
export async function fetchLibraryRow(libraryId: string, limit: number = 20) {
	const response = await fetch(`${API_BASE}/home/library/${libraryId}?limit=${limit}`, {
		credentials: 'include'
	});
	return handleResponse(response);
}

/**
 * Browse 콘텐츠 조회 (필터/정렬/페이지네이션)
 */
export async function fetchBrowseContents(params: BrowseParams = {}): Promise<BrowseResponse> {
	const searchParams = new URLSearchParams();

	if (params.library) searchParams.set('library', params.library);
	if (params.sort) searchParams.set('sort', params.sort);
	if (params.order) searchParams.set('order', params.order);
	if (params.page) searchParams.set('page', params.page.toString());
	if (params.limit) searchParams.set('limit', params.limit.toString());
	if (params.q) searchParams.set('q', params.q);

	const response = await fetch(`${API_BASE}/home/browse?${searchParams}`, {
		credentials: 'include'
	});
	return handleResponse<BrowseResponse>(response);
}

export const homeApi = {
	fetchHomeRows,
	fetchLibraryRow,
	fetchBrowseContents
};
