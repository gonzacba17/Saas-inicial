/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'cafe': {
          50: '#fdf7ed',
          100: '#f5e8d5',
          200: '#eacfaa',
          300: '#deb175',
          400: '#d19043',
          500: '#c97f2e',
          600: '#b86625',
          700: '#974e21',
          800: '#7b3f21',
          900: '#65351e',
        },
        'cream': {
          50: '#fffcf5',
          100: '#fef7e6',
          200: '#fdebc8',
          300: '#fbd89e',
          400: '#f8c471',
          500: '#f5ad51',
          600: '#e9923d',
          700: '#c17333',
          800: '#9a5c30',
          900: '#7d4c2a',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
        'serif': ['Georgia', 'ui-serif'],
        'mono': ['Fira Code', 'ui-monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}