import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    host: true,
    port: 5173,
    // API проксируем на backend в dev, чтобы избегать CORS и ходить на /api.
    // Локально (pnpm run dev) — localhost; в docker-compose переопределяется на http://backend:8000.
    proxy: {
      "/api": {
        target: process.env.PUBLIC_API_URL || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
