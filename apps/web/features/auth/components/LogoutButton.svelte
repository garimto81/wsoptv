<script lang="ts">
  /**
   * LogoutButton Component
   *
   * 로그아웃 버튼 컴포넌트
   * @see ../AGENT_RULES.md
   */

  import { Button } from '$shared/ui';
  import { useAuth } from '../hooks/useAuth';

  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    onLogout?: () => void;
  }

  let { variant = 'ghost', size = 'md', onLogout }: Props = $props();

  const auth = useAuth();

  let isLoggingOut = $state(false);

  async function handleLogout() {
    isLoggingOut = true;

    try {
      await auth.logout();
      onLogout?.();
    } finally {
      isLoggingOut = false;
    }
  }
</script>

<Button {variant} {size} loading={isLoggingOut} onclick={handleLogout}>
  로그아웃
</Button>
