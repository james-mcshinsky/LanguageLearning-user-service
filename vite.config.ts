import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  root: 'src',
  plugins: [react()],
  server: {
    proxy: {
      // forward all /api requests to your FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
      '/login': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/signup': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../dist'
  }
});
