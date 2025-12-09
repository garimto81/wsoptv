<script lang="ts">
	interface Hand {
		id: number;
		handNumber: number | null;
		startSec: number;
		endSec: number;
		winner: string | null;
		potSizeBb: number | null;
		isAllIn: boolean;
		isShowdown: boolean;
		grade: 'S' | 'A' | 'B' | 'C';
	}

	interface Props {
		hands: Hand[];
		currentTime: number;
		duration: number;
		onSeek: (time: number) => void;
	}

	let { hands, currentTime, duration, onSeek }: Props = $props();

	const currentHand = $derived(
		hands.find((h) => currentTime >= h.startSec && currentTime < h.endSec)
	);

	const currentHandIndex = $derived(
		currentHand ? hands.indexOf(currentHand) : -1
	);

	function goToHand(hand: Hand) {
		onSeek(hand.startSec);
	}

	function previousHand() {
		if (currentHandIndex > 0) {
			goToHand(hands[currentHandIndex - 1]);
		}
	}

	function nextHand() {
		if (currentHandIndex < hands.length - 1) {
			goToHand(hands[currentHandIndex + 1]);
		} else if (currentHandIndex === -1 && hands.length > 0) {
			// Find next hand after current time
			const next = hands.find((h) => h.startSec > currentTime);
			if (next) goToHand(next);
		}
	}

	function formatTime(seconds: number): string {
		const m = Math.floor(seconds / 60);
		const s = Math.floor(seconds % 60);
		return `${m}:${s.toString().padStart(2, '0')}`;
	}

	const gradeColors: Record<string, string> = {
		S: '#f5c518',
		A: '#46d369',
		B: '#4db8ff',
		C: '#888'
	};
</script>

<div class="hand-timeline">
	<div class="timeline-header">
		<h3>핸드 타임라인</h3>
		<div class="nav-buttons">
			<button
				class="nav-btn"
				onclick={previousHand}
				disabled={currentHandIndex <= 0}
				aria-label="이전 핸드"
			>
				← 이전
			</button>
			<span class="hand-counter">
				{#if currentHand}
					{currentHandIndex + 1} / {hands.length}
				{:else}
					- / {hands.length}
				{/if}
			</span>
			<button
				class="nav-btn"
				onclick={nextHand}
				disabled={currentHandIndex >= hands.length - 1}
				aria-label="다음 핸드"
			>
				다음 →
			</button>
		</div>
	</div>

	<div class="timeline-bar">
		{#each hands as hand}
			<button
				class="hand-marker"
				class:active={hand === currentHand}
				style="left: {(hand.startSec / duration) * 100}%; width: {((hand.endSec - hand.startSec) / duration) * 100}%; background-color: {gradeColors[hand.grade]}"
				onclick={() => goToHand(hand)}
				title="핸드 #{hand.handNumber || hand.id} ({hand.grade})"
			>
			</button>
		{/each}
		<div
			class="current-position"
			style="left: {(currentTime / duration) * 100}%"
		></div>
	</div>

	{#if currentHand}
		<div class="current-hand-info">
			<div class="hand-badge" style="background-color: {gradeColors[currentHand.grade]}">
				{currentHand.grade}
			</div>
			<div class="hand-details">
				<strong>핸드 #{currentHand.handNumber || currentHand.id}</strong>
				<span class="hand-meta">
					{formatTime(currentHand.startSec)} - {formatTime(currentHand.endSec)}
					{#if currentHand.potSizeBb}
						| Pot: {currentHand.potSizeBb}BB
					{/if}
					{#if currentHand.isAllIn}
						| <span class="tag all-in">All-In</span>
					{/if}
					{#if currentHand.isShowdown}
						| <span class="tag showdown">Showdown</span>
					{/if}
				</span>
				{#if currentHand.winner}
					<span class="winner">승자: {currentHand.winner}</span>
				{/if}
			</div>
		</div>
	{/if}

	<div class="hand-list">
		{#each hands as hand, index}
			<button
				class="hand-item"
				class:active={hand === currentHand}
				onclick={() => goToHand(hand)}
			>
				<span class="hand-grade" style="color: {gradeColors[hand.grade]}">
					{hand.grade}
				</span>
				<span class="hand-number">#{hand.handNumber || index + 1}</span>
				<span class="hand-time">{formatTime(hand.startSec)}</span>
				{#if hand.isAllIn}
					<span class="mini-tag">AI</span>
				{/if}
			</button>
		{/each}
	</div>
</div>

<style>
	.hand-timeline {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--spacing-md);
	}

	.timeline-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--spacing-md);
	}

	.timeline-header h3 {
		font-size: 1rem;
		font-weight: 600;
	}

	.nav-buttons {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.nav-btn {
		background: var(--color-surface-hover);
		border: none;
		border-radius: var(--radius-sm);
		padding: 0.25rem 0.5rem;
		color: var(--color-text);
		cursor: pointer;
		font-size: 0.75rem;
	}

	.nav-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.nav-btn:hover:not(:disabled) {
		background: var(--color-border);
	}

	.hand-counter {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.timeline-bar {
		position: relative;
		height: 20px;
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		margin-bottom: var(--spacing-md);
	}

	.hand-marker {
		position: absolute;
		top: 2px;
		height: 16px;
		min-width: 4px;
		border: none;
		border-radius: 2px;
		cursor: pointer;
		opacity: 0.6;
		transition: opacity 0.2s ease;
	}

	.hand-marker:hover,
	.hand-marker.active {
		opacity: 1;
	}

	.current-position {
		position: absolute;
		top: 0;
		width: 2px;
		height: 100%;
		background: white;
		pointer-events: none;
	}

	.current-hand-info {
		display: flex;
		align-items: flex-start;
		gap: var(--spacing-sm);
		padding: var(--spacing-sm);
		background: var(--color-bg);
		border-radius: var(--radius-sm);
		margin-bottom: var(--spacing-md);
	}

	.hand-badge {
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-sm);
		font-weight: 700;
		font-size: 0.875rem;
		color: black;
	}

	.hand-details {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
		font-size: 0.875rem;
	}

	.hand-meta {
		color: var(--color-text-muted);
		font-size: 0.75rem;
	}

	.winner {
		color: var(--color-success);
		font-size: 0.75rem;
	}

	.tag {
		padding: 0.125rem 0.375rem;
		border-radius: var(--radius-sm);
		font-size: 0.625rem;
		font-weight: 600;
	}

	.tag.all-in {
		background: var(--color-primary);
		color: white;
	}

	.tag.showdown {
		background: var(--color-warning);
		color: black;
	}

	.hand-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-xs);
		max-height: 150px;
		overflow-y: auto;
	}

	.hand-item {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-size: 0.75rem;
		color: var(--color-text);
	}

	.hand-item.active {
		border-color: var(--color-primary);
		background: rgba(229, 9, 20, 0.1);
	}

	.hand-item:hover {
		border-color: var(--color-text-muted);
	}

	.hand-grade {
		font-weight: 700;
	}

	.hand-number {
		color: var(--color-text-muted);
	}

	.hand-time {
		color: var(--color-text-muted);
	}

	.mini-tag {
		padding: 0.0625rem 0.25rem;
		background: var(--color-primary);
		color: white;
		border-radius: 2px;
		font-size: 0.625rem;
		font-weight: 700;
	}
</style>
