/**
 * SvelteKit Server Hooks
 *
 * API 요청을 백엔드로 프록시
 */

import type { Handle } from '@sveltejs/kit';

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8001';

export const handle: Handle = async ({ event, resolve }) => {
	// Proxy /api requests to backend
	if (event.url.pathname.startsWith('/api')) {
		const targetUrl = `${BACKEND_URL}${event.url.pathname}${event.url.search}`;

		try {
			const response = await fetch(targetUrl, {
				method: event.request.method,
				headers: event.request.headers,
				body: event.request.method !== 'GET' && event.request.method !== 'HEAD'
					? await event.request.text()
					: undefined,
			});

			// Forward response with all headers
			const responseHeaders = new Headers(response.headers);

			// Remove hop-by-hop headers
			responseHeaders.delete('transfer-encoding');
			responseHeaders.delete('connection');

			return new Response(response.body, {
				status: response.status,
				statusText: response.statusText,
				headers: responseHeaders,
			});
		} catch (error) {
			console.error('API proxy error:', error);
			return new Response(
				JSON.stringify({ error: { code: 'PROXY_ERROR', message: 'Failed to connect to backend' } }),
				{
					status: 502,
					headers: { 'Content-Type': 'application/json' },
				}
			);
		}
	}

	return resolve(event);
};
