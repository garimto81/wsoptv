<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { Header, Footer } from '$lib/components/layout';
	import { authStore } from '$lib/stores';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();

	onMount(() => {
		authStore.init();
	});
</script>

<div class="app">
	<Header />
	<main class="main">
		{@render children()}
	</main>
	<Footer />
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.main {
		flex: 1;
	}
</style>
