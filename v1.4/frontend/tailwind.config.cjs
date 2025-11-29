/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#e94560',
        secondary: '#f39c12',
        dark: '#1a1a2e',
      }
    },
  },
  plugins: [],
}
