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

	async init() {
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
		const user = await api.post<User>('/auth/register', {
			username,
			password,
			passwordConfirm
		});
		state.user = user;
		state.isAuthenticated = true;
		return user;
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
