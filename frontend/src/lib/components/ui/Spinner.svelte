<script lang="ts">
	interface Props {
		size?: 'sm' | 'md' | 'lg';
	}

	let { size = 'md' }: Props = $props();
</script>

<div class="spinner {size}" role="status" aria-label="로딩 중">
	<span class="sr-only">로딩 중...</span>
</div>

<style>
	.spinner {
		border: 3px solid var(--color-border);
		border-top-color: var(--color-primary);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	.sm {
		width: 1rem;
		height: 1rem;
		border-width: 2px;
	}

	.md {
		width: 2rem;
		height: 2rem;
	}

	.lg {
		width: 3rem;
		height: 3rem;
		border-width: 4px;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		border: 0;
	}
</style>
