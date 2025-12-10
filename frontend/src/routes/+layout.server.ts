/**
 * Root Layout Server Load
 *
 * 서버에서만 인증 상태를 로드하여 하위 라우트에 전달
 * 클라이언트 네비게이션 시 중복 API 호출 방지
 */

import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
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
