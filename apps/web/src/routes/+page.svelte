<script lang="ts">
  // WSOPTV 메인 페이지
</script>

<svelte:head>
  <title>WSOPTV - 포커 VOD 스트리밍</title>
</svelte:head>

<main class="container">
  <h1>WSOPTV</h1>
  <p>18TB+ 포커 방송 아카이브 기반 VOD 스트리밍 플랫폼</p>

  <div class="features">
    <div class="feature-card">
      <h2>🔍 검색</h2>
      <p>플레이어, 대회, 핸드를 검색하세요</p>
    </div>
    <div class="feature-card">
      <h2>🎬 스트리밍</h2>
      <p>고화질 HLS 스트리밍으로 시청하세요</p>
    </div>
    <div class="feature-card">
      <h2>🃏 핸드 스킵</h2>
      <p>하이라이트 핸드만 골라서 시청하세요</p>
    </div>
  </div>
</main>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
  }

  h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    color: var(--color-primary, #3b82f6);
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 3rem;
  }

  .feature-card {
    padding: 2rem;
    border-radius: 12px;
    background: var(--color-bg-card, #f8fafc);
    border: 1px solid var(--color-border, #e2e8f0);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }

  .feature-card h2 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }
</style>
