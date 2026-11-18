/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Deep obsidian requested palette: background #080A0F, cards #11141D, borders #1F2433
        obsidian: {
          bg: '#080A0F',
          card: '#11141D',
          border: '#1F2433',
          950: '#080A0F',
          900: '#11141D',
          850: '#161A26',
          800: '#1F2433',
          700: '#2A3144',
          600: '#3A445D',
        },
        cyber: {
          950: '#080A0F',
          900: '#11141D',
          850: '#161A26',
          800: '#1F2433',
          700: '#2A3144',
          600: '#3A445D',
        },
        // Alerts crimson #EF4444, Safe emerald #10B981
        crimson: {
          DEFAULT: '#EF4444',
          500: '#EF4444',
          600: '#DC2626',
          950: '#450A0A',
        },
        emerald: {
          DEFAULT: '#10B981',
          500: '#10B981',
          600: '#059669',
          950: '#064E3B',
        },
        tactical: {
          cyan: '#00F0FF',
          emerald: '#10B981',
          crimson: '#EF4444',
          amber: '#F59E0B',
          ice: '#E0F7FA',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Fira Code', 'Menlo', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      boxShadow: {
        'tactical-cyan': '0 0 25px -4px rgba(0, 240, 255, 0.22)',
        'tactical-crimson': '0 0 30px -4px rgba(239, 68, 68, 0.35)',
        'tactical-emerald': '0 0 25px -4px rgba(16, 185, 129, 0.22)',
        'tactical-amber': '0 0 25px -4px rgba(245, 158, 11, 0.25)',
      },
    },
  },
  plugins: [],
};
