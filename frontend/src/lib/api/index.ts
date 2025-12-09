export { api, default } from './client';
export { contentApi } from './content';
export { searchApi } from './search';
export { streamApi } from './stream';
export { jellyfinApi } from './jellyfin';

// Re-export types
export type {
	Catalog,
	Series,
	Content,
	ContentDetail,
	ContentFile,
	Hand,
	HandPlayer,
	ContentListResponse
} from './content';

export type {
	SearchResult,
	SearchResponse,
	AutocompleteResult
} from './search';

export type {
	StreamInfo,
	StreamQuality,
	WatchProgress,
	ViewEvent
} from './stream';

export type {
	JellyfinServerInfo,
	JellyfinLibrary,
	JellyfinContent,
	JellyfinContentList,
	JellyfinStreamInfo
} from './jellyfin';
