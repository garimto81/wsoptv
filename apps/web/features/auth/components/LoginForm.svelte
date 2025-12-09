<script lang="ts">
  /**
   * LoginForm Component
   *
   * 로그인 폼 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Button, Input } from '$shared/ui';
  import { useAuth } from '../hooks/useAuth';
  import type { LoginRequest } from '../types';

  interface Props {
    onSuccess?: () => void;
    onRegisterClick?: () => void;
  }

  let { onSuccess, onRegisterClick }: Props = $props();

  const auth = useAuth();

  // Form State
  let username = $state('');
  let password = $state('');
  let rememberMe = $state(false);

  // Validation
  let usernameError = $state('');
  let passwordError = $state('');

  function validate(): boolean {
    let isValid = true;

    if (!username.trim()) {
      usernameError = '아이디를 입력해주세요';
      isValid = false;
    } else {
      usernameError = '';
    }

    if (!password) {
      passwordError = '비밀번호를 입력해주세요';
      isValid = false;
    } else {
      passwordError = '';
    }

    return isValid;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();

    if (!validate()) return;

    const request: LoginRequest = {
      username: username.trim(),
      password,
      rememberMe
    };

    try {
      await auth.login(request);
      onSuccess?.();
    } catch {
      // 에러는 store에서 관리
    }
  }
</script>

<form class="login-form" onsubmit={handleSubmit}>
  <h2 class="title">로그인</h2>

  {#if auth.error}
    <div class="error-banner" role="alert">
      {auth.error.message}
    </div>
  {/if}

  <div class="form-fields">
    <Input
      name="username"
      label="아이디"
      placeholder="아이디를 입력하세요"
      bind:value={username}
      error={usernameError}
      autocomplete="username"
      disabled={auth.isLoading}
      required
    />

    <Input
      type="password"
      name="password"
      label="비밀번호"
      placeholder="비밀번호를 입력하세요"
      bind:value={password}
      error={passwordError}
      autocomplete="current-password"
      disabled={auth.isLoading}
      required
    />

    <label class="remember-me">
      <input
        type="checkbox"
        bind:checked={rememberMe}
        disabled={auth.isLoading}
      />
      <span>로그인 상태 유지</span>
    </label>
  </div>

  <div class="form-actions">
    <Button type="submit" loading={auth.isLoading}>
      로그인
    </Button>
  </div>

  {#if onRegisterClick}
    <p class="register-link">
      계정이 없으신가요?
      <button type="button" class="link-button" onclick={onRegisterClick}>
        회원가입
      </button>
    </p>
  {/if}
</form>

<style>
  .login-form {
    max-width: 400px;
    margin: 0 auto;
    padding: var(--spacing-xl, 2rem);
  }

  .title {
    font-size: 1.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: var(--spacing-lg, 1.5rem);
  }

  .error-banner {
    padding: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-md, 1rem);
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--color-error, #ef4444);
    border-radius: var(--radius-md, 8px);
    color: var(--color-error, #ef4444);
    font-size: 14px;
  }

  .form-fields {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-lg, 1.5rem);
  }

  .remember-me {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 14px;
    cursor: pointer;
  }

  .remember-me input {
    width: 16px;
    height: 16px;
    cursor: pointer;
  }

  .form-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
  }

  .form-actions :global(button) {
    width: 100%;
  }

  .register-link {
    text-align: center;
    margin-top: var(--spacing-lg, 1.5rem);
    font-size: 14px;
    color: var(--color-text-muted, #64748b);
  }

  .link-button {
    background: none;
    border: none;
    color: var(--color-primary, #3b82f6);
    cursor: pointer;
    text-decoration: underline;
    font-size: inherit;
  }

  .link-button:hover {
    color: var(--color-primary-dark, #2563eb);
  }
</style>
