<script lang="ts">
  interface Props {
    type?: 'text' | 'email' | 'password' | 'search' | 'number';
    name: string;
    value?: string;
    placeholder?: string;
    label?: string;
    error?: string;
    disabled?: boolean;
    required?: boolean;
    autocomplete?: AutoFill;
    onchange?: (value: string) => void;
    oninput?: (value: string) => void;
  }

  let {
    type = 'text',
    name,
    value = $bindable(''),
    placeholder = '',
    label,
    error,
    disabled = false,
    required = false,
    autocomplete,
    onchange,
    oninput
  }: Props = $props();

  function handleInput(e: Event) {
    const target = e.target as HTMLInputElement;
    value = target.value;
    oninput?.(target.value);
  }

  function handleChange(e: Event) {
    const target = e.target as HTMLInputElement;
    onchange?.(target.value);
  }
</script>

<div class="input-wrapper" class:has-error={!!error}>
  {#if label}
    <label for={name} class="label">
      {label}
      {#if required}
        <span class="required" aria-hidden="true">*</span>
      {/if}
    </label>
  {/if}

  <input
    {type}
    {name}
    id={name}
    {value}
    {placeholder}
    {disabled}
    {required}
    {autocomplete}
    class="input"
    aria-invalid={!!error}
    aria-describedby={error ? `${name}-error` : undefined}
    oninput={handleInput}
    onchange={handleChange}
  />

  {#if error}
    <p id="{name}-error" class="error" role="alert">
      {error}
    </p>
  {/if}
</div>

<style>
  .input-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .label {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text, #1e293b);
  }

  .required {
    color: var(--color-error, #ef4444);
    margin-left: 2px;
  }

  .input {
    height: 40px;
    padding: 0 12px;
    font-size: 15px;
    border: 1px solid var(--color-border, #e2e8f0);
    border-radius: var(--radius-md, 8px);
    background: var(--color-bg, #ffffff);
    color: var(--color-text, #1e293b);
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .input:focus {
    outline: none;
    border-color: var(--color-primary, #3b82f6);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .input:disabled {
    background: var(--color-bg-card, #f8fafc);
    cursor: not-allowed;
  }

  .input::placeholder {
    color: var(--color-text-muted, #64748b);
  }

  .has-error .input {
    border-color: var(--color-error, #ef4444);
  }

  .has-error .input:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .error {
    font-size: 13px;
    color: var(--color-error, #ef4444);
    margin-top: 0.25rem;
  }
</style>
