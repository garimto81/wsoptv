<script lang="ts">
	import { page } from '$app/stores';
	import { Button } from '$lib/components/ui';

	const status = $derived($page.status);
	const message = $derived($page.error?.message || '페이지를 찾을 수 없습니다');

	const errorMessages: Record<number, string> = {
		400: '잘못된 요청입니다',
		401: '로그인이 필요합니다',
		403: '접근 권한이 없습니다',
		404: '페이지를 찾을 수 없습니다',
		500: '서버 오류가 발생했습니다'
	};

	const displayMessage = $derived(errorMessages[status] || message);
</script>

<svelte:head>
	<title>오류 {status} - WSOPTV</title>
</svelte:head>

<div class="error-page">
	<div class="error-content">
		<div class="error-code">{status}</div>
		<h1>{displayMessage}</h1>
		<p class="error-description">
			{#if status === 404}
				요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.
			{:else if status === 401}
				이 페이지를 보려면 로그인이 필요합니다.
			{:else if status === 403}
				이 페이지에 접근할 권한이 없습니다.
			{:else}
				일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.
			{/if}
		</p>

		<div class="error-actions">
			<a href="/">
				<Button variant="primary">홈으로</Button>
			</a>
			<Button variant="secondary" onclick={() => history.back()}>
				뒤로 가기
			</Button>
		</div>
	</div>
</div>

<style>
	.error-page {
		min-height: calc(100vh - 200px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.error-content {
		text-align: center;
		max-width: 500px;
	}

	.error-code {
		font-size: 8rem;
		font-weight: 800;
		line-height: 1;
		color: var(--color-primary);
		margin-bottom: var(--spacing-md);
	}

	h1 {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: var(--spacing-md);
	}

	.error-description {
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-xl);
	}

	.error-actions {
		display: flex;
		justify-content: center;
		gap: var(--spacing-md);
	}

	@media (max-width: 480px) {
		.error-code {
			font-size: 5rem;
		}

		.error-actions {
			flex-direction: column;
		}
	}
</style>
