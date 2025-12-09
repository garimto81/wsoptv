<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Hls from 'hls.js';

	interface Props {
		src: string;
		poster?: string;
		autoplay?: boolean;
		startTime?: number;
		onTimeUpdate?: (currentTime: number) => void;
		onEnded?: () => void;
	}

	let {
		src,
		poster,
		autoplay = false,
		startTime = 0,
		onTimeUpdate,
		onEnded
	}: Props = $props();

	let videoElement: HTMLVideoElement;
	let hls: Hls | null = null;
	let isPlaying = $state(false);
	let currentTime = $state(0);
	let duration = $state(0);
	let volume = $state(1);
	let isMuted = $state(false);
	let isFullscreen = $state(false);
	let showControls = $state(true);
	let controlsTimeout: ReturnType<typeof setTimeout>;

	onMount(() => {
		if (Hls.isSupported()) {
			hls = new Hls({
				enableWorker: true,
				lowLatencyMode: true
			});
			hls.loadSource(src);
			hls.attachMedia(videoElement);
			hls.on(Hls.Events.MANIFEST_PARSED, () => {
				if (autoplay) {
					videoElement.play();
				}
				if (startTime > 0) {
					videoElement.currentTime = startTime;
				}
			});
		} else if (videoElement.canPlayType('application/vnd.apple.mpegurl')) {
			// Native HLS support (Safari)
			videoElement.src = src;
			if (startTime > 0) {
				videoElement.currentTime = startTime;
			}
		}

		// Keyboard shortcuts
		document.addEventListener('keydown', handleKeydown);

		return () => {
			document.removeEventListener('keydown', handleKeydown);
		};
	});

	onDestroy(() => {
		if (hls) {
			hls.destroy();
		}
	});

	function handleKeydown(e: KeyboardEvent) {
		if (e.target instanceof HTMLInputElement) return;

		switch (e.key) {
			case ' ':
			case 'k':
				e.preventDefault();
				togglePlay();
				break;
			case 'ArrowLeft':
				e.preventDefault();
				seek(-10);
				break;
			case 'ArrowRight':
				e.preventDefault();
				seek(10);
				break;
			case 'ArrowUp':
				e.preventDefault();
				changeVolume(0.1);
				break;
			case 'ArrowDown':
				e.preventDefault();
				changeVolume(-0.1);
				break;
			case 'm':
				e.preventDefault();
				toggleMute();
				break;
			case 'f':
				e.preventDefault();
				toggleFullscreen();
				break;
		}
	}

	function togglePlay() {
		if (videoElement.paused) {
			videoElement.play();
		} else {
			videoElement.pause();
		}
	}

	function seek(seconds: number) {
		videoElement.currentTime = Math.max(0, Math.min(duration, currentTime + seconds));
	}

	function seekTo(time: number) {
		videoElement.currentTime = time;
	}

	function changeVolume(delta: number) {
		volume = Math.max(0, Math.min(1, volume + delta));
		videoElement.volume = volume;
		if (volume > 0) {
			isMuted = false;
			videoElement.muted = false;
		}
	}

	function toggleMute() {
		isMuted = !isMuted;
		videoElement.muted = isMuted;
	}

	function toggleFullscreen() {
		if (!document.fullscreenElement) {
			videoElement.parentElement?.requestFullscreen();
			isFullscreen = true;
		} else {
			document.exitFullscreen();
			isFullscreen = false;
		}
	}

	function handleTimeUpdate() {
		currentTime = videoElement.currentTime;
		onTimeUpdate?.(currentTime);
	}

	function handleLoadedMetadata() {
		duration = videoElement.duration;
	}

	function handlePlay() {
		isPlaying = true;
	}

	function handlePause() {
		isPlaying = false;
	}

	function handleEnded() {
		isPlaying = false;
		onEnded?.();
	}

	function handleMouseMove() {
		showControls = true;
		clearTimeout(controlsTimeout);
		controlsTimeout = setTimeout(() => {
			if (isPlaying) {
				showControls = false;
			}
		}, 3000);
	}

	function handleProgressClick(e: MouseEvent) {
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const percent = (e.clientX - rect.left) / rect.width;
		seekTo(percent * duration);
	}

	function formatTime(seconds: number): string {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = Math.floor(seconds % 60);
		if (h > 0) {
			return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
		}
		return `${m}:${s.toString().padStart(2, '0')}`;
	}

	// Export methods for parent component
	export function getCurrentTime() {
		return currentTime;
	}

	export function seekToTime(time: number) {
		seekTo(time);
	}
</script>

<div
	class="video-player"
	class:fullscreen={isFullscreen}
	onmousemove={handleMouseMove}
	onmouseleave={() => isPlaying && (showControls = false)}
