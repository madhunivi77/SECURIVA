import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/salesforce': 'http://localhost:8000',
      '/callback': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/mcp': 'http://localhost:8000',
    },
  },
})
