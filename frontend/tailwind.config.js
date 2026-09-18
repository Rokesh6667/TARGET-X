/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pitch: {
          dark: '#0a0d14',
          card: '#121824',
          border: '#1e293b',
          grass: '#1a472a',
          line: '#3a7d44',
          accent: '#00f2fe',
          neon: '#10b981',
        },
      },
    },
  },
  plugins: [],
}
