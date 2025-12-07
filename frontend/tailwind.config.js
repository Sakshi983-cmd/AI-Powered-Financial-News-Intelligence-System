/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'finance-dark': '#0a0a0f',
        'accent-green': '#00d4aa',
      }
    },
  },
  plugins: [],
  darkMode: 'class',  // Dark theme default
};
