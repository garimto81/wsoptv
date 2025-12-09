/**
 * Root Layout Load
 *
 * 인증 상태를 로드하여 하위 라우트에 전달
 */

import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ fetch }) => {
	try {
		const response = await fetch('/api/v1/auth/me', {
			credentials: 'include'
		});

		if (response.ok) {
			const data = await response.json();
			return { user: data.data };
		}
	} catch {
		// 인증 실패 (미로그인 상태)
	}

	return { user: null };
};
