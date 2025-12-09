/**
 * Jellyfin Watch Page Load
 *
 * 인증 가드: 미인증 사용자는 로그인 페이지로 리다이렉트
 */

import { redirect, error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, parent }) => {
	const { user } = await parent();

	// 미인증 사용자 → 로그인 페이지로 리다이렉트
	if (!user) {
		throw redirect(302, `/login?redirect=/jellyfin/watch/${params.id}`);
	}

	// 승인되지 않은 사용자
	if (user.status !== 'approved') {
		throw redirect(302, '/register/pending');
	}

	// itemId 유효성 검사
	if (!params.id) {
		throw error(400, 'Item ID is required');
	}

	return {
		user,
		itemId: params.id
	};
};
