/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'chat-bg': '#f7f9fc',
        'chat-user': '#007bff',
        'chat-bot': '#6c757d',
        'chat-user-text': '#ffffff',
        'chat-bot-text': '#ffffff',
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'typing': 'typing 1.5s steps(3, end) infinite',
      },
      keyframes: {
        typing: {
          '0%': { content: '"."' },
          '33%': { content: '".."' },
          '66%': { content: '"..."' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}