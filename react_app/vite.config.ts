import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',   // Bind to all interfaces (IPv4 + IPv6) so localhost works in browser
  },
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
          // AG Grid — only needed by /editor and /import routes
          'ag-grid': [
            '@ag-grid-community/core',
            '@ag-grid-community/react',
            '@ag-grid-community/client-side-row-model',
          ],
          // Animation library
          'framer-motion': ['framer-motion'],
        },
      },
    },
    // Enable chunk size warnings
    chunkSizeWarningLimit: 500,
  },
})
