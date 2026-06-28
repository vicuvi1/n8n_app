/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#0B0F19',
          raised: '#111827',
          card: '#151C2F',
          hover: '#1A2236',
          border: '#1F2937',
        },
        accent: {
          pink: '#FF6D5A',
          green: '#10B981',
          blue: '#3B82F6',
          purple: '#8B5CF6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        shimmer: 'shimmer 1.8s ease-in-out infinite',
        'spin-slow': 'spin 1.2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { opacity: 0.4 },
          '50%': { opacity: 1 },
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(255, 109, 90, 0.15)',
        'glow-green': '0 0 20px rgba(16, 185, 129, 0.2)',
      },
    },
  },
  plugins: [],
};
