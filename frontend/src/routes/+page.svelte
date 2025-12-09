<script lang="ts">
	// Home page - will show catalog grid
</script>

<svelte:head>
	<title>WSOPTV - 포커 VOD 스트리밍</title>
</svelte:head>

<main class="home">
	<section class="hero">
		<h1>WSOPTV</h1>
		<p>세계 최고의 포커 방송을 한 곳에서</p>
	</section>

	<section class="catalogs">
		<h2>카탈로그</h2>
		<p class="placeholder">카탈로그 로딩 중...</p>
	</section>
</main>

<style>
	.home {
		flex: 1;
		padding: var(--spacing-xl);
	}

	.hero {
		text-align: center;
		padding: var(--spacing-xl) 0;
		margin-bottom: var(--spacing-xl);
	}

	.hero h1 {
		font-size: 3rem;
		font-weight: 700;
		color: var(--color-primary);
		margin-bottom: var(--spacing-sm);
	}

	.hero p {
		font-size: 1.25rem;
		color: var(--color-text-muted);
	}

	.catalogs h2 {
		font-size: 1.5rem;
		margin-bottom: var(--spacing-md);
	}

	.placeholder {
		color: var(--color-text-muted);
	}
</style>
