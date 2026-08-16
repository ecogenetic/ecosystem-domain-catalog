import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5175,
    strictPort: true,
    proxy: {
      '/catalog': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/data': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/v1': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/docs': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    },
  },
});
