import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Split Three.js into separate chunk (~600KB gzipped)
          three: ['three'],
          // React Three Fiber ecosystem
          'react-three': [
            '@react-three/fiber',
            '@react-three/drei',
          ],
          // React core
          react: ['react', 'react-dom'],
          // UI framework
          dockview: ['dockview'],
        },
      },
    },
    // Enable chunk size warnings
    chunkSizeWarningLimit: 500,
  },
})
