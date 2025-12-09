<script lang="ts">
	import { page } from '$app/stores';
	import { Button } from '$lib/components/ui';

	const status = $derived($page.status);
	const message = $derived($page.error?.message || 'Page not found');

	const errorMessages: Record<number, string> = {
		400: 'Bad Request',
		401: 'Authentication Required',
		403: 'Access Denied',
		404: 'Page Not Found',
		500: 'Server Error'
	};

	const displayMessage = $derived(errorMessages[status] || message);
</script>

<svelte:head>
	<title>Error {status} - WSOPTV</title>
</svelte:head>

<div class="error-page">
	<div class="error-content">
		<div class="error-code">{status}</div>
		<h1>{displayMessage}</h1>
		<p class="error-description">
			{#if status === 404}
				The page you requested does not exist or may have been moved.
			{:else if status === 401}
				Please sign in to view this page.
			{:else if status === 403}
				You do not have permission to access this page.
			{:else}
				A temporary error occurred. Please try again later.
			{/if}
		</p>

		<div class="error-actions">
			<a href="/">
				<Button variant="primary">Go to Home</Button>
			</a>
			<Button variant="secondary" onclick={() => history.back()}>
				Go Back
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
