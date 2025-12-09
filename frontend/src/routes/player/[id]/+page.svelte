<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Card, Spinner } from '$lib/components/ui';

	interface Hand {
		id: number;
		contentId: number;
		handNumber: number | null;
		startSec: number;
		grade: 'S' | 'A' | 'B' | 'C';
		isWinner: boolean;
		content?: {
			id: number;
			title: string;
			thumbnailUrl: string | null;
		};
	}

	interface Player {
		id: number;
		name: string;
		displayName: string;
		country: string | null;
		avatarUrl: string | null;
		totalHands: number;
		totalWins: number;
		hands: Hand[];
	}

	let player = $state<Player | null>(null);
	let isLoading = $state(true);
	let error = $state('');

	const playerId = $derived($page.params.id);

	onMount(async () => {
		try {
			player = await api.get<Player>(`/players/${playerId}`);
		} catch (err: any) {
			error = err.message || '플레이어 정보를 불러오는데 실패했습니다';
		} finally {
			isLoading = false;
		}
	});

	const winRate = $derived(
		player && player.totalHands > 0
			? ((player.totalWins / player.totalHands) * 100).toFixed(1)
			: '0'
	);

	const gradeColors: Record<string, string> = {
		S: '#f5c518',
		A: '#46d369',
		B: '#4db8ff',
		C: '#888'
	};
</script>

<svelte:head>
	<title>{player?.displayName || '플레이어'} - WSOPTV</title>
</svelte:head>

<div class="player-page container">
	{#if isLoading}
		<div class="loading">
			<Spinner size="lg" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if player}
		<header class="player-header">
			<div class="player-avatar">
				{#if player.avatarUrl}
					<img src={player.avatarUrl} alt={player.displayName} />
				{:else}
					<div class="avatar-placeholder">
						{player.displayName.charAt(0).toUpperCase()}
					</div>
				{/if}
			</div>
			<div class="player-info">
				<h1>{player.displayName}</h1>
				{#if player.country}
					<span class="country">{player.country}</span>
				{/if}
			</div>
		</header>

		<section class="stats-section">
			<div class="stats-grid">
				<Card padding="md">
					<div class="stat">
						<span class="stat-value">{player.totalHands.toLocaleString()}</span>
						<span class="stat-label">총 핸드</span>
					</div>
				</Card>
				<Card padding="md">
					<div class="stat">
						<span class="stat-value">{player.totalWins.toLocaleString()}</span>
						<span class="stat-label">승리</span>
					</div>
				</Card>
				<Card padding="md">
					<div class="stat">
						<span class="stat-value">{winRate}%</span>
						<span class="stat-label">승률</span>
					</div>
				</Card>
			</div>
		</section>

		<section class="hands-section">
			<h2>참여 핸드</h2>

			{#if player.hands.length === 0}
				<p class="empty">참여한 핸드가 없습니다.</p>
			{:else}
				<div class="hands-grid">
					{#each player.hands as hand}
						<a href="/watch/{hand.contentId}?t={hand.startSec}" class="hand-card">
							<Card variant="clickable" padding="sm">
								<div class="hand-layout">
									<div class="hand-thumbnail">
										{#if hand.content?.thumbnailUrl}
											<img src={hand.content.thumbnailUrl} alt="" />
										{:else}
											<div class="thumb-placeholder"></div>
										{/if}
									</div>
									<div class="hand-info">
										<div class="hand-header">
											<span class="grade" style="color: {gradeColors[hand.grade]}">{hand.grade}</span>
											<span class="hand-number">#{hand.handNumber || hand.id}</span>
											{#if hand.isWinner}
												<span class="winner-badge">승리</span>
											{/if}
										</div>
										{#if hand.content}
											<p class="content-title">{hand.content.title}</p>
										{/if}
									</div>
								</div>
							</Card>
						</a>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>

<style>
	.player-page {
		padding: var(--spacing-xl) var(--spacing-md);
	}

	.loading {
		display: flex;
		justify-content: center;
		padding: var(--spacing-xl);
	}

	.error {
		padding: var(--spacing-md);
		background: rgba(229, 9, 20, 0.1);
		border: 1px solid var(--color-error);
		border-radius: var(--radius-md);
		color: var(--color-error);
	}

	.player-header {
		display: flex;
		align-items: center;
		gap: var(--spacing-lg);
		margin-bottom: var(--spacing-xl);
	}

	.player-avatar {
		width: 120px;
		height: 120px;
		border-radius: 50%;
		overflow: hidden;
		flex-shrink: 0;
	}

	.player-avatar img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.avatar-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--color-surface);
		font-size: 3rem;
		font-weight: 700;
		color: var(--color-text-muted);
	}

	.player-info h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: var(--spacing-xs);
	}

	.country {
		color: var(--color-text-muted);
	}

	.stats-section {
		margin-bottom: var(--spacing-xl);
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--spacing-md);
	}

	.stat {
		text-align: center;
	}

	.stat-value {
		display: block;
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.stat-label {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.hands-section h2 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: var(--spacing-lg);
	}

	.empty {
		color: var(--color-text-muted);
		text-align: center;
		padding: var(--spacing-xl);
	}

	.hands-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--spacing-md);
	}

	.hand-card {
		text-decoration: none;
	}

	.hand-layout {
		display: flex;
		gap: var(--spacing-sm);
	}

	.hand-thumbnail {
		width: 100px;
		aspect-ratio: 16 / 9;
		border-radius: var(--radius-sm);
		overflow: hidden;
		flex-shrink: 0;
	}

	.hand-thumbnail img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.thumb-placeholder {
		width: 100%;
		height: 100%;
		background: var(--color-surface-hover);
	}

	.hand-info {
		min-width: 0;
	}

	.hand-header {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-xs);
	}

	.grade {
		font-weight: 700;
		font-size: 1rem;
	}

	.hand-number {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	.winner-badge {
		padding: 0.125rem 0.375rem;
		background: var(--color-success);
		color: black;
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 600;
	}

	.content-title {
		font-size: 0.875rem;
		color: var(--color-text-muted);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	@media (max-width: 768px) {
		.player-header {
			flex-direction: column;
			text-align: center;
		}

		.stats-grid {
			grid-template-columns: 1fr;
		}

		.hands-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
