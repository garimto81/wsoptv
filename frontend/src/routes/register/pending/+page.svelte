<script lang="ts">
	import { Card, Button } from '$lib/components/ui';
</script>

<svelte:head>
	<title>Registration Pending - WSOPTV</title>
</svelte:head>

<div class="pending-page">
	<Card padding="lg">
		<div class="pending-content">
			<div class="icon">⏳</div>
			<h1>Registration Submitted</h1>
			<p>Your registration request has been received.</p>
			<p class="sub">Access will be available after admin approval.</p>
			<p class="sub">You will be notified once approved.</p>

			<div class="actions">
				<a href="/">
					<Button variant="secondary">Go to Home</Button>
				</a>
			</div>
		</div>
	</Card>
</div>

<style>
	.pending-page {
		min-height: calc(100vh - 200px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.pending-page :global(.card) {
		width: 100%;
		max-width: 400px;
	}

	.pending-content {
		text-align: center;
	}

	.icon {
		font-size: 4rem;
		margin-bottom: var(--spacing-md);
	}

	h1 {
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: var(--spacing-sm);
	}

	p {
		color: var(--color-text-muted);
		margin-bottom: var(--spacing-xs);
	}

	.sub {
		font-size: 0.875rem;
	}

	.actions {
		margin-top: var(--spacing-lg);
	}
</style>
