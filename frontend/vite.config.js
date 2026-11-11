import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: true, // 监听 0.0.0.0，允许局域网内其他设备访问（页面内的 /api、/ai 由本机代理转发）
    proxy: {
      // SpringBoot 主后端
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      // Python AI 微服务
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
