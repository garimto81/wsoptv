<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Input, Card } from '$lib/components/ui';
	import { authStore } from '$lib/stores';

	let username = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let displayName = $state('');
	let error = $state('');
	let isLoading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		// Validation
		if (password !== confirmPassword) {
			error = '비밀번호가 일치하지 않습니다';
			return;
		}

		if (password.length < 8) {
			error = '비밀번호는 8자 이상이어야 합니다';
			return;
		}

		isLoading = true;

		try {
			await authStore.register(username, password, displayName || undefined);
			goto('/register/pending');
		} catch (err: any) {
			error = err.message || '회원가입에 실패했습니다';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>회원가입 - WSOPTV</title>
</svelte:head>

<div class="register-page">
	<Card padding="lg">
		<div class="register-header">
			<h1>회원가입</h1>
			<p>WSOPTV에 가입하고 포커 방송을 즐기세요</p>
		</div>

		<form class="register-form" onsubmit={handleSubmit}>
			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<Input
				label="사용자명"
				type="text"
				placeholder="사용자명 (영문, 숫자)"
				bind:value={username}
				required
				autocomplete="username"
			/>

			<Input
				label="표시 이름 (선택)"
				type="text"
				placeholder="표시될 이름"
				bind:value={displayName}
				autocomplete="name"
			/>

			<Input
				label="비밀번호"
				type="password"
				placeholder="8자 이상"
				bind:value={password}
				required
				autocomplete="new-password"
			/>

			<Input
				label="비밀번호 확인"
				type="password"
				placeholder="비밀번호 재입력"
				bind:value={confirmPassword}
				required
				autocomplete="new-password"
			/>

			<div class="notice">
				<p>⚠️ 회원가입 후 관리자 승인이 필요합니다.</p>
			</div>

			<Button type="submit" variant="primary" loading={isLoading}>
				회원가입
			</Button>
		</form>

		<div class="register-footer">
			<p>이미 계정이 있으신가요? <a href="/login">로그인</a></p>
		</div>
	</Card>
</div>

<style>
	.register-page {
		min-height: calc(100vh - 200px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.register-page :global(.card) {
		width: 100%;
		max-width: 400px;
	}

	.register-header {
		text-align: center;
		margin-bottom: var(--spacing-lg);
	}

	.register-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.register-header p {
		color: var(--color-text-muted);
	}

	.register-form {
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

	.notice {
		padding: var(--spacing-sm);
		background: rgba(245, 197, 24, 0.1);
		border: 1px solid var(--color-warning);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		color: var(--color-warning);
	}

	.register-footer {
		margin-top: var(--spacing-lg);
		text-align: center;
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.register-footer a {
		color: var(--color-primary);
		text-decoration: none;
	}

	.register-footer a:hover {
		text-decoration: underline;
	}
</style>
