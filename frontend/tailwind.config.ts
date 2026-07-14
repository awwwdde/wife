import type { Config } from "tailwindcss";

// Палитра и типографика — DECISIONS §4 (направление Lisa Tran Brows).
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#F2EBE3", // фон
        graphite: "#2B2622", // текст/тёмный
        terracotta: "#B08968", // акцент (терракота/охра)
      },
      fontFamily: {
        // serif — заголовки, sans — текст, script — рукописный акцент.
        serif: ["Cormorant", "Playfair Display", "Georgia", "serif"],
        sans: ["Inter", "Manrope", "system-ui", "sans-serif"],
        script: ["'Playwrite'", "cursive"],
      },
    },
  },
  plugins: [],
} satisfies Config;
