import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  base: '/flashcards/',
  plugins: [react(), basicSsl()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/flashcards/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/flashcards\/api/, '/api'),
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 80,
    https: true,
    proxy: {
      '/flashcards/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/flashcards\/api/, '/api'),
      },
      '/flashcards/docs': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/flashcards/redoc': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/flashcards/openapi.json': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
