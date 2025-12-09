<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Input, Card } from '$lib/components/ui';
	import { authStore } from '$lib/stores';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let isLoading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		isLoading = true;

		try {
			await authStore.login(username, password);
			goto('/');
		} catch (err: any) {
			error = err.message || '로그인에 실패했습니다';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>로그인 - WSOPTV</title>
</svelte:head>

<div class="login-page">
	<Card padding="lg">
		<div class="login-header">
			<h1>로그인</h1>
			<p>WSOPTV에 오신 것을 환영합니다</p>
		</div>

		<form class="login-form" onsubmit={handleSubmit}>
			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<Input
				label="사용자명"
				type="text"
				placeholder="사용자명을 입력하세요"
				bind:value={username}
				required
				autocomplete="username"
			/>

			<Input
				label="비밀번호"
				type="password"
				placeholder="비밀번호를 입력하세요"
				bind:value={password}
				required
				autocomplete="current-password"
			/>

			<Button type="submit" variant="primary" loading={isLoading}>
				로그인
			</Button>
		</form>

		<div class="login-footer">
			<p>계정이 없으신가요? <a href="/register">회원가입</a></p>
		</div>
	</Card>
</div>

<style>
	.login-page {
		min-height: calc(100vh - 200px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.login-page :global(.card) {
		width: 100%;
		max-width: 400px;
	}

	.login-header {
		text-align: center;
		margin-bottom: var(--spacing-lg);
	}

	.login-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.login-header p {
		color: var(--color-text-muted);
	}

	.login-form {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	.error-message {
		padding: var(--spacing-sm);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
		font-size: 0.875rem;
	}

	.login-footer {
		margin-top: var(--spacing-lg);
		text-align: center;
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.login-footer a {
		color: var(--color-primary);
		text-decoration: none;
	}

	.login-footer a:hover {
		text-decoration: underline;
	}
</style>
