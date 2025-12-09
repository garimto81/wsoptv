<script lang="ts">
  /**
   * RegisterForm Component
   *
   * 회원가입 폼 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Button, Input } from '$shared/ui';
  import { useAuth } from '../hooks/useAuth';
  import type { RegisterRequest } from '../types';

  interface Props {
    onSuccess?: () => void;
    onLoginClick?: () => void;
  }

  let { onSuccess, onLoginClick }: Props = $props();

  const auth = useAuth();

  // Form State
  let username = $state('');
  let password = $state('');
  let passwordConfirm = $state('');
  let displayName = $state('');

  // Validation Errors
  let errors = $state<Record<string, string>>({});

  function validate(): boolean {
    const newErrors: Record<string, string> = {};

    // 아이디 검증
    if (!username.trim()) {
      newErrors.username = '아이디를 입력해주세요';
    } else if (username.length < 4) {
      newErrors.username = '아이디는 4자 이상이어야 합니다';
    } else if (username.length > 50) {
      newErrors.username = '아이디는 50자 이하여야 합니다';
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      newErrors.username = '영문, 숫자, 밑줄만 사용 가능합니다';
    }

    // 비밀번호 검증
    if (!password) {
      newErrors.password = '비밀번호를 입력해주세요';
    } else if (password.length < 8) {
      newErrors.password = '비밀번호는 8자 이상이어야 합니다';
    } else if (!/[A-Z]/.test(password)) {
      newErrors.password = '대문자를 포함해야 합니다';
    } else if (!/[a-z]/.test(password)) {
      newErrors.password = '소문자를 포함해야 합니다';
    } else if (!/[0-9]/.test(password)) {
      newErrors.password = '숫자를 포함해야 합니다';
    }

    // 비밀번호 확인
    if (!passwordConfirm) {
      newErrors.passwordConfirm = '비밀번호를 다시 입력해주세요';
    } else if (password !== passwordConfirm) {
      newErrors.passwordConfirm = '비밀번호가 일치하지 않습니다';
    }

    // 표시 이름 (선택)
    if (displayName && displayName.length < 2) {
      newErrors.displayName = '표시 이름은 2자 이상이어야 합니다';
    }

    errors = newErrors;
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();

    if (!validate()) return;

    const request: RegisterRequest = {
      username: username.trim(),
      password,
      displayName: displayName.trim() || undefined
    };

    try {
      await auth.register(request);
      onSuccess?.();
    } catch {
      // 에러는 store에서 관리
    }
  }
</script>

<form class="register-form" onsubmit={handleSubmit}>
  <h2 class="title">회원가입</h2>

  <p class="notice">
    가입 후 관리자 승인이 필요합니다.
  </p>

  {#if auth.error}
    <div class="error-banner" role="alert">
      {auth.error.message}
    </div>
  {/if}

  <div class="form-fields">
    <Input
      name="username"
      label="아이디"
      placeholder="영문, 숫자, 밑줄 (4-50자)"
      bind:value={username}
      error={errors.username}
      autocomplete="username"
      disabled={auth.isLoading}
      required
    />

    <Input
      type="password"
      name="password"
      label="비밀번호"
      placeholder="대소문자, 숫자 포함 (8자 이상)"
      bind:value={password}
      error={errors.password}
      autocomplete="new-password"
      disabled={auth.isLoading}
      required
    />

    <Input
      type="password"
      name="passwordConfirm"
      label="비밀번호 확인"
      placeholder="비밀번호를 다시 입력하세요"
      bind:value={passwordConfirm}
      error={errors.passwordConfirm}
      autocomplete="new-password"
      disabled={auth.isLoading}
      required
    />

    <Input
      name="displayName"
      label="표시 이름 (선택)"
      placeholder="다른 사용자에게 표시될 이름"
      bind:value={displayName}
      error={errors.displayName}
      autocomplete="name"
      disabled={auth.isLoading}
    />
  </div>

  <div class="form-actions">
    <Button type="submit" loading={auth.isLoading}>
      가입하기
    </Button>
  </div>

  {#if onLoginClick}
    <p class="login-link">
      이미 계정이 있으신가요?
      <button type="button" class="link-button" onclick={onLoginClick}>
        로그인
      </button>
    </p>
  {/if}
</form>

<style>
  .register-form {
    max-width: 400px;
    margin: 0 auto;
    padding: var(--spacing-xl, 2rem);
  }

  .title {
    font-size: 1.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: var(--spacing-sm, 0.5rem);
  }

  .notice {
    text-align: center;
    font-size: 14px;
    color: var(--color-text-muted, #64748b);
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

  .form-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
  }

  .form-actions :global(button) {
    width: 100%;
  }

  .login-link {
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
