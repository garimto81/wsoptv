/**
 * Row Types
 *
 * Netflix-style 동적 카탈로그 Row 시스템 타입 정의
 */

export type RowType =
	| 'recently_added'
	| 'library'
	| 'continue_watching'
	| 'trending'
	| 'top_rated'
	| 'tag';

export interface RowItem {
	id: string;
	title: string;
	thumbnailUrl: string | null;
	durationSec: number;
	libraryName: string | null;
	progress?: number;
	year: number | null;
	dateCreated: string | null;
}

export interface RowFilter {
	libraryId?: string;
	sortBy?: string;
	sortOrder?: string;
	limit?: number;
}

export interface RowData {
	id: string;
	type: RowType;
	title: string;
	items: RowItem[];
	filter?: RowFilter;
	viewAllUrl: string;
	totalCount: number;
}

export interface HomeRowsResponse {
	rows: RowData[];
	cached: boolean;
	cacheExpiresAt: string | null;
}

export interface BrowseParams {
	library?: string;
	sort?: string;
	order?: string;
	page?: number;
	limit?: number;
	q?: string;
}

export interface BrowseResponse {
	items: RowItem[];
	total: number;
	page: number;
	limit: number;
	hasNext: boolean;
}
