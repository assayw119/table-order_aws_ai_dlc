import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite 설정: React 플러그인 + Vitest(jsdom) 설정
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
  },
})