>
	<video
		bind:this={videoElement}
		class="video"
		{poster}
		playsinline
		ontimeupdate={handleTimeUpdate}
		onloadedmetadata={handleLoadedMetadata}
		onplay={handlePlay}
		onpause={handlePause}
		onended={handleEnded}
		onclick={togglePlay}
	>
		<track kind="captions" />
	</video>

	<div class="controls" class:visible={showControls}>
		<div class="progress-bar" onclick={handleProgressClick}>
			<div class="progress-bg"></div>
			<div class="progress-fill" style="width: {(currentTime / duration) * 100}%"></div>
		</div>

		<div class="controls-row">
			<div class="controls-left">
				<button class="control-btn" onclick={togglePlay} aria-label={isPlaying ? '일시정지' : '재생'}>
					{#if isPlaying}
						<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
							<rect x="6" y="4" width="4" height="16" />
							<rect x="14" y="4" width="4" height="16" />
						</svg>
					{:else}
						<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
							<polygon points="5,3 19,12 5,21" />
						</svg>
					{/if}
				</button>

				<button class="control-btn" onclick={() => seek(-10)} aria-label="10초 뒤로">
					<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
						<path d="M12.5 3C17.15 3 21.08 6.03 22.47 10.22L20.1 11C19.05 7.81 16.04 5.5 12.5 5.5C10.54 5.5 8.77 6.22 7.38 7.38L10 10H3V3L5.6 5.6C7.45 4 9.85 3 12.5 3M10 12L7.12 14.88C7.04 14.96 7 15.06 7 15.18C7 15.42 7.2 15.62 7.44 15.62H10V12M10 18V16.62H7.44C6.03 16.62 4.88 15.47 4.88 14.06C4.88 13.56 5.03 13.09 5.29 12.69L3.87 11.27C3.33 11.95 3 12.8 3 13.75C3 15.71 4.54 17.34 6.44 17.62V18H10Z" />
					</svg>
				</button>

				<button class="control-btn" onclick={() => seek(10)} aria-label="10초 앞으로">
					<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
						<path d="M11.5 3C6.85 3 2.92 6.03 1.53 10.22L3.9 11C4.95 7.81 7.96 5.5 11.5 5.5C13.46 5.5 15.23 6.22 16.62 7.38L14 10H21V3L18.4 5.6C16.55 4 14.15 3 11.5 3M14 12L16.88 14.88C16.96 14.96 17 15.06 17 15.18C17 15.42 16.8 15.62 16.56 15.62H14V12M14 18V16.62H16.56C17.97 16.62 19.12 15.47 19.12 14.06C19.12 13.56 18.97 13.09 18.71 12.69L20.13 11.27C20.67 11.95 21 12.8 21 13.75C21 15.71 19.46 17.34 17.56 17.62V18H14Z" />
					</svg>
				</button>

				<div class="volume-control">
					<button class="control-btn" onclick={toggleMute} aria-label={isMuted ? '음소거 해제' : '음소거'}>
						{#if isMuted || volume === 0}
							<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
								<path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" />
							</svg>
						{:else}
							<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
								<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
							</svg>
						{/if}
					</button>
					<input
						type="range"
						class="volume-slider"
						min="0"
						max="1"
						step="0.1"
						bind:value={volume}
						oninput={() => {
							videoElement.volume = volume;
							isMuted = volume === 0;
						}}
					/>
				</div>

				<span class="time">
					{formatTime(currentTime)} / {formatTime(duration)}
				</span>
			</div>

			<div class="controls-right">
				<button class="control-btn" onclick={toggleFullscreen} aria-label={isFullscreen ? '전체화면 종료' : '전체화면'}>
					{#if isFullscreen}
						<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
							<path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z" />
						</svg>
					{:else}
						<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
							<path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z" />
						</svg>
					{/if}
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	.video-player {
		position: relative;
		width: 100%;
		background: black;
		aspect-ratio: 16 / 9;
	}

	.video-player.fullscreen {
		aspect-ratio: auto;
	}

	.video {
		width: 100%;
		height: 100%;
		cursor: pointer;
	}

	.controls {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		padding: var(--spacing-sm);
		background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
		opacity: 0;
		transition: opacity 0.3s ease;
	}

	.controls.visible {
		opacity: 1;
	}

	.progress-bar {
		position: relative;
		height: 4px;
		cursor: pointer;
		margin-bottom: var(--spacing-sm);
	}

	.progress-bg {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 100%;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 2px;
	}

	.progress-fill {
		position: absolute;
		top: 0;
		left: 0;
		height: 100%;
		background: var(--color-primary);
		border-radius: 2px;
	}

	.controls-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.controls-left,
	.controls-right {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.control-btn {
		background: none;
		border: none;
		color: white;
		padding: var(--spacing-xs);
		cursor: pointer;
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.control-btn:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.volume-control {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
	}

	.volume-slider {
		width: 60px;
		height: 4px;
		-webkit-appearance: none;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 2px;
	}

	.volume-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 12px;
		height: 12px;
		background: white;
		border-radius: 50%;
		cursor: pointer;
	}

	.time {
		font-size: 0.75rem;
		color: white;
	}

	@media (max-width: 768px) {
		.volume-control {
			display: none;
		}
	}
</style>
