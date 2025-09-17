/**
 * Configuración de PostCSS para Cafeteria IA
 * Compatible con ES Modules + Vite + TailwindCSS + Windows
 */

export default {
  plugins: {
    // TailwindCSS - Framework de utilidades CSS
    tailwindcss: {},
    
    // Autoprefixer - Añade prefijos de navegador automáticamente
    autoprefixer: {},
    
    // CSSnano para minificar en producción (opcional)
    ...(process.env.NODE_ENV === 'production' ? {
      cssnano: {
        preset: 'default',
      }
    } : {})
  },
}