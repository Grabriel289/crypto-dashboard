/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk color palette
        'cyber': {
          bg: {
            primary: '#0a0a0f',
            secondary: '#12121a',
            card: '#1a1a2e',
            hover: '#242438'
          },
          accent: {
            green: '#00ff88',
            'green-dim': '#00cc6a',
            red: '#ff4444',
            'red-dim': '#cc3333',
            yellow: '#ffaa00',
            orange: '#ff6b35',
            cyan: '#00d4ff',
            purple: '#9d4edd'
          },
          text: {
            primary: '#ffffff',
            secondary: '#888888',
            muted: '#555555'
          },
          border: {
            subtle: '#2a2a3e',
            accent: '#3a3a5e'
          }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-in': 'slideIn 0.5s ease-out'
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00ff88, 0 0 10px #00ff88' },
          '100%': { boxShadow: '0 0 20px #00ff88, 0 0 30px #00ff88' }
        },
        slideIn: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    }
  },
  plugins: []
}
