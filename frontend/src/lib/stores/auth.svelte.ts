/**
 * Auth Store
 *
 * 인증 상태 관리 (Svelte 5 runes)
 */

import { api } from '$lib/api';

export interface User {
	id: number;
	username: string;
	displayName: string | null;
	avatarUrl: string | null;
	role: 'user' | 'admin';
	status: 'pending' | 'approved' | 'rejected' | 'suspended';
}

interface AuthState {
	user: User | null;
	isLoading: boolean;
	isAuthenticated: boolean;
}

// Svelte 5 state
let state = $state<AuthState>({
	user: null,
	isLoading: true,
	isAuthenticated: false
});

export const authStore = {
	get user() {
		return state.user;
	},
	get isLoading() {
		return state.isLoading;
	},
	get isAuthenticated() {
		return state.isAuthenticated;
	},
	get isAdmin() {
		return state.user?.role === 'admin';
	},
	get isApproved() {
		return state.user?.status === 'approved';
	},

	/**
	 * Set user from server-side load data (from +layout.ts)
	 * This avoids duplicate API calls since +layout.ts already fetched auth
	 */
	setUser(user: User | null) {
		state.user = user;
		state.isAuthenticated = user !== null;
		state.isLoading = false;
	},

	async init() {
		// Skip if already initialized (e.g., from setUser)
		if (!state.isLoading) return;

		try {
			state.isLoading = true;
			const user = await api.get<User>('/auth/me');
			state.user = user;
			state.isAuthenticated = true;
		} catch {
			state.user = null;
			state.isAuthenticated = false;
		} finally {
			state.isLoading = false;
		}
	},

	async login(username: string, password: string) {
		const user = await api.post<User>('/auth/login', { username, password });
		state.user = user;
		state.isAuthenticated = true;
		return user;
	},

	async register(username: string, password: string, passwordConfirm: string) {
		// 회원가입은 pending 상태로 생성되므로 인증 상태를 설정하지 않음
		// 로그인은 관리자 승인 후에만 가능
		const response = await api.post<{ user: User; message: string }>('/auth/register', {
			username,
			password,
			passwordConfirm
		});
		return response;
	},

	async logout() {
		try {
			await api.post('/auth/logout');
		} finally {
			state.user = null;
			state.isAuthenticated = false;
		}
	},

	async refresh() {
		try {
			const user = await api.post<User>('/auth/refresh');
			state.user = user;
			state.isAuthenticated = true;
			return user;
		} catch {
			state.user = null;
			state.isAuthenticated = false;
			throw new Error('Session expired');
		}
	}
};
