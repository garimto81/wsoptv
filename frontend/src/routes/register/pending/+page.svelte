<script lang="ts">
	import { Card, Button } from '$lib/components/ui';
</script>

<svelte:head>
	<title>가입 대기 중 - WSOPTV</title>
</svelte:head>

<div class="pending-page">
	<Card padding="lg">
		<div class="pending-content">
			<div class="icon">⏳</div>
			<h1>가입 신청 완료</h1>
			<p>회원가입 신청이 접수되었습니다.</p>
			<p class="sub">관리자 승인 후 서비스 이용이 가능합니다.</p>
			<p class="sub">승인 완료 시 알림을 보내드립니다.</p>

			<div class="actions">
				<a href="/">
					<Button variant="secondary">홈으로</Button>
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
