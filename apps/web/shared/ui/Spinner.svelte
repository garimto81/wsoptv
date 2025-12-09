<script lang="ts">
  interface Props {
    size?: 'sm' | 'md' | 'lg';
    label?: string;
  }

  let { size = 'md', label = '로딩 중...' }: Props = $props();
</script>

<div class="spinner-container" role="status" aria-label={label}>
  <div class="spinner spinner-{size}"></div>
  <span class="visually-hidden">{label}</span>
</div>

<style>
  .spinner-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .spinner {
    border: 3px solid var(--color-border, #e2e8f0);
    border-top-color: var(--color-primary, #3b82f6);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner-sm {
    width: 16px;
    height: 16px;
    border-width: 2px;
  }

  .spinner-md {
    width: 24px;
    height: 24px;
  }

  .spinner-lg {
    width: 40px;
    height: 40px;
    border-width: 4px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
</style>
