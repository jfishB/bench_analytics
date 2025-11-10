/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#233e8c",
        "primary-foreground": "#ffffff",
        "muted-foreground": "#6b7280",
      },
    },
  },
  plugins: [],
};