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
      // en dev, /produits/* → backend
      '/produits': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      // login admin → backend
      '/login': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      '/send-email': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
})
