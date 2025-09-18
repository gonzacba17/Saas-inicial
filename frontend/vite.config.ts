import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Configuración CSS - usar archivo PostCSS externo
  css: {
    postcss: './postcss.config.cjs',
    devSourcemap: true,
  },
  
  // Configuración del servidor de desarrollo
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    open: false,
    cors: true,
    hmr: {
      overlay: true
    }
  },
  
  // Configuración para resolver módulos
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@types': path.resolve(__dirname, './src/types'),
      '@assets': path.resolve(__dirname, './src/assets'),
    }
  },
  
  // Optimización de dependencias
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'zustand'
    ],
    esbuildOptions: {
      target: 'es2020',
      loader: {
        '.js': 'jsx',
        '.ts': 'tsx',
      }
    },
  },
  
  // Configuración de build para producción
  build: {
    target: 'es2020',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom'],
          router: ['react-router-dom'],
          store: ['zustand']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
  },
  
  // Configuración específica de esbuild
  esbuild: {
    target: 'es2020',
    jsx: 'automatic',
    jsxDev: false,
  },
  
  // Variables de entorno
  envPrefix: 'VITE_',
  
  // Configuración de testing con Vitest
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: [
        'node_modules/',
        'src/tests/',
        'dist/',
        '**/*.d.ts',
        '**/*.config.*'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  
  // Configuración para compatibilidad con Windows
  define: {
    global: 'globalThis',
  }
})