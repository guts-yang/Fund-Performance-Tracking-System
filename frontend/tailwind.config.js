/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
        },
        sci: {
          base: '#050810',      // Deep midnight blue
          surface: '#0a0f1a',
          midnight: '#030508',
          cyan: '#00d4ff',      // Neon cyan (enhanced)
          gold: '#ffd700',      // Luxury gold (enhanced)
          danger: '#ef4444',
          success: '#22c55e',
          'cyan-dim': 'rgba(0, 212, 255, 0.1)',
          'gold-dim': 'rgba(255, 215, 0, 0.1)',
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Consolas', 'Monaco', 'monospace'],
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        tech: ['"Orbitron"', 'sans-serif'],           // Futuristic headers
        modern: ['"Rajdhani"', 'sans-serif'],        // Clean modern labels
        data: ['"JetBrains Mono"', 'monospace'],      // Monospace for data
      },
      backgroundImage: {
        'cyber-grid': `
          linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px)
        `,
        'cyber-grid-glow': `
          linear-gradient(rgba(0, 212, 255, 0.1) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, 0.1) 1px, transparent 1px)
        `,
        'radial-glow': 'radial-gradient(circle at center, rgba(0, 212, 255, 0.05) 0%, transparent 70%)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 212, 255, 0.5), 0 0 40px rgba(0, 212, 255, 0.3)',
        'glow-cyan-sm': '0 0 10px rgba(0, 212, 255, 0.6)',
        'glow-gold': '0 0 20px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.3)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.4)',
        'glow-success': '0 0 20px rgba(34, 197, 94, 0.4)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.5)',
        'glass-enhanced': '0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 0 20px rgba(0, 212, 255, 0.15)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'scanline': 'scanline 8s linear infinite',
        'float': 'float 3s ease-in-out infinite',
        'border-glow': 'borderGlow 4s ease-in-out infinite',
        'inner-glow': 'innerGlow 8s linear infinite',
        'status-pulse': 'statusPulse 2s ease-out infinite',
      },
      keyframes: {
        glowPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        borderGlow: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1' },
        },
        innerGlow: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        statusPulse: {
          '0%': { transform: 'scale(0.8)', opacity: '1' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
      },
      borderWidth: {
        '1.5': '1.5px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
