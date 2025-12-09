<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button, Input, Card } from '$lib/components/ui';
	import { authStore } from '$lib/stores';

	let username = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');
	let isLoading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		// Validation
		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 4) {
			error = 'Password must be at least 4 characters';
			return;
		}

		isLoading = true;

		try {
			await authStore.register(username, password, confirmPassword);
			goto('/register/pending');
		} catch (err: any) {
			error = err.message || 'Registration failed. Please try again.';
		} finally {
			isLoading = false;
		}
	}
</script>

<svelte:head>
	<title>Register - WSOPTV</title>
</svelte:head>

<div class="register-page">
	<Card padding="lg">
		<div class="register-header">
			<h1>Create Account</h1>
			<p>Join WSOPTV and enjoy poker broadcasts</p>
		</div>

		<form class="register-form" onsubmit={handleSubmit}>
			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<Input
				label="Username"
				type="text"
				placeholder="Letters and numbers only"
				bind:value={username}
				required
				autocomplete="username"
			/>

			<Input
				label="Password"
				type="password"
				placeholder="At least 4 characters"
				bind:value={password}
				required
				autocomplete="new-password"
			/>

			<Input
				label="Confirm Password"
				type="password"
				placeholder="Re-enter password"
				bind:value={confirmPassword}
				required
				autocomplete="new-password"
			/>

			<div class="notice">
				<p>Admin approval is required after registration.</p>
			</div>

			<Button type="submit" variant="primary" loading={isLoading}>
				Create Account
			</Button>
		</form>

		<div class="register-footer">
			<p>Already have an account? <a href="/login">Sign In</a></p>
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
