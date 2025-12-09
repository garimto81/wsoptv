import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [sveltekit()],
  resolve: {
    alias: {
      $features: '/features',
      $shared: '/shared'
    }
  },
  test: {
    include: ['features/**/*.{test,spec}.ts', 'shared/**/*.{test,spec}.ts'],
    globals: true,
    environment: 'jsdom'
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
});
