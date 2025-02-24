import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import reactRefresh from '@vitejs/plugin-react-refresh'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), reactRefresh()],
  test: {
    globals: true,
    environment: 'jsdom',
  },
  build: {
    outDir: 'dist',
  },
  server: {
    port: 3000,
  },
  // Añadir configuración específica para variables de entorno
  envDir: './',
  envPrefix: 'VITE_',
  define: {
    'process.env': process.env
  }
})