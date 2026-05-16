import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['4a0e9dbf.r16.cpolar.top', '.cpolar.top', 'dd4e0a.r11.vip.cpolar.cn', '.cpolar.cn', 'localhost', '127.0.0.1'],
    proxy: {
      '/api': {
        target: 'http://localhost:6789', 
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:6789',
        changeOrigin: true
      }
    }
  },
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true
      }
    }
  }
})
