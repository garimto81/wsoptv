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
