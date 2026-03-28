/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        surface: '#111111',
        'neon-green': '#00FF88',
        'neon-cyan': '#00FFA3',
        'neon-red': '#FF4B4B',
      },
    },
  },
  plugins: [],
}
