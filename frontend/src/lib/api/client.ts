/**
 * WSOPTV API Client
 *
 * Backend API와 통신하는 클라이언트
 */

const API_BASE = '/api/v1';

interface ApiResponse<T> {
	data: T;
	message?: string;
}

interface ApiError {
	code: string;
	message: string;
	detail?: unknown;
}

class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE) {
		this.baseUrl = baseUrl;
	}

	async fetch<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<ApiResponse<T>> {
		const url = `${this.baseUrl}${endpoint}`;

		const response = await fetch(url, {
			...options,
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			}
		});

		if (!response.ok) {
			// 401 Unauthorized - 로그인 페이지로 리다이렉트 (브라우저 환경에서만)
			if (response.status === 401 && typeof window !== 'undefined') {
				const currentPath = window.location.pathname;
				// 이미 로그인 페이지가 아닌 경우에만 리다이렉트
				if (!currentPath.startsWith('/login') && !currentPath.startsWith('/register')) {
					window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
					// 리다이렉트 중 추가 처리 방지
					throw { code: 'REDIRECT', message: 'Redirecting to login...' };
				}
			}

			const error: ApiError = await response.json().catch(() => ({
				code: 'UNKNOWN_ERROR',
				message: 'An unknown error occurred'
			}));
			throw error;
		}

		return response.json();
	}

	async get<T>(endpoint: string): Promise<T> {
		const response = await this.fetch<T>(endpoint);
		return response.data;
	}

	async post<T>(endpoint: string, body?: unknown): Promise<T> {
		const response = await this.fetch<T>(endpoint, {
			method: 'POST',
			body: body ? JSON.stringify(body) : undefined
		});
		return response.data;
	}

	async put<T>(endpoint: string, body?: unknown): Promise<T> {
		const response = await this.fetch<T>(endpoint, {
			method: 'PUT',
			body: body ? JSON.stringify(body) : undefined
		});
		return response.data;
	}

	async delete<T>(endpoint: string): Promise<T> {
		const response = await this.fetch<T>(endpoint, {
			method: 'DELETE'
		});
		return response.data;
	}
}

export const api = new ApiClient();
export default api;
