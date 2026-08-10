import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',   // Bind to all interfaces (IPv4 + IPv6) so localhost works in browser
    proxy: (() => {
      const backendUrl = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const wsBackendUrl = backendUrl.replace(/^http/, 'ws');
      return {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/health': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/docs': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/openapi.json': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/stream': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/ws': {
          target: wsBackendUrl,
          ws: true,
        },
      };
    })(),
  },
  build: {
    rollupOptions: {
      maxParallelFileOps: 2,
      output: {
        onlyExplicitManualChunks: true,
        manualChunks(id) {
          const moduleId = id.replaceAll('\\', '/');
          if (moduleId.includes('/node_modules/three/')) return 'three';
          if (moduleId.includes('/node_modules/@react-three/')) return 'react-three';
          if (moduleId.includes('/node_modules/framer-motion/')) return 'framer-motion';
          if (moduleId.includes('/node_modules/zustand/')) return 'zustand';
          if (moduleId.includes('/node_modules/dockview/')) return 'dockview';
          if (moduleId.includes('/node_modules/@ag-grid-community/')) return 'ag-grid';
          return undefined;
        },
      },
    },
    // Enable chunk size warnings
    chunkSizeWarningLimit: 500,
  },
})
