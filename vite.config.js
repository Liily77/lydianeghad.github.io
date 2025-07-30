import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { 
      '@': path.resolve(__dirname, './src') 
    }
  },
  server: {
    proxy: {
      // Proxy toute l'API derrière /api/*
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')  // enlève le /api avant de forwarder
      },
      // Et si tu appelles directement /uploads en dev :
      '/uploads': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      }
    }
  }
})

