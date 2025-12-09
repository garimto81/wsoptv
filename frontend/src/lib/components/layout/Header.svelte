<script lang="ts">
	import { authStore } from '$lib/stores';
	import Button from '../ui/Button.svelte';

	let searchQuery = $state('');

	function handleSearch(e: Event) {
		e.preventDefault();
		if (searchQuery.trim()) {
			window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`;
		}
	}

	async function handleLogout() {
		await authStore.logout();
		window.location.href = '/login';
	}
</script>

<header class="header">
	<div class="header-content">
		<a href="/" class="logo">
			<span class="logo-text">WSOPTV</span>
		</a>

		<nav class="nav">
			<a href="/" class="nav-link">Home</a>
			<a href="/browse" class="nav-link">Browse</a>
			<a href="/jellyfin" class="nav-link">Jellyfin</a>
			<a href="/search" class="nav-link">Search</a>
		</nav>

		<form class="search-form" onsubmit={handleSearch}>
			<input
				type="search"
				class="search-input"
				placeholder="Search..."
				bind:value={searchQuery}
			/>
		</form>

		<div class="user-menu">
			{#if authStore.isAuthenticated}
				<a href="/history" class="nav-link">History</a>
				{#if authStore.isAdmin}
					<a href="/admin" class="nav-link">Admin</a>
				{/if}
				<button class="user-button" onclick={handleLogout}>
					{authStore.user?.displayName || authStore.user?.username}
				</button>
			{:else}
				<a href="/login">
					<Button variant="primary" size="sm">Sign In</Button>
				</a>
			{/if}
		</div>
	</div>
</header>

<style>
	.header {
		position: sticky;
		top: 0;
		z-index: 100;
		background: rgba(15, 15, 15, 0.95);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid var(--color-border);
	}

	.header-content {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 var(--spacing-md);
		height: 64px;
		display: flex;
		align-items: center;
		gap: var(--spacing-lg);
	}

	.logo {
		text-decoration: none;
	}

	.logo-text {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.nav {
		display: flex;
		gap: var(--spacing-md);
	}

	.nav-link {
		color: var(--color-text-muted);
		text-decoration: none;
		font-weight: 500;
		transition: color 0.2s ease;
	}

	.nav-link:hover {
		color: var(--color-text);
	}

	.search-form {
		flex: 1;
		max-width: 400px;
	}

	.search-input {
		width: 100%;
		padding: 0.5rem 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		font-size: 0.875rem;
	}

	.search-input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.user-menu {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
	}

	.user-button {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 0.5rem 1rem;
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.875rem;
	}

	.user-button:hover {
		background: var(--color-surface-hover);
	}

	@media (max-width: 768px) {
		.nav {
			display: none;
		}

		.search-form {
			display: none;
		}
	}
</style>
