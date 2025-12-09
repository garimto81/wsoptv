<script lang="ts">
  /**
   * SearchBar Component
   *
   * 검색 입력 바 컴포넌트 (자동완성 포함)
   * @see ../AGENT_RULES.md
   */

  import { useAutocomplete, getSuggestionIcon } from '../hooks/useSearch';
  import type { Suggestion } from '../types';

  interface Props {
    placeholder?: string;
    onSearch?: (query: string) => void;
  }

  let { placeholder = '검색어를 입력하세요', onSearch }: Props = $props();

  const autocomplete = useAutocomplete();

  let inputRef: HTMLInputElement | null = null;
  let selectedIndex = $state(-1);

  function handleInput(e: Event) {
    const target = e.target as HTMLInputElement;
    autocomplete.handleInput(target.value);
    selectedIndex = -1;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!autocomplete.isOpen) {
      if (e.key === 'Enter') {
        handleSubmit();
      }
      return;
    }

    const suggestions = autocomplete.suggestions;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
        break;
      case 'ArrowUp':
        e.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          autocomplete.selectSuggestion(suggestions[selectedIndex]);
        } else {
          handleSubmit();
        }
        break;
      case 'Escape':
        autocomplete.close();
        selectedIndex = -1;
        break;
    }
  }

  function handleSubmit() {
    if (autocomplete.inputValue.trim()) {
      onSearch?.(autocomplete.inputValue.trim());
      autocomplete.close();
    }
  }

  function handleSuggestionClick(suggestion: Suggestion) {
    autocomplete.selectSuggestion(suggestion);
    onSearch?.(suggestion.text);
  }

  function handleBlur() {
    // 약간의 지연을 두어 클릭 이벤트가 먼저 처리되도록
    setTimeout(() => {
      autocomplete.close();
      selectedIndex = -1;
    }, 150);
  }
</script>

<div class="search-bar">
  <div class="input-wrapper">
    <span class="search-icon" aria-hidden="true">🔍</span>

    <input
      bind:this={inputRef}
      type="search"
      class="search-input"
      {placeholder}
      value={autocomplete.inputValue}
      oninput={handleInput}
      onkeydown={handleKeydown}
      onblur={handleBlur}
      aria-label="검색"
      aria-expanded={autocomplete.isOpen}
      aria-autocomplete="list"
      aria-controls="search-suggestions"
      role="combobox"
    />

    {#if autocomplete.isLoading}
      <span class="loading-indicator" aria-hidden="true"></span>
    {/if}
  </div>

  {#if autocomplete.isOpen}
    <ul
      id="search-suggestions"
      class="suggestions"
      role="listbox"
    >
      {#each autocomplete.suggestions as suggestion, index (suggestion.text + suggestion.type)}
        <li
          class="suggestion-item"
          class:selected={index === selectedIndex}
          role="option"
          aria-selected={index === selectedIndex}
          onclick={() => handleSuggestionClick(suggestion)}
        >
          <span class="suggestion-icon">{getSuggestionIcon(suggestion.type)}</span>
          <span class="suggestion-text">{@html suggestion.highlight}</span>
          <span class="suggestion-type">{suggestion.type}</span>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .search-bar {
    position: relative;
    width: 100%;
    max-width: 600px;
  }

  .input-wrapper {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
    padding: 0 var(--spacing-md, 1rem);
    background: var(--color-bg-card, #f8fafc);
    border: 1px solid var(--color-border, #e2e8f0);
    border-radius: var(--radius-lg, 12px);
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .input-wrapper:focus-within {
    border-color: var(--color-primary, #3b82f6);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .search-icon {
    font-size: 16px;
    opacity: 0.5;
  }

  .search-input {
    flex: 1;
    height: 44px;
    border: none;
    background: transparent;
    font-size: 15px;
    color: var(--color-text, #1e293b);
  }

  .search-input:focus {
    outline: none;
  }

  .search-input::placeholder {
    color: var(--color-text-muted, #64748b);
  }

  /* Remove default search input styling */
  .search-input::-webkit-search-cancel-button {
    display: none;
  }

  .loading-indicator {
    width: 16px;
    height: 16px;
    border: 2px solid var(--color-border, #e2e8f0);
    border-top-color: var(--color-primary, #3b82f6);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .suggestions {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    margin: 0;
    padding: var(--spacing-sm, 0.5rem) 0;
    list-style: none;
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e2e8f0);
    border-radius: var(--radius-md, 8px);
    box-shadow: var(--shadow-lg, 0 10px 15px rgba(0, 0, 0, 0.1));
    z-index: 100;
    max-height: 300px;
    overflow-y: auto;
  }

  .suggestion-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm, 0.5rem);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    cursor: pointer;
    transition: background 0.1s;
  }

  .suggestion-item:hover,
  .suggestion-item.selected {
    background: var(--color-bg-hover, #f1f5f9);
  }

  .suggestion-icon {
    font-size: 14px;
  }

  .suggestion-text {
    flex: 1;
    font-size: 14px;
  }

  .suggestion-text :global(mark) {
    background: rgba(59, 130, 246, 0.2);
    color: var(--color-primary, #3b82f6);
    border-radius: 2px;
  }

  .suggestion-type {
    font-size: 11px;
    color: var(--color-text-muted, #64748b);
    text-transform: uppercase;
  }
</style>
