/**
 * Stream API Client
 *
 * HLS 스트리밍 및 재생 관련 API
 */

import { api } from './client';

// =============================================================================
// Types
// =============================================================================

export interface StreamInfo {
	contentId: number;
	hlsUrl: string;
	thumbnailUrl?: string;
	duration: number;
	qualities: StreamQuality[];
}

export interface StreamQuality {
	label: string;
	resolution: string;
	bitrate: number;
	url: string;
}

export interface WatchProgress {
	contentId: number;
	userId: number;
	progressSec: number;
	lastWatched: string;
	completed: boolean;
}

export interface ViewEvent {
	contentId: number;
	eventType: 'start' | 'progress' | 'complete' | 'seek';
	timestampSec: number;
	metadata?: Record<string, unknown>;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Get HLS playlist URL for content
 */
export function getPlaylistUrl(contentId: number): string {
	return `/api/v1/stream/${contentId}/playlist.m3u8`;
}

/**
 * Get stream info for content
 */
export async function getStreamInfo(contentId: number): Promise<StreamInfo> {
	return api.get<StreamInfo>(`/stream/${contentId}/info`);
}

/**
 * Get watch progress for content
 */
export async function getWatchProgress(contentId: number): Promise<WatchProgress | null> {
	try {
		return await api.get<WatchProgress>(`/stream/${contentId}/progress`);
	} catch {
		return null;
	}
}

/**
 * Update watch progress
 */
export async function updateWatchProgress(
	contentId: number,
	progressSec: number
): Promise<WatchProgress> {
	return api.post<WatchProgress>(`/stream/${contentId}/progress`, {
		progress_sec: progressSec
	});
}

/**
 * Log view event (analytics)
 */
export async function logViewEvent(event: ViewEvent): Promise<void> {
	await api.post('/stream/events', event);
}

/**
 * Get recently watched contents
 */
export async function getWatchHistory(limit: number = 20): Promise<WatchProgress[]> {
	return api.get<WatchProgress[]>(`/stream/history?limit=${limit}`);
}

/**
 * Get continue watching list
 */
export async function getContinueWatching(limit: number = 10): Promise<WatchProgress[]> {
	return api.get<WatchProgress[]>(`/stream/continue?limit=${limit}`);
}

// Export as namespace
export const streamApi = {
	getPlaylistUrl,
	getStreamInfo,
	getWatchProgress,
	updateWatchProgress,
	logViewEvent,
	getWatchHistory,
	getContinueWatching
};

export default streamApi;
