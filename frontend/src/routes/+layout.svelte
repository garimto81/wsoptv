<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { Header, Footer } from '$lib/components/layout';
	import { authStore } from '$lib/stores';
	import type { LayoutData } from './$types';

	interface Props {
		children: Snippet;
		data: LayoutData;
	}

	let { children, data }: Props = $props();

	// Sync auth data from +layout.ts load function to authStore
	// This runs before children render, ensuring auth state is available
	$effect(() => {
		authStore.setUser(data.user);
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
