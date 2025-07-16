import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import * as sass from 'sass'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    open: true
  },
  css: {
    preprocessorOptions: {
      scss: {
        implementation: sass,
        silenceDeprecations: ["legacy-js-api"],
      }
    }
  }
}) 