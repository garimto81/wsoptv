<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';

	interface Props extends HTMLInputAttributes {
		label?: string;
		error?: string;
	}

	let {
		label,
		error,
		id,
		type = 'text',
		...restProps
	}: Props = $props();

	const inputId = id || `input-${Math.random().toString(36).slice(2)}`;
</script>

<div class="input-wrapper" class:has-error={!!error}>
	{#if label}
		<label for={inputId} class="label">{label}</label>
	{/if}

	<input
		{id}
		{type}
		class="input"
		aria-invalid={!!error}
		aria-describedby={error ? `${inputId}-error` : undefined}
		{...restProps}
	/>

	{#if error}
		<span id="{inputId}-error" class="error">{error}</span>
	{/if}
</div>

<style>
	.input-wrapper {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text);
	}

	.input {
		padding: 0.75rem 1rem;
		font-size: 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		color: var(--color-text);
		transition: border-color 0.2s ease;
	}

	.input:focus {
		outline: none;
		border-color: var(--color-primary);
	}

	.input::placeholder {
		color: var(--color-text-muted);
	}

	.has-error .input {
		border-color: var(--color-error);
	}

	.error {
		font-size: 0.75rem;
		color: var(--color-error);
	}
</style>
