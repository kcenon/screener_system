import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png', 'robots.txt'],
      manifest: false, // Use external manifest.json
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\..*\/v1\/stocks/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'stocks-api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 300, // 5 minutes
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /^https:\/\/api\..*\/v1\/prices/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'prices-api-cache',
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60, // 1 minute
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /^https:\/\/api\..*\/v1\/market/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'market-api-cache',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 20,
                maxAgeSeconds: 120, // 2 minutes
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'images-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
              },
            },
          },
          {
            urlPattern: /\.(?:woff|woff2|ttf|eot)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'fonts-cache',
              expiration: {
                maxEntries: 20,
                maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
              },
            },
          },
        ],
      },
      devOptions: {
        enabled: true,
        type: 'module',
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Target chunk size warning threshold (in KB)
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        // Split chunks for better caching and loading performance
        manualChunks: {
          // Core React libraries - rarely change
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Data fetching and state management
          'vendor-query': ['@tanstack/react-query', 'zustand', 'axios'],
          // Chart libraries - large, only needed on specific pages
          'vendor-charts': ['lightweight-charts', 'recharts'],
          // UI component libraries
          'vendor-ui': [
            '@radix-ui/react-dialog',
            '@radix-ui/react-select',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-tooltip',
            '@radix-ui/react-tabs',
            '@radix-ui/react-accordion',
          ],
          // Internationalization
          'vendor-i18n': ['i18next', 'react-i18next', 'i18next-browser-languagedetector'],
          // Utilities
          'vendor-utils': ['date-fns', 'clsx', 'tailwind-merge', 'class-variance-authority'],
        },
      },
    },
  },
})
