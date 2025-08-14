/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        telegram: {
          bg: 'var(--tg-theme-bg-color)',
          text: 'var(--tg-theme-text-color)',
          hint: 'var(--tg-theme-hint-color)',
          link: 'var(--tg-theme-link-color)',
          button: 'var(--tg-theme-button-color)',
          'button-text': 'var(--tg-theme-button-text-color)',
          secondary: 'var(--tg-theme-secondary-bg-color)',
        }
      },
      animation: {
        'shake': 'shake 0.5s ease-in-out 3',
        'glow': 'glow 1s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-10px) rotate(-5deg)' },
          '75%': { transform: 'translateX(10px) rotate(5deg)' },
        },
        glow: {
          '0%, 100%': { 
            filter: 'drop-shadow(0 0 5px rgba(255, 215, 0, 0.5))',
            transform: 'scale(1)',
          },
          '50%': { 
            filter: 'drop-shadow(0 0 20px rgba(255, 215, 0, 0.8))',
            transform: 'scale(1.05)',
          },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}